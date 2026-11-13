# Vehicle and Kart Modeling

Stylized vehicles fail on silhouette and wheel placement before they fail on
details. Build order below is ordered by identity weight.

## Build order

1. **Chassis envelope.** Overall wedge/box shape at final length/width/height
   from the side view. This is the single most identity-bearing form.
2. **Wheel positions and proportions.** Axle height, track width, wheel
   diameter — measure from the reference side view. Wheels are separate
   objects (animatable).
3. **Wheel arches / fenders.** Cut or built around wheels with consistent
   clearance (~5–10% wheel diameter stylized).
4. **Front and rear faces.** Grille/lights/rear panel as designed shapes with
   reference geometry, not decoration added last.
5. **Cockpit / driver seat / steering wheel.** Seat and wheel at plausible
   driver scale even if driver is a separate asset.
6. **Spoiler and aero.** Profile and mount points from reference.
7. **Materials.** Body color, trim, glass, tire rubber as separate materials —
   see `materials-and-uv.md`.

## Animate-ready requirements

- Each wheel: own object, origin at its hub center, +Z axle convention unless
  the target project documents otherwise; name `kart_wheel_fl|fr|rl|rr`.
- Steering wheel as its own object with hub origin.
- Body/chassis hierarchy under the asset root; wheels are children but with
  clean pivots so engine code can rotate them independently.
- No transforms baked into meshes that block rotation (apply object
  transforms, keep origins).

## Kart-specific notes (stylized racing karts)

- Open-wheel: wheels outside the body silhouette — check side view.
- Driver sits visibly above/behind the front bodywork — check side silhouette.
- Number plate / livery panel as designed geometry plane, texture-decorable.

## View gate

Front, exact side, back, top (vehicles add top over characters). Wheelbase,
overhangs, and body height measured per view. The kart must match from every
listed direction, not just the hero angle.

## Budget guidance

1200–4000 tris typical for a stylized kart (configurable). Wheels flat-shaded
12–16 segments. When trimming, delete surface subdivision before silhouette
edges.
