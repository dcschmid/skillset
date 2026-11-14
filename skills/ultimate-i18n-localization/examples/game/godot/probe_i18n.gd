extends SceneTree
# Headless adapter probe (Godot 4.7.2). Prints PROBE PASS/FAIL + counts.
func _init():
	var fail := 0
	var t := Translation.new()
	t.locale = "de"
	t.add_message("nav/home", "Startseite")
	t.add_message("actions/save", "Speichern")
	TranslationServer.add_translation(t)
	TranslationServer.set_locale("de")
	if TranslationServer.translate("nav/home") != "Startseite":
		print("  de/home wrong: ", TranslationServer.translate("nav/home")); fail += 1
	TranslationServer.set_locale("fr")  # no fr catalog -> fallback "en" -> key passthrough
	var fb := TranslationServer.translate("actions/save")
	if fb != "actions/save":
		print("  fallback wrong: ", fb); fail += 1
	var ps := TranslationServer.pseudolocalize("Hello {name}")
	# engine pseudo transforms identifier glyphs inside {} too; structure survives
	if not ("{" in ps and "}" in ps):
		print("  pseudo lost placeholder braces: ", ps); fail += 1
	if TranslationServer.get_plural_rules("ar") != "nplurals=6; plural=(n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 && n%100<=99 ? 4 : 5);":
		print("  plural rules drift"); fail += 1
	if TranslationServer.standardize_locale("de_DE") != "de_DE":
		fail += 1
	print("PROBE ", "PASS" if fail == 0 else "FAIL", " keys=2 pseudo_braces_ok=", "{" in ps and "}" in ps)
	quit(0 if fail == 0 else 1)
