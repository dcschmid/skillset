extends RefCounted
## Deterministic voxel chunk with greedy-merge meshing (references/voxel-art.md).
## Data = flat PackedByteArray, id 0 = air. Mesh = one surface, merged quads,
## per-quad normals; collision rebuild is the caller's cadence decision.
## No global class_name: consumers preload this file, so the example parses
## before any import cache exists.

var blocks := PackedByteArray()
var size := 0

func index(x: int, y: int, z: int) -> int:
	return (y * size + z) * size + x

func fill(n: int, gen: Callable) -> void:
	size = n
	blocks.resize(n * n * n)
	for y in n:
		for z in n:
			for x in n:
				blocks[index(x, y, z)] = gen.call(x, y, z)

func at(x: int, y: int, z: int) -> int:
	if x < 0 or y < 0 or z < 0 or x >= size or y >= size or z >= size:
		return 0
	return blocks[index(x, y, z)]

## Greedy merge along +x runs of equal id with open +y face (air above).
func build_mesh(n: int) -> ArrayMesh:
	fill(n, func(x: int, _y: int, z: int) -> int: return 1 if (x + z) % 2 == 0 else 0)
	var verts := PackedVector3Array()
	var norms := PackedVector3Array()
	for y in size:
		for z in size:
			var x := 0
			while x < size:
				var id := at(x, y, z)
				if id == 0 or at(x, y + 1, z) != 0:
					x += 1
					continue
				var run := 1
				while x + run < size and at(x + run, y, z) == id and at(x + run, y + 1, z) != 0:
					run += 1
				var base := Vector3(x, y + 1, z)
				verts.append_array([base, base + Vector3(run, 0, 0),
					base + Vector3(run, 0, 1), base + Vector3(0, 0, 1)])
				norms.resize(norms.size() + 0)
				for _i in 4:
					norms.append(Vector3.UP)
				x += run
	if verts.is_empty():
		return ArrayMesh.new()
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = verts
	arrays[Mesh.ARRAY_NORMAL] = norms
	arrays[Mesh.ARRAY_INDEX] = _quad_indices(verts.size() / 4)
	var mesh := ArrayMesh.new()
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	return mesh

func _quad_indices(quads: int) -> PackedInt32Array:
	var idx := PackedInt32Array()
	for q in quads:
		var o := q * 4
		idx.append_array([o, o + 1, o + 2, o, o + 2, o + 3])
	return idx

func serialize() -> Dictionary:
	return {"size": size, "blocks": blocks}

static func deserialize(payload: Dictionary) -> Dictionary:
	return {"size": int(payload["size"]), "blocks": payload["blocks"]}
