extends Area2D

@onready var check = null
@onready var godot = false
@onready var godotSprite = $AnimatedSprite2D

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	var now := int(Time.get_unix_time_from_system())
	var day := 86400  # 24 * 60 * 60
	check = now - day
	# var dbg_time = 5
	# check = now + dbg_time
	godotSprite.hide()


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	var now := int(Time.get_unix_time_from_system())
	if now == check and godot == false:
		godot = true
		godotSprite.show()

func _on_body_entered(body: Node2D) -> void:
	body.shop = true
	body.godot = godot

func _on_body_exited(body: Node2D) -> void:
	body.shop = false
