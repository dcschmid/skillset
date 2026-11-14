extends Node
## Reusable gameplay component (component-pattern exemplar in
## references/architecture.md): owner-agnostic, signal-out, inspector-tunable.
## Preloaded by consumers (const Counter := preload) instead of a global
## class_name, so the example parses before any import cache exists.

@export var step: int = 1
@export var start_at: int = 0

var value: int = 0:
	set(v):
		value = v
		changed.emit(value)

signal changed(value: int)

func _ready() -> void:
	value = start_at

func bump() -> void:
	value += step
