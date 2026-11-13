# Adding a new skill

1. **Create the directory**
   `skills/<kebab-name>/` with `SKILL.md`, plus `references/`, `scripts/`,
   `assets/`, `tests/` as needed. No empty placeholder files — a missing
   directory beats a stub.

2. **Frontmatter**
   ```yaml
   ---
   name: <kebab-name>            # identical to the directory name
   description: >
       One paragraph: what it does, when to trigger, requirements.
   ---
   ```

3. **SKILL.md = the workflow spine.** Trigger conditions, the ordered steps
   an agent must follow, binding quality rules, parameters with defaults,
   environment truths for the host. Anything longer than ~150 lines belongs
   in `references/`, linked from the step that needs it.

4. **scripts/ must execute on this machine** against the real installed
   versions (probe first; record versions in AGENTS.md). Split host vs
   embedded interpreters explicitly (e.g. Blender Python vs system Python).

5. **tests/** at minimum one reproducible end-to-end run covering the skill's
   core promise, runnable headless, printing a parseable verdict.

6. **Install + verify**

   ```bash
   tools/install-skills.sh
   blender -b --python skills/<name>/tests/test_*.py   # or its own runner
   python3 -m py_compile skills/<name>/scripts/*.py
   ```

7. **Project specifics** go in `profiles/`, never in the skill body.

## Checklist

- [ ] name == directory; description mentions trigger phrases
- [ ] works with zero prior context beyond SKILL.md
- [ ] all gates produce PASS/FAIL/REVIEW_REQUIRED, not vibes
- [ ] non-destructive outputs; collisions get dated suffixes
- [ ] installer picks it up automatically (it globs `skills/*/SKILL.md`)
