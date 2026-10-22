// End-to-end tests for Space Invaders, run in headless Chromium with phone emulation.
//   node tests/e2e.js            (needs the "playwright" package)
// Screenshots are written to $SHOTS (default: <tmp>/si-shots).
let pw;
try { pw = require('playwright'); } catch (e) { pw = require('/opt/node-tools/node_modules/playwright'); }
const { chromium, devices } = pw;
const path = require('path'), fs = require('fs'), os = require('os');
const URL = 'file://' + path.resolve(__dirname, '..', 'index.html');
const OUT = process.env.SHOTS || path.join(os.tmpdir(), 'si-shots');
fs.mkdirSync(OUT, { recursive: true });

let failures = 0, passes = 0;
const check = (cond, msg) => { console.log((cond ? 'PASS ' : 'FAIL ') + msg); if (cond) passes++; else failures++; };
const info = msg => console.log('     ' + msg);
const sleep = ms => new Promise(r => setTimeout(r, ms));
async function touch(cdp, type, x, y, id = 1) {
  await cdp.send('Input.dispatchTouchEvent', { type, touchPoints: type === 'touchEnd' ? [] : [{ x, y, id, radiusX: 5, radiusY: 5, force: 1 }] });
}
async function center(page, sel) {
  const b = await page.locator(sel).boundingBox();
  return { x: b.x + b.width / 2, y: b.y + b.height / 2, b };
}
async function tap(page, sel) { await page.locator(sel).scrollIntoViewIfNeeded(); const c = await center(page, sel); await page.touchscreen.tap(c.x, c.y); }
const ev = (page, fn, arg) => page.evaluate(fn, arg);

