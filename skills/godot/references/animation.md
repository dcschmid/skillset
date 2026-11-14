# Animation (4.7 baseline)

Route by detected content type; verify exact node/method names in 4.7 docs.

## Sprite / 2D

`AnimatedSprite2D` + `SpriteFrames` for flips; `AnimationPlayer` for
property/`method` tracks (UI, cutscenes); `AnimationTree` for blendspaces and
state-machine playback over animations. Stepped keys for retro feel.

## Skeletal 3D

`AnimationPlayer` (imported clips) → `AnimationTree` (RESET / blend /
`AnimationNodeStateMachine`); root motion vs in-place per genre (verify
`Skeleton3D` motion-extract API); retarget via shared skeleton or per-mesh.

## IK & procedural

`SkeletonIK3D` (two-bone, foot placement); procedural: `AnimationPlayer`
track codegen or direct bone pose in `_process` (tails/props). `PhysicalBone3D`
ragdoll fallback on death — budget per-character.

## State wiring

`AnimationNodeStateMachine` mirrors the gameplay `enum` state machine
(`gameplay-systems.md`); transitions driven by signal, not `match` polling in
`_process`. Blend spaces for speed/direction.

## Gates

IMPORTED: clip length/count from `.import`; RUNTIME: play through state graph
covering every state once; VISUAL: foot-slide / pop check on lowest target.
Missing imports (blank AnimationList) surface in import log — treat as FAIL.
