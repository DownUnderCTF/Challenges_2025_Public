extends Area2D
@onready var timer: Timer = $Timer

func _on_body_entered(body: Node2D) -> void:
	# body.get_node("CollisionShape2D").queue_free()
	body.isAlive = false
	timer.start()

func _on_timer_timeout() -> void:
	get_tree().reload_current_scene()


func _on_world_boundary_lhs_body_entered(body: Node2D) -> void:
	body.global_position.x = 639


func _on_world_boundary_rhs_body_entered(body: Node2D) -> void:
	body.global_position.x = -639
