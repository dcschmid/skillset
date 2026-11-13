# Face Modeling

Faces are where automated Blender workflows historically fail. This process is
deliberately slow. A simplified low-poly face is allowed; a faceless or
generic face is not.

## Identity rules

1. The face preserves the reference's identity: eye shape and placement, brow
   presence, nose form, mouth line, ear visibility, hairline.
2. Simplification = fewer edge loops, larger facets, flatter planes. It does
   NOT mean removing features.
3. If the reference character has eyes, the model has eyes — as geometry
   (sculpted or inset) or as explicitly designed texture elements. Never
   omitted silently.

## Face construction sequence (inside Pass 2)

1. **Skull block.** Scaled cube or UV sphere reduced to the designed head
   shape. Establish the eye line height and face-forward plane first.
   Head axis convention: face looks along **+Y** (see modeling-workflow).
2. **Jaw and cheeks.** Taper the lower skull; cheek line as a single edge loop
   is enough at low poly. The jaw angle is identity-bearing — match it to the
   reference before anything finer.
3. **Eye sockets / eyes.** Either shallow inset sockets + separate eyeball
   spheres (flat-shaded, 12–16 segments) or a socket-less stylized eye disc.
   Eye size vs. head size ratio measured from reference; stylized characters
   usually run larger. Eyes symmetric about the face centerline.
4. **Brows.** Thin extruded strips or beveled edge loops. Present only if the
   reference shows them; absent otherwise is a design match, not an omission.
5. **Nose.** At low poly: a wedge or a single extruded ridge. Its profile from
   the side view must match the reference profile (button / pointed / flat).
6. **Mouth.** A crease line or slightly inset strip at the correct
   head-height position; width matches the reference.
7. **Ears.** Visible from the front in the reference → modeled. Not visible →
   may be omitted, documented.
8. **Hairline and hairstyle.** Hair volume sits ON the skull (no floating),
   silhouette from side matches the reference. Strand-level detail is out of
   scope at low poly: represent the hairstyle as 2–5 designed volume shapes.
9. **Helm / headwear.** Follows `character-modeling.md`; intersects the
   hairline consistently, opening aligned with brows/eyes.

## Face view gate

- Front render: eye line level, symmetric eyes, mouth centered, proportions
  measured against reference front view.
- Side render: nose profile, jaw angle, hairstyle profile, skull depth.
- Both must pass before Pass 3.

## Budget guidance

Face region typically 300–1500 tris within a character budget of
1500–6000 tris (configurable). Faces get budget priority: when over budget,
cut torso/limb loops first, face loops last.

## Rejected outcomes

- Sphere head with two dot textures shipped as "done".
- Asymmetric eyes from modeling in a rotated pose (model in neutral, +Y facing).
- Hair as an unedited icosphere sitting on the head.
- A "handsome angle" hero shot substituting for the front/side/back gate.

## Method ceiling (honest scoring)

Primitive chains (ball+box+cyl) bound the face at readable-but-simple:
dot eyes, flat planes. That is a floor of ~60-70 against a painterly
reference, not 90+. Reference-true anime eyes need mesh operations
(boolean sockets, inset+skill, or shape keys) or a documented higher
budget. Score must cite the actual render: feature-present != face-matching.

Boolean surgery in code (verified on 5.3 background): DIFFERENCE with
solver='EXACT' via modifier_apply works, but costs debug rounds —
p.center is mesh-LOCAL (not world), socket walls need normal-based not
depth-based marking, and applying needs the object active in the view
layer. Expect ~74 with chains+booleans; 90+ needs Skulpt/shape-keys over
primitive boundaries. Budget rises when crossing those boundaries — that
is the honest cost, state it, do not fake the number.
