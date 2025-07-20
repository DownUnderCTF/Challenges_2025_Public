extends CharacterBody2D

const SPEED = 200.0
const JUMP_VELOCITY = -400.0

@onready var playerSprite = $AnimatedSprite2D
@onready var isAlive = true
@onready var lucky = false
@onready var godot = false
@onready var pozzo = false
@onready var shop = false

func _physics_process(delta: float) -> void:
	if isAlive:
		if Input.is_action_pressed("interact") and is_on_floor():
			if shop:
				if lucky and godot:
					global_position.x = 0
					global_position.y = -10000
				elif godot:
					DialogueManager.show_example_dialogue_balloon(load("res://dialgoue/estragon_godot.dialogue"), "start")
				else:
					DialogueManager.show_example_dialogue_balloon(load("res://dialgoue/estragon.dialogue"), "start")
				
			elif pozzo:
				DialogueManager.show_example_dialogue_balloon(load("res://dialgoue/pozzo.dialogue"), "start")
				lucky = true
		
		if Input.is_action_pressed("jump") and is_on_floor():
			velocity.y = JUMP_VELOCITY
		elif Input.is_action_pressed("move_left"):
			playerSprite.flip_h = true
			velocity.x = -1 * SPEED
			if is_on_floor():
				playerSprite.animation = "move"
		elif Input.is_action_pressed("move_right"):
			playerSprite.flip_h = false
			velocity.x = SPEED
			if is_on_floor():
				playerSprite.animation = "move"
		else:
			velocity.x = 0
			if is_on_floor():
				playerSprite.animation = "idle" 
		
		# Gravity + fall anim
		if not is_on_floor():
			playerSprite.animation = "air"
			velocity += get_gravity() * delta
			
	else:
		playerSprite.animation = "death"
		velocity.x = 0
		
	move_and_slide()
