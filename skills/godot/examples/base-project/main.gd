extends Node
## Base-example boot: input actions -> typed signal -> reusable component.
## Genre-agnostic shape; run headless: godot --headless --path . --quit-after 60

signal announced(text: String)

const Counter := preload("res://counter.gd")

@onready var counter: Counter = $Counter

func _ready() -> void:
	announced.connect(_on_announced)
	announced.emit("base-example ready on %s" % Engine.get_version_info().get("string", "?"))

func _process(_delta: float) -> void:
	if Input.is_action_just_pressed("action_a"):
		counter.bump()

func _on_announced(text: String) -> void:
	print(text)
