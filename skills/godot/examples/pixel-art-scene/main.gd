extends Node2D
## Pixel-art scene exemplar (workflow: workflows/pixel-art-workflow.md).
## Boots headless-safe; prints the style-gate checks and quits.

const BASE := Vector2i(320, 180)

func _ready() -> void:
	print("pixel-art gate: viewport=%s filter=%s snap_xf=%s" % [
		get_viewport().get_visible_rect().size,
		ProjectSettings.get_setting("rendering/textures/canvas_textures/default_texture_filter"),
		ProjectSettings.get_setting("rendering/2d/snap/snap_2d_transforms_to_pixel"),
	])
	var cam := Camera2D.new()
	cam.position_smoothing_enabled = true
	cam.position_smoothing_speed = 8.0
	add_child(cam)
	var label := Label.new()
	label.text = "pixel %dx%d" % [BASE.x, BASE.y]
	add_child(label)
	await get_tree().create_timer(0.25).timeout
	print("pixel-art scene booted")
	get_tree().quit()
