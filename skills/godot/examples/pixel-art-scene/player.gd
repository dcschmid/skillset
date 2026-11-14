extends CharacterBody2D
## Pixel-perfect mover: integer-snapped positions at base resolution
## (references/pixel-art.md). Input-agnostic: intent comes from the caller.

@export var speed_px: int = 60

func walk(intent: Vector2, delta: float) -> void:
	velocity = Vector2(roundf(intent.x * speed_px), roundf(intent.y * speed_px))
	move_and_slide()
	position = position.round()
