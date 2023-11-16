extends Node3D

@export var rotation_speed = 180
@export var camera_distance = 4

# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	$camera_arm/camera.position.z = camera_distance
	rotate_y(rotation_speed * -Input.get_axis("turntable_left", "turntable_right") * delta * PI / 180)
	$camera_arm.rotate_x(rotation_speed * Input.get_axis("turntable_down", "turntable_up") * delta * PI / 180)

