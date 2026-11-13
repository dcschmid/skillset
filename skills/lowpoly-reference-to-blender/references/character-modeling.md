# Character Modeling

Highest-priority specialty. Generic Blender character passes produce weak
faces; these passes exist to prevent that.

## Character build passes

### Pass 1 — Silhouette

- Head, torso, hips, limbs at final proportions. Block with primitives only
  as scaffolding — every primitive gets edited into its designed form before
  Pass 1 ends.
- Head:body ratio is identity-bearing. Measure it against the reference in
  front view before adding anything.
- Pose is neutral A- or T-pose for export; posing is engine-side or via
  later rig.
- Exit test: front + side renders match the reference silhouette at squint
  distance. No materials yet.

### Pass 2 — Character identity

- Work `face-modeling.md` in full.
- Hair / helmet / headwear as designed shapes, not primitives dropped on the
  skull.
- Signature features from the feature inventory (goggles, scarf, markings)
  exist as actual geometry or explicitly-documented texture decisions.
- Exit test: the character is recognizable from the front render alone,
  compared side-by-side with the reference.

### Pass 3 — Polish

- Materials per `materials-and-uv.md`; palette locked to reference samples.
- Bevel transitions, hard edges, small details.
- No shape changes to Pass 1/2 geometry without a re-run of the view gate.

## Proportions checklist

- Head height in BU and as body fraction (`head_up` value)
- Eye line sits at the correct head-height fraction for the stylization
  (stylized characters: lower/larger eyes — but consistent with reference)
- Shoulder width, arm length, hip width relative to reference

## Character Multi-View Gate

Front, exact left side, back. Hero view optional. Each render compared to the
matching reference; unseen views documented as reconstruction.

## Failure patterns to reject

- Pretty-in-one-angle character shipped without side/back verification
- Face as smooth blob with painted eyes (unless the project is explicitly
  flat-shaded-paper style — then it is a documented design choice, not a shortcut)
- Hair/helmet floating off the scalp
- Identity features dropped because "low poly"
