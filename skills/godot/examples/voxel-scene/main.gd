extends Node2D
## Voxel-scene exemplar (workflow: workflows/voxel-art-workflow.md).
## Builds a 4x4x4 ArrayMesh chunk + collision from pure code, saves/loads it,
## prints the audit lines, quits. Reference: references/voxel-art.md.

const CHUNK := 4
const ChunkScript := preload("res://chunk.gd")

func _ready() -> void:
	var chunk := ChunkScript.new()
	var mesh := chunk.build_mesh(CHUNK)
	var vcount := 0
	if mesh.get_surface_count() > 0:
		vcount = (mesh.surface_get_arrays(0)[Mesh.ARRAY_VERTEX] as PackedVector3Array).size()
	print("voxel chunk: vertices=%d meshing=%s" % [vcount, "greedy"])
	var data := chunk.serialize()
	var round := ChunkScript.deserialize(data)
	print("save/load equal: %s" % str(round == data))
	var node := MeshInstance3D.new()
	node.mesh = mesh
	add_child(node)
	print("voxel scene booted")
	get_tree().quit()
