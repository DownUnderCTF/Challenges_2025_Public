extends Area2D


func _on_body_entered(body: Node2D) -> void:
	body.pozzo = true
	body.lucky = true
		



func _on_body_exited(body: Node2D) -> void:
	body.pozzo = false
