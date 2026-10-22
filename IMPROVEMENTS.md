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
