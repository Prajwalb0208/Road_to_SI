# LVL 05 — Mech Dragon · build log (long-form source of truth)

Every version, every owner note (verbatim where it matters), every fail and fix, every file. The long video script is written from this.
Owner rules: record the whole build; Cycles samples ≤ 512; final must look good; no human review said once in the video.

## Timeline

| # | Version | What changed | Owner reaction / why next | Evidence |
|---|---------|--------------|---------------------------|----------|
| 1 | v1 `dragon.py` | Bronze/obsidian dragon from primitives + curved shells, 51-bone rig, awakening anim, ruins set | Owner showed a Zoids-style red/gold mecha painting: *"This is what i meant by complex"* | `work/test/a_*.png`, `t_*.png` |
| 2 | swatches | 3 candy paints (A blue, B emerald, **C black-cherry**) | Picked **C**: *"colour should be good instead of normal grey or steel colour"* | `work/test/swatches.png` |
| 3 | v2 `mecha.py` (take 1–2) | Kitbash library (piston, gear, turbine, vent, ribs, split panels), candy paint with cavity/flake/clear coat/edge wear, 426 parts, shrinkwrapped head plates | — | `rec/t1_kit.mkv` 28.9 s, `rec/t2_body.mkv` 87.3 s |
| 4 | rig (take 3) | 51 bones, 10 Stretch-To pistons, pose test; white feathers fixed (edge wear on thin plates → `M_paint_clean`) | Close-up sent | `rec/t3_rig.mkv` 154.7 s, `test/close_*.png` |
| 5 | v3 (take 4) | Bulkier legs, heavier head + visor glow, armoured wing arm, head camera fix | *"Fix them"* → then jaw gap + knee caps | `rec/t4_fixes.mkv` 22.2 s |
| 6 | v4 | Jaw closes (loft tops follow skull), overbite teeth, knee guards | Preview v1 sent | `test/lvl05_awakening_preview.mp4` |
| 7 | v5 | **Jaw bug**: jaw core lost its parent in an edit (floated in mid-air); inline `#` comment swallowed teeth parenting. Fixed. + micro details (598 rivets, codes, hazard tabs, LEDs, hydraulic lines) + transformer armour unlock/slam | *"the jaw is broken… buildup looks lame… like transformer… tiniest details"* | `test/lvl05_awakening_preview_v5.mp4` |
| 8 | v6 | Fierce face (scowl slit eyes, brow blades, sabre fangs, cheek spikes, chin/nose blades, throat glow), feathers deploy one by one, head split + re-lock, roar, 15 s, 3/4 face camera | *"Go bigger and also make sure the face looks feirceful"* | `test/lvl05_awakening_preview_v6.mp4` |
| 9 | v7 `v7.py` | Big wings, face internals (lens eyes, jaw gearsets, crest gear train, wires, traces), gearboxes/gearsets/cables/spanners, dead terminals + robot husks + braziers/embers + Poly Haven boulders, laser breath that blasts a terminal, 420 frames | *"wings more terrifying and large… dead terminals… fire and laser… face looks like nothing… gearboxes, spanners, wires… terrifying"* | `test/v7/*.png` |
| 10 | v7 wings ×3 | thin spikes → heavy 11 cm plates → filled (inner plates hang arm→body) → patterned (cyan veins, gold arcs, alternating cherry/dark-cherry, scallop tips) | *"thin and funny"* → *"why's it only in the top"* → *"have good pattern of wings"* | `test/v7_wings_still.png`, `v7_wings_filled.png`, `v7_wings_pattern.png` |
| 11 | v8 `v8.py` | Mystical ancient hall: flagstones, summoning rune circle (ignites with the core), colossal portal ring with swirling energy, glyph-banded pillars, levitating rocks, crystals, chains, roots, colossal stone guardian head, ground mist, violet moon | *"make it more mystical mysterious ancient and crazy"* | `test/v8_env_still.png` |
| 13 | v8 head | Eye slits own material (cyan, keyed with ignition/split/laser), halo shells, socket lights; scales: geometry studs (read as a pineapple, rejected by me) → procedural Voronoi scales (domed bump + gold seams) on skull, jaw, brows, crest, cheeks, neck plates; tracking cyan head rim + stronger face spot | *"make sure the head of the dragon looks good… I want the eyes and scales to be highlighted"* | `test/v8_head_scales.png` |
| 14 | v8 dark grade | Palette discipline: black-cherry paint (#4A0818), antique bronze metal, ONE accent (cyan) for eyes/core/runes; red rim + violet glyphs/crystals/portal removed; hall near-black, portal deep teal and dim; wing veins ×0.22; exposure −0.35, AgX High Contrast | *"looks like a vomit of colours, keep it dark and mysterious"* | `test/v7/dark.png`, `work/mecha_v8_dark.blend` |
| 12 | v8 light | Dragon-tracking hero spots (warm key, cyan + red rims, face spot, warm under-bounce), env accents dimmed | *"dragon is not highlighted enough"* | preview v8 (rendering) |

| 16 | v10 `v10.py` + `collide.py` | Eyes: 25 cm almond slits seated in sockets under the brow, vertical white-hot pupils (keyed with the slits). Flight physics: wings tucked through turn/charge/breach, unfold clear of the wall, 12-f flap cycles (fast down/slow up, forearm lags 2 f, feathers spread on the downstroke + half-fold on the upstroke), body bob + pitch breathing, legs gallop on the charge then trail horizontal, tail sway. Sleep fold lifted. Wing clearance zone + charge/flight corridor (pillars, rocks, chains, rubble, husks, spanners, blasted terminal moved). Breach bigger (180 blocks) and blasted sideways out of the path. Flight camera keyed on the real path. **collide.py audit: 4403 → 0 wing hits over all 640 frames** (BVH overlap of every wing part vs env + own body; flight checked every 2 f) | *"make sure eyes are placed correctly… wings should follow physics… legs horizontal in flight… no objects should collide with wings or go through wings"* | `test/v10_flight.png`, `test/v10_eyes_flight.png` |

| 17 | v11 `v11.py` | Wall stays whole until the hit (boolean + blocks keyed on at f588), jagged noise-sphere hole, 180 irregular fractured rocks (slab/chunk/small convex hulls), 900 gravel + 2500 grit particles, 23 rolling volumetric dust clouds at the breach (both faces + hanging pall), 22 dust plumes where the stone shell bursts. Hole widened ~10 % after audit (2 feather-tip hits → 0). Preview `test/lvl05_preview_v11.mp4` (26.7 s, 50 %, EEVEE 16 spp, 640 f in ~2 h, 9→16 s/f) | *"we need more dust and natural burst of wall or rock"* → *"ok render we'll see"* | `test/v11_dust_breach.png`, `test/replay_v11.png` |

| 18 | final | Blocked shot 5-6 s fixed (camera path moved between the braziers, husk 3 off the camera line), shell-burst dust thinned so the dragon reads through it. **Final render started** from `work/mecha_final.blend`: EEVEE 1920×1080, 64 spp, motion blur, resumable PNG frames → `exports/frames_1080/` → `exports/lvl05_mech_dragon_hero_1080p.mp4` | *"Fix the blocked camera at 5-6 s, then start the 1080p EEVEE final render."* | `test/v7/s_130.png` |

| 19 | v12 + v13 (honest review) | Owner: *"what made everything turn stone to dragon / remove all sources of lights before the awakening / the computers are bad / why was the leg that bad when it started flying / make it cinematic / story making sense / the main thing is dragon itself is not proper… pieces not attached"*. Answers given straight: no cause was shown; the tomb was lit for no reason; terminals off-tone; legs aimed straight back = stick legs; no DOF/shake/shot design; dragon = ~1100 rigid pieces with no body. Fixes: **continuous skinned body** (skin modifier along the skeleton, near-rigid nearest-bone weights — auto heat weights let the armour float off in the curled pose); **re-seat** (112 floating parts → snapped); **per-bone anchor** (63 parts snapped onto their bone core; neck seams = invisible edge rings removed; jaw hinge pin; teeth rooted); fixed 3.3 m stray strut. Story: **lightning** through the roof onto the statue's head (f20/24) → eyes → cracks → shell → temple ignites (braziers 124-148, crystals 150, glyphs 156, portal 162-176), dark tomb before; terminals removed, laser cuts a glowing scar into the wall it then smashes. Legs: real flight tuck. Cinema: DOF f/2.4 on the head, 180° shutter, 2.39:1, shake on 10 hits, grain + vignette at encode | picked: lightning trigger, continuous body | `test/v13_inspect.png`, `work/inspect_views.py`, `work/gap_audit.py`, `work/float_probe.py` |

### v10 collision audit trail
4403 hits (v9 baseline: floor/tail/rubble/boulders while asleep, pillar 1 + floating rock while spread, wall + blocks at the breach) → 7 + 1289 (clear zone, sleep fold) → 1442 (slow blocks hung in the path) → 1428 (syntax slip, audit ran on stale file) → 31 (sideways blast, bigger breach) → 17 (later unfold) → 1 (spanners, terminal) → **0** (husk 0 moved).

### v9 fixes found in test frames
- Breach cut smeared (camera flew 10 m in 10 frames + motion blur) → hard CONSTANT cut to outside at f597, shutter 0.35.
- Flight shot black: EEVEE world volume absorbs the whole sky background → haze moved into a volume box around the hall (`hall haze`), world volume unlinked; storm clouds brightened; moon sun + two chest-tracking flight spots on after the breach.
- Dragon turned back to STONE in the sky: the reveal is distance-from-head based and capped at 14 m → R held at 900 after f124.
- Statue camera blocked by a brazier → moved between the braziers.

## Fails worth showing in the video (honest receipts)
- SimpleDeform BEND barely bent shells → bent in the vertex math.
- Turbine cowl invisible (edge-only circle can't be solidified) → tube. *(take 1)*
- Head plates floated as flat slabs → shrinkwrapped sheets. *(take 2)*
- Feathers rendered white (AO edge wear reads thin plates as all-edge) → wear-free paint copy.
- Jaw floated in mid-air in the preview (lost rig parent) — owner caught it: *"the jaw is broken"*.
- Inline `#` comment in a one-line edit swallowed the teeth's rig parenting → teeth hung in the air at frame 110.
- Rotating gears via `rotation_euler` drivers after rig parenting would wreck their orientation → spin on `delta_rotation_euler`.
- Live shrinkwrap would pull opening plates back onto the skull → baked before the transform.
- Fire cones rendered as solid pink cones (AgX + emission 18) → thin tongues, emission 2.2.
- Laser ray-cast hit the ground-mist volume box → skip volumes/fx in the ray loop.
- EEVEE "Shadow buffer full (2446/2048)" → accent lights cast no shadows.
- Screen locked mid-session → live take 5 couldn't record (gdigrab error 5); built headless, live take re-run on unlock.

## Files
- Builders: `work/dragon.py` (v1 base + set/light/anim), `work/mecha.py` (paint, kitbash, body, fierce face, details, transform, bigger, rig), `work/v7.py` (wings, face internals, body mechanics, env props, laser), `work/v8.py` (mystical hall, dragon lighting).
- Runners: `work/anim_v7.py` (full headless build + test frames → `mecha_v7.blend`), `work/anim_v7_preview.py` (EEVEE preview).
- Takes: `work/rec/t1_kit.mkv`, `t2_body.mkv`, `t3_rig.mkv`, `t4_fixes.mkv`, `t5_v9_build.mkv` (136.7 s: full v9 rebuild live, body → face → heavy wings → mechanics → details/scales/rig → mystical hall → lights → animation → stone/sky/finale, then a camera-view scrub of all 640 frames). All privacy-scanned: Blender only. Live file `work/mecha_live_v9.blend`; final renders come from the headless `work/mecha_v9.blend` (same scripts).
- Previews: `work/test/lvl05_awakening_preview*.mp4`, stills in `work/test/`.

| 15 | v9 story `v9.py` | Owner's new story: stone statue → eyes glow first → cyan cracks race head→tail and the stone shell shatters off (reveal shader group on every dragon material + chunk bursts) → awakening (old timeline shifted +120 f) → turns, charges, smashes through the right hall wall (112 blocks) → flies up into a night storm (cloud world, moon, lightning, ridges). 640 f ≈ 26.7 s | *"transition from stone to this live cyberpunk creature… first the eyes glow and then everything… destroys the cave wall and moves to fly in the sky"*; picked: stone shell shatters, night storm, ~25 s | `test/v7/v7_*.png` |

## Render decision (benchmark 2026-10-21, `work/bench.py`, frame 205, 1080p, mecha_v8_dark.blend)
| Engine | Time / frame | Notes |
|---|---|---|
| EEVEE, 128 TAA | ~91 s | raytracing on, volumes; matches previews |
| Cycles CUDA 128 + OIDN | ~7 min | |
| Cycles CUDA 256 + OIDN | ~12.8 min | peak VRAM 3.49 / 4 GB (near the limit) |
| Cycles 512 | not run (~25 min est.) | owner cap 512 |
GTX 1650 4 GB. 640 frames in Cycles = 75 h+ at 128 → not viable. **Final = EEVEE** (side-by-side `test/bench/cmp.png`: EEVEE reads as well or better in this dark scene). Cycles only for 1–3 hero stills (thumbnail) at ≤ 512 samples.