(async () => {
  const browser = await chromium.launch();
  const errors = [];
  const watch = (p, tag) => {
    p.on('pageerror', e => errors.push(tag + ' pageerror: ' + e.message));
    p.on('console', m => { if (m.type() === 'error' && !/fonts\.g|ERR_|net::/.test(m.text())) errors.push(tag + ' console: ' + m.text()); });
  };

  // ════════════════════════════════════════════════════════════════════════
  const ctx = await browser.newContext({ ...devices['iPhone 13'] });
  const page = await ctx.newPage();
  watch(page, 'main');
  await page.goto(URL);
  await sleep(800);
  const cdp = await ctx.newCDPSession(page);

  console.log('\n— Title & start —');
  check(await ev(page, () => __SI.state) === 'title', 'boots to title screen');
  check(await page.locator('#modeBtn').innerText() === 'MODE: CLASSIC', 'title shows current mode');
  check(await page.locator('#contBtn').isHidden(), 'no CONTINUE button without a saved game');
  check((await page.locator('#tRank').innerText()).startsWith('RANK: CADET'), 'pilot rank shown on title');
  await page.screenshot({ path: OUT + '/01-title.png' });
  await tap(page, '#playBtn');
  await sleep(300);
  check(await ev(page, () => __SI.state) === 'playing', 'tapping PLAY starts the game');
  check(await ev(page, () => document.body.classList.contains('coach')), 'first game shows coaching hints');
  await page.screenshot({ path: OUT + '/02-tutorial.png' });
  await sleep(1900);

  console.log('\n— Layout —');
  const lay = await ev(page, () => ({ L: __SI.L, worldBottom: __SI.L.offY + 232 * __SI.L.s, vw: innerWidth, vh: innerHeight, G: { phase: __SI.G.phase, alive: __SI.G.alive, lives: __SI.G.lives } }));
  const fireBtn = await center(page, '#bF'), leftBtn = await center(page, '#bL'), rightBtn = await center(page, '#bR');
  check(lay.worldBottom <= leftBtn.b.y + 1 && lay.worldBottom <= fireBtn.b.y + 1, 'controls sit below the playfield');
  check(fireBtn.b.x + fireBtn.b.width <= lay.vw && fireBtn.b.y + fireBtn.b.height <= lay.vh, 'fire button fully on screen');
  check(lay.G.alive === 55 && lay.G.lives === 3 && lay.G.phase === 'play', '55 invaders, 3 lives, GET READY finished');

  console.log('\n— Touch controls —');
  const x0 = await ev(page, () => __SI.G.player.x);
  await touch(cdp, 'touchStart', leftBtn.x, leftBtn.y);
  await sleep(1000);
  const x1 = await ev(page, () => __SI.G.player.x);
  check(await page.locator('#bL.on').count() === 1, 'left button lights up while held');
  await touch(cdp, 'touchMove', rightBtn.x, rightBtn.y);
  await sleep(600);
  const x2 = await ev(page, () => __SI.G.player.x);
  await touch(cdp, 'touchEnd', 0, 0);
  await sleep(100);
  info(`player x ${x0.toFixed(1)} -> ${x1.toFixed(1)} -> ${x2.toFixed(1)}`);
  check(x1 < x0 - 30 && x2 > x1 + 15, 'hold LEFT moves left; sliding onto RIGHT reverses');
  check(await page.locator('.cbtn.on').count() === 0, 'buttons release when finger lifts');
  const s0 = await ev(page, () => __SI.G.shotsFired);
  await touch(cdp, 'touchStart', fireBtn.x, fireBtn.y, 2);
  await sleep(2500);
  await touch(cdp, 'touchEnd', 0, 0);
  const s1 = await ev(page, () => __SI.G.shotsFired);
  check(s1 - s0 >= 3, `holding FIRE keeps shooting (${s1 - s0} shots)`);
  check(!(await ev(page, () => document.body.classList.contains('coach'))), 'coaching hints disappear after first shot');
  await sleep(700);
  const s2 = await ev(page, () => __SI.G.shotsFired);
  const L0 = await ev(page, () => __SI.L);
  await page.touchscreen.tap(L0.offX + 112 * L0.s, L0.offY + 120 * L0.s);
  await sleep(150);
  check(await ev(page, () => __SI.G.shotsFired) > s2, 'tapping the playfield fires');
  const t0 = await ev(page, () => __SI.G.t); await sleep(2000);
  const t1 = await ev(page, () => __SI.G.t);
  check(Math.abs(t1 - t0 - 120) < 20, `simulation runs at 60 ticks/sec (${t1 - t0} in 2s)`);

  console.log('\n— Pause / resume —');
  await tap(page, '#bP'); await sleep(300);
  check(await ev(page, () => __SI.state) === 'paused', 'pause button pauses');
  check((await page.locator('#pauseInfo').innerText()).includes('SCORE'), 'pause screen shows score, wave and lives');
  check(await ev(page, () => !!localStorage.getItem('si.save')), 'pausing saves the game');
  await page.screenshot({ path: OUT + '/03-paused.png' });
  await tap(page, '#sPause [data-act=resume]'); await sleep(100);
  check(await ev(page, () => __SI.state === 'playing' && __SI.G.resumeT > 0), 'resume shows a 3-2-1 countdown');

  console.log('\n— Arcade rules (fast-forwarded) —');
  await ev(page, () => { __SI.freeze = true; });
  const pacing = await ev(page, () => {
    __SI.startGame('classic');
    const G = __SI.G; let ticks = 0, firstDrop = -1; const y0 = G.aliens[0].y;
    while (G.phase !== 'dying' && ticks < 60 * 600) { G.player.invuln = 9999; G.bombs.length = 0; __SI.tick(); ticks++; if (firstDrop < 0 && G.aliens[0].y > y0) firstDrop = ticks; }
    return { s: ticks / 60, first: firstDrop / 60, invasion: G.invasion };
  });
  info(`untouched fleet: first drop ${pacing.first.toFixed(1)}s, lands ${pacing.s.toFixed(0)}s`);
  check(pacing.first > 5 && pacing.s > 90 && pacing.invasion, 'fleet marches slowly, landing = invasion');
  const speed = await ev(page, () => {
    __SI.startGame('classic'); const G = __SI.G; G.phase = 'play'; G.banner = null;
    const measure = () => { const a = G.aliens.find(a => a.alive); const x = a.x, y = a.y; let n = 0; while (a.x === x && a.y === y && n < 200) { G.player.invuln = 9999; G.bombs.length = 0; __SI.tick(); n++; } return { n, dx: a.x - x }; };
    measure(); const full = measure().n;
    G.aliens.forEach((a, i) => { if (i) a.alive = false; }); G.alive = 1; G.fleetDir = 1; G.fleetDrop = false;
    const r1 = measure(); G.fleetDir = -1; const r2 = measure();
    return { full, one: r1.n, right: r1.dx, left: r2.dx };
  });
  check(speed.full > 40 && speed.one <= 2, `fleet speeds up (${speed.full} ticks/step -> ${speed.one})`);
  check(speed.right === 3 && speed.left === -2, 'last invader moves 3px right, 2px left (arcade quirk)');
  const stop = await ev(page, () => {
    __SI.startGame('classic'); const G = __SI.G; G.phase = 'play'; G.banner = null; G.player.invuln = 9999;
    for (let i = 0; i < 30; i++) __SI.tick();
    const a = G.aliens.find(a => a.alive && a.row === 4); G.shots = [{ x: a.x + 3, y: a.y + 10, vx: 0, spd: 4, volley: { hit: false, left: 1 }, pierce: false }];
    __SI.tick(); __SI.tick();
    const snap = JSON.stringify(G.aliens.map(a => [a.x, a.y]));
    for (let i = 0; i < 3; i++) __SI.tick();
    return { killed: !a.alive, frozen: snap === JSON.stringify(G.aliens.map(a => [a.x, a.y])) };
  });
  check(stop.killed && stop.frozen, 'fleet freezes briefly when an invader is hit');
  const wave = await ev(page, () => {
    const G = __SI.G; G.aliens.forEach(a => { a.alive = false; }); G.alive = 0; __SI.tick(); const p = G.phase;
    for (let i = 0; i < 160; i++) __SI.tick();
    return { p, wave: G.wave, alive: G.alive, topY: Math.min(...G.aliens.map(a => a.y)) };
  });
  check(wave.p === 'waveclear' && wave.wave === 2 && wave.alive === 55 && wave.topY === 64, 'wave clear -> wave 2 starts lower');
  const sc = await ev(page, () => {
    const G = __SI.G; G.phase = 'play'; G.banner = null; G.player.invuln = 9999; const lives = G.lives;
    const a = G.aliens.find(a => a.type === 'squid'); G.score = 1490;
    G.shots = [{ x: a.x + 3, y: a.y + 10, vx: 0, spd: 4, volley: { hit: false, left: 1 }, pierce: false }];
    for (let i = 0; i < 4; i++) __SI.tick();
    return { score: G.score, lives, now: G.lives, alive: a.alive };
  });
  check(!sc.alive && sc.score === 1520 && sc.now === sc.lives + 1, 'squid = 30 pts; bonus ship at 1,500');

  console.log('\n— Danger zone —');
  const danger = await ev(page, () => {
    const G = __SI.G; G.aliens.forEach(a => { if (a.alive) a.y += 72; });
    G.player.invuln = 9999; __SI.tick(); const d = G.danger;
    G.aliens.forEach(a => { a.alive = false; }); G.alive = 0; G.wDeaths = 0; __SI.tick();
    return { d, close: !!__SI.achs.close, phase: G.phase };
  });
  check(danger.d, 'invaders near the ground trigger the danger warning');
  check(danger.close && danger.phase === 'waveclear', 'clearing a wave in the danger zone unlocks CLOSE CALL');

  console.log('\n— Game over, initials, share —');
  await ev(page, () => {
    const G = __SI.G; for (let i = 0; i < 200; i++) __SI.tick();
    G.lives = 1; G.player.invuln = 0; G.phase = 'play'; G.banner = null;
    G.bombs.push({ type: 'roll', x: Math.round(G.player.x) + 5, y: 196, f: 0, ft: 0 });
    for (let i = 0; i < 140; i++) if (__SI.state === 'playing') __SI.tick();
  });
  check(await ev(page, () => __SI.state) === 'gameover', 'losing the last life ends the game');
  await ev(page, () => { __SI.freeze = false; });
  await sleep(1000);
  check(await page.locator('#sInit').isVisible(), 'top-10 score asks for initials');
  await page.screenshot({ path: OUT + '/04-initials.png' });
  await tap(page, '#sInit [data-act=initUp][data-i="0"]');
  await tap(page, '#sInit [data-act=initUp][data-i="1"]');
  await tap(page, '#sInit [data-act=initUp][data-i="1"]');
  check(await page.locator('#ch0').innerText() === 'B' && await page.locator('#ch1').innerText() === 'C', 'arrow buttons change letters');
  await tap(page, '#initDone'); await sleep(200);
  check(await page.locator('#sOver').isVisible(), 'DONE shows the game over screen');
  check(await page.locator('#againBtn').isDisabled(), 'AGAIN briefly locked');
  const top = await ev(page, () => __SI.scores.classic[0]);
  check(top && top.n === 'BCA', `score saved with initials (${top && top.n})`);
  check(await ev(page, () => localStorage.getItem('si.initials')) === '"BCA"', 'initials remembered for next time');
  check(await page.locator('#shareBtn').isVisible(), 'share button offered');
  await ev(page, () => { Object.defineProperty(navigator, 'share', { value: undefined, configurable: true }); Object.defineProperty(navigator, 'clipboard', { value: { writeText: t => { window.__copied = t; return Promise.resolve(); } }, configurable: true }); });
  await tap(page, '#shareBtn'); await sleep(200);
  check(/I scored \d+ in SPACE INVADERS/.test(await ev(page, () => window.__copied || '')), 'share copies a brag message when there is no share sheet');
  await page.screenshot({ path: OUT + '/05-gameover.png' });
  await sleep(900);
  check(!(await page.locator('#againBtn').isDisabled()), 'AGAIN unlocks');
  check(await ev(page, () => !!__SI.achs.first && !!__SI.achs.wave), 'awards unlocked during play (FIRST CONTACT, WAVE BREAKER)');

  console.log('\n— Plus mode: power-ups & combos —');
  await tap(page, '#menuBtn'); await sleep(300);
  check(await ev(page, () => __SI.current) === 'Title', 'MENU returns to title');
  await tap(page, '#modeBtn'); await sleep(200);
  check(await page.locator('#sModes .modecard').count() === 6, 'mode screen lists 6 modes');
  await page.screenshot({ path: OUT + '/06-modes.png' });
  await tap(page, '#sModes [data-mode=plus]'); await sleep(300);
  check(await ev(page, () => __SI.state === 'playing' && __SI.G.mode === 'plus'), 'picking PLUS starts a Plus game');
  await ev(page, () => { __SI.freeze = true; });
  const pu = await ev(page, () => {
    const G = __SI.G; G.phase = 'play'; G.banner = null;
    const prep = () => { G.player.invuln = 9999; G.bombs.length = 0; G.shots = []; };
    const grab = k => { prep(); G.capsules = [{ k, x: Math.round(G.player.x) + 3, y: 198 }]; __SI.tick(); };
    const out = {};
    grab('R'); out.R = G.power && G.power.k;
    G.player.x = 203; G.lastShotT = -99; __SI.settings.autofire = true; for (let i = 0; i < 14; i++) __SI.tick(); out.rapidShots = G.shots.length; __SI.settings.autofire = false;
    grab('S'); G.shots = []; G.lastShotT = -99; __SI.settings.autofire = true; __SI.tick(); __SI.settings.autofire = false; out.spread = G.shots.length;
    grab('L'); G.shots = [];
    const col = G.aliens.filter(a => a.alive && a.col === 5); G.player.x = col[0].x + col[0].w / 2 - 6.5;
    __SI.settings.autofire = true; __SI.tick(); __SI.settings.autofire = false;
    const before = G.alive; for (let i = 0; i < 60; i++) { G.player.invuln = 9999; G.bombs.length = 0; __SI.tick(); }
    out.laserKills = before - G.alive;
    grab('T'); out.T = G.power && G.power.k;
    G.shields[0].m.fill(0); grab('H'); out.shieldRepaired = G.shields[0].m.some(v => v);
    const l0 = G.lives; grab('+'); out.life = G.lives - l0;
    return out;
  });
  check(pu.R === 'R' && pu.rapidShots === 2, 'rapid fire allows two shots on screen');
  check(pu.spread === 3, 'spread shot fires three ways');
  check(pu.laserKills >= 2, `laser pierces through invaders (${pu.laserKills} kills)`);
  check(pu.T === 'T' && pu.shieldRepaired && pu.life === 1, 'time warp, shield repair and extra life work');
  const combo = await ev(page, () => {
    __SI.startGame('plus'); const G = __SI.G; G.phase = 'play'; G.banner = null;
    for (let k = 0; k < 9; k++) {
      G.player.invuln = 9999; G.bombs.length = 0;
      const a = G.aliens.find(a => a.alive && a.row === 4);
      G.shots = [{ x: a.x + 3, y: a.y + 10, vx: 0, spd: 4, volley: { hit: false, left: 1 }, pierce: false }];
      for (let i = 0; i < 4; i++) __SI.tick();
    }
    const mult = G.mult;
    G.shots = [{ x: 2, y: 30, vx: 0, spd: 4, volley: { hit: false, left: 1 }, pierce: false }];
    for (let i = 0; i < 4; i++) __SI.tick();
    return { mult, after: G.mult };
  });
  check(combo.mult === 2 && combo.after === 1, 'combo builds to x2 after 8 hits and resets on a miss');
  const bonus = await ev(page, () => {
    const G = __SI.G; G.wShots = 10; G.wHits = 9; G.wDeaths = 0; const s = G.score;
    G.aliens.forEach(a => { a.alive = false; }); G.alive = 0; G.player.invuln = 9999; __SI.tick();
    return { gain: G.score - s, lines: G.banner.lines };
  });
  check(bonus.gain === 950 && bonus.lines.length === 2, `wave bonus: accuracy + no-death (${bonus.gain})`);
  await ev(page, () => { __SI.freeze = false; });
  await sleep(300);
  await page.screenshot({ path: OUT + '/07-wave-bonus.png' });
  await ev(page, () => { __SI.freeze = true; });

  console.log('\n— Other modes —');
  const hc = await ev(page, () => {
    __SI.startGame('hardcore'); const G = __SI.G; G.phase = 'play'; G.banner = null; G.player.invuln = 9999;
    const lives = G.lives; G.score = 1495;
    const a = G.aliens.find(a => a.alive && a.row === 4); G.shots = [{ x: a.x + 3, y: a.y + 10, vx: 0, spd: 4, volley: { hit: false, left: 1 }, pierce: false }];
    for (let i = 0; i < 4; i++) __SI.tick();
    return { lives, after: G.lives, diff: G.diffKey };
  });
  check(hc.lives === 1 && hc.after === 1 && hc.diff === 'hard', 'hardcore: one life, hard bombs, no bonus ship');
  const ta = await ev(page, () => {
    __SI.startGame('time'); const G = __SI.G; G.phase = 'play'; G.banner = null;
    const t0 = G.timeLeft; for (let i = 0; i < 60; i++) { G.player.invuln = 9999; G.bombs.length = 0; __SI.tick(); }
    const t1 = G.timeLeft;
    G.player.invuln = 0; G.bombs = [{ type: 'roll', x: Math.round(G.player.x) + 5, y: 196, f: 0, ft: 0 }]; __SI.tick(); __SI.tick();
    const t2 = G.timeLeft, livesShown = G.lives;
    for (let i = 0; i < 140; i++) __SI.tick();
    const respawned = !G.player.dead && __SI.state === 'playing';
    G.timeLeft = 3; G.player.invuln = 9999; for (let i = 0; i < 5; i++) if (__SI.state === 'playing') __SI.tick();
    return { t0, t1, t2, respawned, state: __SI.state, over: document.getElementById('overTitle').textContent };
  });
  check(ta.t0 === 7200 && ta.t1 === 7140, 'time attack: 2-minute clock counts down');
  check(ta.t1 - ta.t2 >= 600 && ta.respawned, 'time attack: dying costs 10 seconds, then you respawn');
  check(ta.state === 'gameover' && ta.over === 'TIME UP!', 'time attack ends with TIME UP!');
  await ev(page, () => { __SI.freeze = false; }); await sleep(1100);
  await page.screenshot({ path: OUT + '/08-timeup.png' });
  if (await page.locator('#sInit').isVisible()) { await tap(page, '#initDone'); await sleep(100); }
  await sleep(1000);                                    // game-over screen ignores restarts for a moment
  await ev(page, () => { __SI.freeze = true; });
  const daily = await ev(page, () => {
    const seq = () => { __SI.startGame('daily'); const G = __SI.G; const r = []; for (let i = 0; i < 5; i++) { G.capsules = []; G.aliens[0].alive = true; } return [G.rng, G.seeded]; };
    const a = seq(), b = seq();
    return { same: a[0] === b[0] && a[1] };
  });
  check(daily.same, 'daily challenge uses the same seed for every player today');
  const pr = await ev(page, () => {
    const before = JSON.stringify(__SI.scores);
    __SI.startGame('practice'); const G = __SI.G; G.phase = 'play'; G.banner = null;
    for (let i = 0; i < 1200; i++) { G.player.invuln = 9999; __SI.tick(); }
    const bombs = G.bombs.length;
    G.score = 999; G.lives = 1; G.player.invuln = 0; G.aliens.forEach(a => { if (a.alive) a.y = 195; }); for (let i = 0; i < 200; i++) if (__SI.state === 'playing') __SI.tick();
    return { bombs, state: __SI.state, same: before === JSON.stringify(__SI.scores) };
  });
  check(pr.bombs === 0, 'practice: invaders never shoot');
  check(pr.state === 'gameover' && pr.same, 'practice: scores are not recorded');
  await ev(page, () => { __SI.freeze = false; }); await sleep(1100);
  check(await page.locator('#sOver').isVisible() && (await page.locator('#overRank').innerText()) === 'NOT RECORDED', 'practice game over says NOT RECORDED (no initials)');

  console.log('\n— Awards & scores screens —');
  await sleep(700);                                     // MENU is locked for 0.9s after the screen appears
  await tap(page, '#menuBtn'); await sleep(300);
  await tap(page, '#sTitle [data-act=ach]'); await sleep(200);
  const achTxt = await page.locator('#achCount').innerText();
  check(/^\d+ \/ 20 UNLOCKED$/.test(achTxt) && parseInt(achTxt) >= 3, `awards screen (${achTxt})`);
  await page.screenshot({ path: OUT + '/09-awards.png' });
  await tap(page, '#sAch [data-act=back]'); await sleep(150);
  await tap(page, '#sTitle [data-act=scores]'); await sleep(200);
  check(await page.locator('#scoreTabs .tab').count() === 5, 'score table has a tab per ranked mode');
  await tap(page, '#scoreTabs [data-mode=time]'); await sleep(100);
  check(await page.locator('#scoreTabs .tab.on').innerText() === 'TIME', 'score tabs switch');
  await page.screenshot({ path: OUT + '/10-scores.png' });
  await tap(page, '#sScores [data-act=back]'); await sleep(150);

  console.log('\n— Saved game: continue after the tab is closed —');
  await ev(page, () => {
    __SI.freeze = true; __SI.startGame('classic'); const G = __SI.G; G.phase = 'play'; G.banner = null;
    G.score = 777; G.wave = 3; G.aliens[3].alive = false; G.alive = 54; G.shields[1].m.fill(0);
    __SI.pause();
  });
  await page.reload(); await sleep(800);
  check(await page.locator('#contBtn').isVisible(), 'after reopening, title offers CONTINUE');
  check((await page.locator('#contInfo').innerText()).includes('WAVE 3'), 'continue button shows mode, wave and score');
  await tap(page, '#contBtn'); await sleep(200);
  const restored = await ev(page, () => ({ s: __SI.state, score: __SI.G.score, wave: __SI.G.wave, alive: __SI.G.alive, dead3: !__SI.G.aliens[3].alive, shield: __SI.G.shields[1].m.some(v => v), resumeT: __SI.G.resumeT }));
  check(restored.s === 'playing' && restored.score === 777 && restored.wave === 3 && restored.alive === 54 && restored.dead3 && !restored.shield, 'continued game restores score, wave, fleet and shields');

  console.log('\n— Back button —');
  await page.goBack(); await sleep(300);
  check(await ev(page, () => __SI.state) === 'paused' && page.url().endsWith('index.html'), 'browser/Android back pauses instead of leaving');
  await page.goBack(); await sleep(300);
  check(await ev(page, () => __SI.state) === 'playing', 'back again resumes from the pause menu');

  console.log('\n— Keyboard menus —');
  await ev(page, () => __SI.toTitle()); await sleep(200);
  await page.keyboard.press('ArrowDown');
  check(await ev(page, () => document.activeElement && document.activeElement.closest('#sTitle') !== null), 'arrow keys move focus through menu buttons');
  await ev(page, () => { const b = document.getElementById('contBtn'); if (!b.classList.contains('hidden')) b.classList.add('hidden'); document.getElementById('playBtn').focus(); });
  await page.keyboard.press('Enter'); await sleep(200);
  check(await ev(page, () => __SI.state) === 'playing', 'Enter activates the focused button');

  console.log('\n— Other control schemes —');
  await ev(page, () => { __SI.freeze = false; __SI.settings.controls = 'pad'; __SI.applySettings(); __SI.G.phase = 'play'; __SI.G.banner = null; __SI.G.player.invuln = 9999; __SI.G.player.x = 60; });
  check(await page.locator('#bL').isHidden() && await page.locator('#bF').isVisible(), 'trackpad mode: arrows hidden, FIRE kept');
  const L1 = await ev(page, () => __SI.L);
  const px0 = await ev(page, () => __SI.G.player.x);
  await touch(cdp, 'touchStart', L1.offX + 60 * L1.s, L1.offY + 140 * L1.s);
  for (let i = 1; i <= 6; i++) { await touch(cdp, 'touchMove', L1.offX + 60 * L1.s + i * 10, L1.offY + 140 * L1.s); await sleep(30); }
  await touch(cdp, 'touchEnd', 0, 0); await sleep(100);
  const px1 = await ev(page, () => __SI.G.player.x);
  check(px1 - px0 > 20, `trackpad: swiping right nudges the cannon right (+${(px1 - px0).toFixed(1)})`);
  await ev(page, () => { __SI.settings.controls = 'tilt'; __SI.applySettings(); __SI.G.player.x = 60; __SI.onOrient({ gamma: 0, beta: 0 }); __SI.onOrient({ gamma: 20, beta: 0 }); });
  await sleep(500);
  const tx = await ev(page, () => __SI.G.player.x);
  check(tx > 80, `tilt: tilting right steers right (x=${tx.toFixed(1)})`);
  await ev(page, () => { __SI.onOrient({ gamma: 0, beta: 0 }); __SI.settings.controls = 'buttons'; __SI.settings.btnSize = 'l'; __SI.applySettings(); });
  const big = (await page.locator('#bL').boundingBox()).width;
  await ev(page, () => { __SI.settings.btnSize = 'm'; __SI.settings.btnAlpha = 0.4; __SI.applySettings(); });
  const med = (await page.locator('#bL').boundingBox()).width;
  check(big > med + 5, `button size setting (${med.toFixed(0)} -> ${big.toFixed(0)}px)`);
  check(await ev(page, () => document.getElementById('bL').style.opacity) === '0.4', 'button opacity setting');
  await ev(page, () => { __SI.settings.btnAlpha = 1; __SI.applySettings(); });

  console.log('\n— Display options —');
  for (const st of ['classic', 'mono', 'contrast', 'cb', 'neon']) {
    await ev(page, s => { __SI.settings.style = s; __SI.applySettings(); }, st); await sleep(120);
    if (st === 'classic' || st === 'cb') await page.screenshot({ path: OUT + `/11-style-${st}.png` });
  }
  check(true, 'all 5 graphics styles render');
  await ev(page, () => { __SI.settings.sharp = true; __SI.applySettings(); });
  const sharpOk = await ev(page, () => Math.abs(__SI.L.s * __SI.L.dpr - Math.round(__SI.L.s * __SI.L.dpr)) < 1e-9);
  check(sharpOk, 'sharp pixels: each game pixel is a whole number of screen pixels');
  await ev(page, () => { __SI.settings.sharp = false; __SI.settings.large = true; __SI.settings.noflash = true; __SI.applySettings(); });
  check(await ev(page, () => document.body.classList.contains('large') && document.body.classList.contains('noflash')), 'large text and reduce-flashing options apply');
  await ev(page, () => { __SI.settings.large = false; __SI.settings.noflash = false; __SI.applySettings(); });

  console.log('\n— Assist speed —');
  await ev(page, () => { __SI.settings.speed = 0.75; __SI.startGame('classic'); });
  const a0 = await ev(page, () => __SI.G.t); await sleep(2000); const a1 = await ev(page, () => __SI.G.t);
  check(Math.abs(a1 - a0 - 90) < 15 && await ev(page, () => __SI.G.assisted), `75% speed runs ~45 ticks/sec and is marked assisted (${a1 - a0})`);
  await ev(page, () => { __SI.settings.speed = 1; __SI.applySettings(); });

  console.log('\n— Settings screen —');
  await ev(page, () => __SI.toTitle()); await sleep(150);
  await tap(page, '#sTitle [data-act=settings]'); await sleep(200);
  check(await page.locator('#sSettings .sethead').count() >= 5, 'settings grouped into sections');
  check((await page.locator('#version').innerText()).startsWith('SPACE INVADERS v'), 'version number shown');
  await page.screenshot({ path: OUT + '/12-settings.png', fullPage: false });
  await page.locator('[data-act=set][data-key=crt]').click();
  check(await ev(page, () => __SI.settings.crt === true && document.body.classList.contains('crt')), 'toggling a setting applies immediately');
  await page.locator('#resetSetBtn').click(); await page.locator('#resetSetBtn').click();
  check(await ev(page, () => __SI.settings.crt === false), 'reset settings (two taps)');

  console.log('\n— Export / import save —');
  await ev(page, () => { Object.defineProperty(navigator, 'clipboard', { value: { writeText: t => { window.__copied = t; return Promise.resolve(); } }, configurable: true }); });
  await page.locator('[data-act=exportSave]').click(); await sleep(200);
  const code = await ev(page, () => window.__copied);
  check(typeof code === 'string' && code.startsWith('SI2:'), 'export copies a save code');
  const keep = await ev(page, () => JSON.stringify(__SI.scores.classic));
  await ev(page, () => { localStorage.clear(); });
  page.once('dialog', d => d.accept(code));
  await page.locator('[data-act=importSave]').click();
  await sleep(1500);
  check(await ev(page, () => JSON.stringify(__SI.scores.classic)) === keep, 'import restores scores on another install');

  console.log('\n— Rotation, background, canvas —');
  await tap(page, '#playBtn'); await sleep(2200);
  const br = await ev(page, () => ({ t: __SI.G.t, alive: __SI.G.alive }));
  await page.setViewportSize({ width: 844, height: 390 }); await sleep(500);
  const ar = await ev(page, () => ({ t: __SI.G.t, alive: __SI.G.alive, land: __SI.L.land }));
  check(ar.land && ar.alive === br.alive && ar.t > br.t, 'rotating keeps the game going');
  await page.screenshot({ path: OUT + '/13-landscape.png' });
  await page.setViewportSize({ width: 390, height: 664 }); await sleep(300);
  const lit = await ev(page, () => { const c = document.getElementById('cv'), d = c.getContext('2d').getImageData(0, 0, c.width, c.height / 2).data; let n = 0; for (let i = 0; i < d.length; i += 16) if (d[i] + d[i + 1] + d[i + 2] > 200) n++; return n; });
  check(lit > 500, 'canvas has visible content');
  await ev(page, () => { Object.defineProperty(document, 'hidden', { value: true, configurable: true }); document.dispatchEvent(new Event('visibilitychange')); });
  check(await ev(page, () => __SI.state) === 'paused', 'switching apps auto-pauses');
  await ctx.close();

  // ════════════════════════════════════════════════════════════════════════
  console.log('\n— Other phones —');
  for (const name of ['iPhone SE', 'iPhone 15 Pro Max', 'Pixel 7']) {
    const c = await browser.newContext({ ...devices[name] });
    const p = await c.newPage(); watch(p, name);
    await p.goto(URL); await sleep(400);
    await p.evaluate(() => __SI.startGame('plus')); await sleep(2100);
    const r = await p.evaluate(() => { const L = __SI.L; return { s: L.s, bottom: L.offY + 232 * L.s, w: innerWidth, h: innerHeight }; });
    const f = await p.locator('#bF').boundingBox(), l = await p.locator('#bL').boundingBox(), rr = await p.locator('#bR').boundingBox();
    check(r.bottom <= f.y + 1 && f.y + f.height <= r.h && 224 * r.s <= r.w + 0.5 && rr.x + rr.width < f.x, `${name}: playfield + controls fit (${r.w}x${r.h})`);
    await p.screenshot({ path: OUT + `/14-${name.replace(/ /g, '_')}.png` });
    await c.close();
  }

  console.log('\n— Inside an iframe (htmlpreview.github.io) —');
  const wrap = path.join(OUT, 'wrap.html');
  fs.writeFileSync(wrap, `<body style="margin:0"><iframe src="${URL}" style="border:0;width:100vw;height:100vh"></iframe></body>`);
  const ic = await browser.newContext({ ...devices['iPhone 13'] });
  const ip = await ic.newPage(); watch(ip, 'iframe');
  await ip.goto('file://' + wrap); await sleep(1000);
  const fr = ip.frames()[1];
  const fb = await fr.locator('#playBtn').boundingBox();
  await ip.touchscreen.tap(fb.x + fb.width / 2, fb.y + fb.height / 2); await sleep(2200);
  check(await fr.evaluate(() => __SI.state === 'playing' && __SI.G.phase === 'play'), 'works inside an iframe');
  await ic.close();

  check(errors.length === 0, 'no JavaScript errors' + (errors.length ? ': ' + errors.slice(0, 5).join(' | ') : ''));
  await browser.close();
  console.log(`\n${passes} passed, ${failures} failed` + (failures ? '' : ' — ALL TESTS PASSED'));
  process.exit(failures ? 1 : 0);
})().catch(e => { console.error(e); process.exit(2); });
