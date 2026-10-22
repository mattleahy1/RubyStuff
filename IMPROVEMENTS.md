# Space Invaders: 100 Improvements

Play: open `index.html` on your phone (or through htmlpreview.github.io).

## Bugs fixed
1. The game now runs at a fixed 60 ticks per second. It no longer plays twice as fast on 120 Hz iPhones.
2. Rotating the phone or the Safari toolbar showing/hiding no longer restarts the wave.
3. The game no longer resets when the screen size changes.
4. Buttons no longer get "stuck" when iOS cancels a touch (`pointercancel` handled).
5. Lifting a finger anywhere releases the button it started on.
6. A mystery ship hit twice in one frame can no longer crash the game.
7. Game over can only be recorded once (no duplicate high scores).
8. Holding FIRE at game over no longer instantly restarts a new game.
9. One bad frame can no longer freeze the game (render loop is error-guarded).
10. Storage errors (private browsing) can no longer crash the game.

## Authentic arcade gameplay
11. Full 5 × 11 fleet of 55 invaders, as in the 1978 original.
12. Correct invader types per row: squids on top, two rows of crabs, two rows of octopuses.
13. Correct points: 30 / 20 / 10.
14. Invader sprites traced from the arcade bitmaps.
15. Two-frame walking animation for every invader.
16. "Ripple" movement: one invader moves per tick, so the fleet shuffles like the arcade.
17. The fleet speeds up naturally as invaders die (55 ticks per step at full strength, 1 tick with one left).
18. The fleet drops one row each time it touches a screen edge.
19. A full, untouched fleet takes about 2½ minutes to land (first drop after ~10 seconds).
20. Invaders reaching your row means instant game over ("INVADED!").
21. The arcade's four-note marching beat, speeding up as the fleet shrinks.
22. Three different enemy bomb types (rolling, plunger, squiggly), each with its own animation.
23. The rolling bomb aims at your column, like the original.
24. The plunger and squiggly bombs use the arcade's column firing tables.
25. At most one bomb of each type on screen at once.
26. Bombs fall faster when 8 or fewer invaders remain.
27. Bomb fire rate rises as your score climbs.
28. You can shoot enemy bombs out of the air.
29. One player shot on screen at a time (classic rule), with hold-to-repeat.
30. Pixel-accurate shields that crumble where they're hit, from above and below.
31. Shot and bomb craters use the original explosion shapes.
32. Invaders that reach the shields eat through them.
33. Bombs chip holes in the ground line.
34. Mystery ship appears about every 25 seconds, only while 8+ invaders remain.
35. The mystery ship's direction depends on your shot count.
36. Mystery ship scores use the arcade table (50 to 300), including the famous 23rd-shot 300-pointer.
37. The mystery score is shown where the ship was destroyed.
38. Bonus ship at 1,500 points.
39. Each new wave starts lower on the screen, up to five rows down.
40. Shields rebuild at the start of each wave.
41. Explosion sprites for invaders, the mystery ship, shots and bombs.
42. Two-frame player explosion; the action freezes while you explode, like the original.
43. Reserve ships shown as icons next to the lives counter.

## Mobile controls
44. Multi-touch: move and fire at the same time.
45. Slide your thumb from ◀ to ▶ to change direction without lifting.
46. Bigger buttons, sized to your screen.
47. Buttons light up and shrink slightly while pressed.
48. New "Drag" control mode: the cannon follows your finger anywhere on screen.
49. Drag mode auto-fires while you're touching.
50. Optional auto-fire for button mode.
51. Left-handed option puts FIRE on the left.
52. Pinch-zoom blocked (iOS ignores the HTML setting, so it's blocked in code).
53. Double-tap zoom blocked.
54. Long-press menu and text selection disabled.
55. Pull-to-refresh / page bounce disabled.
56. Vibration feedback on hits and deaths (Android; iOS Safari doesn't support it).
57. 1.5 seconds of blinking invulnerability after respawning.
58. Respawn in the centre of the screen.

## Screen and layout
59. Fixed 224-pixel-wide game world (the arcade's width), scaled to fit every phone, so difficulty is the same on every device.
60. Respects the notch and home indicator (safe areas).
61. Landscape mode with buttons on either side of the playfield.
62. Controls never overlap the playfield.
63. Sharp rendering on Retina screens (device pixel ratio).
64. Crisp, nearest-neighbour pixel art.
65. Built-in pixel font for the score display.
66. Classic score bar: SCORE, HI-SCORE and WAVE.
67. Ground line and lives row at the bottom, like the cabinet.
68. Works inside an iframe (how htmlpreview.github.io shows it).
69. Tested on iPhone SE, iPhone 13, iPhone 15 Pro Max and Pixel 7 screen sizes.

## Graphics options
70. Neon style: coloured rows with a soft glow.
71. Arcade style: white sprites with the red and green colour strips of the original cabinet.
72. Phosphor style: green monochrome monitor look.
73. Glow is pre-rendered once, so it doesn't slow down older phones.
74. Twinkling, drifting starfield (can be turned off).
75. Optional CRT scanlines and vignette.
76. Screen shake when you're hit (can be turned off; off by default if your phone has Reduce Motion on).
77. Particle bursts when invaders explode (neon and phosphor styles).
78. Floating "+30" style score popups.
79. "WAVE 2 / GET READY" and "WAVE CLEAR" banners.

## Sound
80. Kept your sound effects (shoot, hit, march, mystery warble, fanfare, death) and tuned them.
81. Filtered noise explosions instead of raw white noise.
82. New sounds: bonus ship, wave clear, bomb-on-ground, shot-hits-bomb, menu clicks.
83. Volume slider.
84. Separate on/off for sound effects and the marching beat.
85. M key mutes and unmutes.
86. Audio unlocks properly on the first tap (iOS requirement).
87. Mystery ship sound stops when paused, dead or muted, and restarts on resume.

## Menus and flow
88. Title screen with the arcade's points table, drawn from the real sprites.
89. Invaders march in the background of the title screen.
90. How To Play screen.
91. Settings screen, saved between visits.
92. Pause button, plus a pause menu with Resume, Settings, Restart and Quit.
93. Auto-pause when you switch apps, lock the phone or get a notification.
94. 3-2-1 countdown when resuming.
95. Game over screen with wave reached, invaders destroyed, accuracy and UFOs shot.
96. Top-10 high score table, saved on your phone, with "NEW HIGH SCORE!" and your rank.
97. Lifetime stats: games, invaders, accuracy, best wave, UFOs, play time.
98. Easy / Normal / Hard difficulty (Easy gives 5 lives and slower, rarer bombs).

## Extras
99. Add-to-Home-Screen support: generated app icon, full-screen launch, and a one-time tip on iPhone.
100. Keeps the screen awake while playing; also works with a keyboard (arrows / A-D, Space, P) and Bluetooth game controllers.

---

# Round 2: 100 More Improvements (101–200)

## Game modes and power-ups
101. New game mode menu with six modes, each showing your best score.
102. **Plus** mode: power-ups, combos and wave bonuses.
103. Power-up capsules (lettered, colour-coded) fall from every mystery ship you shoot, and occasionally from invaders.
104. **R**: rapid fire (two shots on screen, faster bullets) for 10 seconds.
105. **S**: three-way spread shot for 10 seconds.
106. **L**: a laser that pierces straight through invaders and bombs.
107. **T**: time warp, which slows invaders, bombs and the mystery ship to half speed.
108. **H**: rebuilds all four shields.
109. **+**: rare extra life.
110. Power-up timer bar in the bottom row.
111. Combo multiplier: every 8 hits in a row raises it (up to x4). A miss resets it.
112. **Hardcore** mode: one life, fast bombs, no bonus ship.
113. **Time Attack** mode: a 2-minute clock and endless waves.
114. **Daily Challenge**: a seeded game that plays out the same for everyone on a given day.
115. **Practice** mode: invaders never shoot, and nothing is recorded.
116. Separate top-10 high-score tables for each mode.

## Gameplay
117. The fleet freezes for a split second when you hit an invader, like the arcade.
118. Arcade quirk: the last invader moves 3 pixels right but only 2 left.
119. Danger warning: a pulsing red line, and the ground turns red, when invaders are 4 drops from landing.
120. A danger alarm sounds while they're that close.
121. Wave-end bonuses in Plus, Time Attack and Daily: up to +500 for accuracy and +500 for not dying.
122. A wave-clear summary showing your accuracy and bonuses.
123. Endless difficulty curve: bombs keep getting faster after wave 8.
124. In Neon style, invaders glow redder as they get closer to the ground.
125. Time Attack: +10 seconds for every wave cleared.
126. Time Attack: dying, or an invasion, costs 10 seconds instead of ending the game.
127. **Continue**: your game is saved when you pause, switch apps, or every 10 seconds, so you can pick up where you left off even if iPhone closes the tab.
128. The score counter rolls up smoothly.
129. A "NEW HI-SCORE!" alert the moment you pass your best.
130. Coaching hints over the controls in your first game.
131. Very quick taps on FIRE are never lost, even if they're shorter than one frame.

## Controls
132. New **Trackpad** control: swipe anywhere to nudge the cannon.
133. New **Tilt** control: steer by tilting the phone (asks for motion permission on iPhone).
134. Tilt/swipe sensitivity setting.
135. Tilt re-centres when you start or resume, plus a RECENTER TILT button in the pause menu.
136. Tap the playfield to fire (button and tilt modes).
137. Button size setting (small / medium / large).
138. Button look setting (solid / faded / ghost).
139. A tiny vibration tick when you press a control (Android).
140. Controller rumble when you're hit (supported controllers).
141. Controller menu navigation: D-pad, A to select, B to go back, Start to pause.
142. Keyboard menu navigation: arrow keys, Enter and Esc, with a visible focus outline.
143. The Android or browser back button pauses the game and closes menus instead of leaving the page.

## Visuals
144. Invaders flash white for an instant when hit.
145. Muzzle flash when you fire.
146. Glowing shot trails, and a wider glowing laser beam.
147. Debris flies off shields when they're hit.
148. Dust kicks up where bombs hit the ground.
149. The mystery ship's lights blink.
150. A shockwave ring when the mystery ship explodes.
151. The screen flashes red when you're hit.
152. Your cannon bursts into particles when destroyed.
153. The lives counter blinks red on your last life.
154. Shooting stars streak across the starfield.
155. A soft nebula behind the stars in Neon style.
156. The title logo shimmers between green and cyan.
157. Attract mode: an AI pilot plays the game behind the title screen.
158. "Sharp pixels" option: each game pixel is a whole number of screen pixels.
159. High-contrast graphics style.
160. Colour-blind-safe graphics style (Okabe–Ito colours).
161. Confetti when you set a new high score.
162. Shields build up from the ground at the start of each wave.
163. Battery saver option: draws 30 frames per second instead of 60.

## Sound
164. Stereo sound: shots, explosions and the mystery ship come from where they happen.
165. The mystery ship's siren pans across as it flies.
166. A compressor stops the sound distorting when lots happens at once.
167. Separate volume sliders for effects and music.
168. Game-over jingle.
169. New-high-score fanfare.
170. Power-up and power-down sounds.
171. 3-2-1 countdown beeps when resuming, and a "go" chirp at each wave start.
172. Combo-up sound that rises in pitch.
173. Time Attack clock ticks in the final 10 seconds.
174. Award-unlocked chime.
175. The marching beat gets deeper and louder in the danger zone.
176. Laser sound effect.

## Progression
177. 20 awards to unlock.
178. Awards screen showing which you have.
179. Award-unlocked banner during play.
180. Arcade-style 3-letter initials entry for top-10 scores.
181. Your initials are remembered for next time.
182. Share your score (iPhone share sheet, or copies a message).
183. Pilot ranks from Cadet to Admiral, based on invaders destroyed.
184. Rank progress on the title screen, and "PROMOTED!" on the game-over screen.
185. 12 lifetime stats, including total score, best streak, power-ups, bombs shot and longest game.
186. Daily Challenge streak counter and today's best.
187. The title screen shows the selected mode and your best score in it.
188. Save-data versioning, so old high scores carry over (into the Classic table).

## Accessibility
189. Large text option for menus.
190. Reduce-flashing option (no red flash, blinking or shake).
191. Screen-reader announcements for waves, lives, power-ups, awards and game over.
192. 75% speed assist option (those games aren't ranked).
193. The pause screen shows your mode, score, wave and lives.
194. Quitting a game in progress needs a second tap to confirm.

## Under the hood
195. Recovers if iPhone drops the game's graphics memory.
196. Adaptive quality: glow switches off automatically if the phone struggles.
197. Friendly error screen with a restart button if something goes badly wrong.
198. Export/import a save code, to move scores into the home-screen app (iPhone keeps its data separate).
199. Settings grouped into sections, with reset-to-defaults and a version number.
200. An automated test suite (`node tests/e2e.js`) that plays the game on emulated iPhones and Android phones.
