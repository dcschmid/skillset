# Clean atomic build: Kira Pulse low-poly driver, faces -Y (project convention).
# Run: blender -b --python kira_build.py  (real API, not MCP safe-mode)
import bpy, bmesh, math
from mathutils import Matrix, Vector

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for m in list(bpy.data.meshes):
    bpy.data.meshes.remove(m)

sc = bpy.context.scene

def mat(name, rgb, rough=0.5, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    m.diffuse_color = (*rgb, 1.0)
    return m

MDARK  = mat("kira_dark", (0.16,0.18,0.22))
MLIGHT = mat("kira_light", (0.80,0.82,0.85), 0.45)
MPURP  = mat("kira_purple", (0.50,0.34,0.87))
MHAIR  = mat("kira_hair", (0.46,0.23,0.80))
MMAG   = mat("kira_magenta", (0.88,0.23,0.66))
MCYAN  = mat("kira_cyan", (0.18,0.80,0.76), 0.4)
MGLOVE = mat("kira_glove", (0.12,0.14,0.17))
MSKIN  = mat("kira_skin", (0.93,0.75,0.60))
MIRIS  = mat("kira_iris", (0.42,0.26,0.13), 0.3)
MEYE   = mat("kira_eye", (0.90,0.90,0.93), 0.35)

root = bpy.data.objects.new("kira_root", None)
sc.collection.objects.link(root)

def add(name, bm, loc, material, parent=root):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = False
    me.update()
    o = bpy.data.objects.new(name, me)
    sc.collection.objects.link(o)
    o.parent = parent
    o.location = loc
    me.materials.append(material)
    return o

def box(*s):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co.x*=s[0]; v.co.y*=s[1]; v.co.z*=s[2]
    return bm
def ball(u, v, r):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=r); return bm
def cone(seg, r1, r2, d, ax=None, ang=0.0):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r1, radius2=r2, depth=d)
    if ax: bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(ang,3,ax), verts=bm.verts[:])
    return bm
def cyl(seg, r, d, ax=None, ang=0.0):
    return cone(seg, r, r, d, ax, ang)
def rz(bm, ang): bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(ang,3,"Z"), verts=bm.verts[:])
def rym(bm, ang): bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(ang,3,"Y"), verts=bm.verts[:])

# ---- proportions (m, feet at 0, faces -Y) ----
HIPZ, SHOZ, HEADZ, HELMZ = 0.86, 1.235, 1.455, 1.560

# legs (charcoal) + thigh stripes + knees + boots + cyan toe
for sx in (-1, 1):
    nm = "l" if sx < 0 else "r"
    add(f"kira_leg_{nm}", cyl(6, 0.052, HIPZ-0.09, ax=None), (sx*0.075, 0.005, (0.09+HIPZ)/2), MDARK)
    bm = box(0.010, 0.028, 0.14); rz(bm, math.radians(6*sx))
    add(f"kira_thighmag_{nm}", bm, (sx*0.120, -0.010, 0.640), MMAG)
    bm = box(0.010, 0.024, 0.16); rz(bm, math.radians(9*sx))
    add(f"kira_thighcy_{nm}", bm, (sx*0.128, 0.010, 0.540), MCYAN)
    add(f"kira_knee_{nm}", box(0.055,0.05,0.06), (sx*0.075, -0.042, 0.505), MLIGHT)
    add(f"kira_boot_{nm}", box(0.070,0.15,0.070), (sx*0.075, -0.020, 0.045), MDARK)
    add(f"kira_toe_{nm}", box(0.056,0.05,0.034), (sx*0.075, -0.115, 0.028), MCYAN)

# torso (hourglass charcoal) + belt + buckle
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=3, use_grid_fill=True)
for v in bm.verts:
    z = v.co.z + 0.5  # 0 hip ->1 shoulder
    if z < 0.28: w = 0.62      # hips
    elif z < 0.5: w = 0.44     # waist
    elif z < 0.85: w = 0.66    # chest
    else: w = 0.52
    v.co.x *= w*0.30; v.co.y *= (0.17 if z<0.5 else 0.13); v.co.z *= (SHOZ-HIPZ)
add("kira_torso", bm, (0, 0.005, (HIPZ+SHOZ)/2 + 0.02), MDARK)
add("kira_belt", box(0.21,0.17,0.05), (0,0.005,HIPZ+0.02), MDARK)
add("kira_buckle", box(0.03,0.012,0.028), (0,-0.095,HIPZ+0.02), MCYAN)

# chest gems: slanted shards (readable at distance)
bm = box(0.070,0.012,0.125); rym(bm, math.radians(10)); rz(bm, math.radians(20))
add("kira_gem_cyan", bm, (-0.048,-0.118,1.120), MCYAN)
bm = box(0.052,0.012,0.150); rym(bm, math.radians(10)); rz(bm, math.radians(-16))
add("kira_gem_mag", bm, (0.052,-0.118,1.115), MMAG)

# arms: parametric from shoulder, A-pose ~30deg, connect by construction
for sx in (-1, 1):
    nm = "l" if sx < 0 else "r"
    add(f"kira_shoulder_{nm}", ball(6,4,0.052), (sx*0.150, 0.005, SHOZ+0.010), MLIGHT)
    a = math.radians(30)
    arm = cyl(6, 0.030, 0.40, ax="Y", ang=0.0)
    # build along local Z then rotate about Y so top stays at shoulder
    rym(arm, -a*sx)
    # offset so it points down-out from shoulder
    add(f"kira_arm_{nm}", arm, (sx*0.165, 0.005, SHOZ-0.195), MPURP)
    wx, wz = sx*(0.165 + 0.20*math.sin(a)), (SHOZ-0.195) - 0.20*math.cos(a)
    add(f"kira_cuff_{nm}", cyl(6,0.034,0.024), (wx, 0.005, wz), MLIGHT)
    add(f"kira_glove_{nm}", box(0.044,0.052,0.078), (wx+sx*0.006, 0.005, wz-0.050), MGLOVE)

# neck + collar
add("kira_neck", cyl(6,0.038,0.08), (0,0.006,1.300), MDARK)
add("kira_collar", cyl(8,0.058,0.035), (0,0.006,1.255), MLIGHT)

# head: skin skull, tapered jaw, protrudes through hair window
bm = ball(10,8,1)
for v in bm.verts:
    v.co.x*=0.108; v.co.y*=0.125; v.co.z*=0.135
    if v.co.y < 0 and v.co.z < -0.05: v.co.x*=0.82
head = add("kira_head", bm, (0,0.005,HEADZ), MSKIN)
FACEY = 0.005 - 0.125   # skin front plane
EYEZ = HEADZ + 0.012

# hair: purple bob, WIDE face opening so skin reads as face
bm = ball(10,7,1)
for v in bm.verts:
    v.co.x*=0.138; v.co.y*=0.146; v.co.z*=0.162
    if v.co.z < -0.03: v.co.z *= 1.15
hair = add("kira_hair", bm, (0,0.018,HEADZ+0.012), MHAIR)
bm = bmesh.new(); bm.from_mesh(hair.data)
for f in list(bm.faces):
    c=f.calc_center_median()
    if c.y < -0.030 and abs(c.x) < 0.080 and c.z < 0.030:
        bm.faces.remove(f)
bm.to_mesh(hair.data); bm.free(); hair.data.update()
# fringe strip above brow (side-view silhouette)
add("kira_fringe", box(0.085,0.014,0.028), (0,FACEY+0.010,EYEZ+0.075), MHAIR)
# nape spikes: visible below helmet rim, behind neck (side-view identity)
add("kira_spike_c", cone(4,0.028,0.005,0.09, ax="X", ang=math.radians(115)), (0,0.130,1.395), MHAIR)
add("kira_spike_l", cone(4,0.024,0.005,0.08, ax="X", ang=math.radians(115)), (-0.062,0.122,1.402), MHAIR)
add("kira_spike_r", cone(4,0.024,0.005,0.08, ax="X", ang=math.radians(115)), (0.062,0.122,1.402), MHAIR)

# eyes: BIG anime style — white proud of skin, dark iris proud of white,
# highlight chip; brows thin dark; mouth tiny magenta smile strip
for sx in (-1,1):
    nm="l" if sx<0 else "r"
    add(f"kira_eye_{nm}", ball(8,6,0.034), (sx*0.046, FACEY-0.004, EYEZ), MEYE)
    add(f"kira_iris_{nm}", box(0.026,0.006,0.030), (sx*0.046, FACEY-0.030, EYEZ), MIRIS)
    add(f"kira_glint_{nm}", box(0.008,0.005,0.008), (sx*0.038, FACEY-0.034, EYEZ+0.010), MEYE)
    add(f"kira_brow_{nm}", box(0.040,0.006,0.006), (sx*0.048, FACEY-0.002, EYEZ+0.052), MHAIR)
add("kira_nose", cone(4,0.008,0.002,0.014, ax="X", ang=math.radians(-90)), (0, FACEY-0.010, EYEZ-0.048), MSKIN)
add("kira_mouth", box(0.024,0.005,0.005), (0, FACEY-0.004, EYEZ-0.092), MMAG)

# helmet: dome over skull, face window front-lower-center
hel = bpy.data.objects.new("kira_helmet", None)
bm = ball(12,8,0.170)
for v in bm.verts:
    if v.co.y > 0: v.co.y *= 0.94
    if v.co.z > 0.10: v.co.z *= 0.88
me = bpy.data.meshes.new("kira_helmet"); bm.to_mesh(me); bm.free()
hel = bpy.data.objects.new("kira_helmet", me)
sc.collection.objects.link(hel); hel.parent=root; hel.location=(0,0.008,HELMZ)
bm = bmesh.new(); bm.from_mesh(me)
for f in list(bm.faces):
    c=f.calc_center_median()
    if abs(c.x) < 0.072 and c.y < -0.090 and -0.150 < c.z < 0.010:
        bm.faces.remove(f)
bm.to_mesh(me); bm.free()
for p in me.polygons: p.use_smooth=False
me.update()
me.materials.append(MDARK)
# visor bar on brow line
add("kira_visor", box(0.140,0.018,0.026), (0,-0.150,HELMZ+0.030), MCYAN)
# earcups (X axis) + cyan rings
for sx in (-1,1):
    nm="l" if sx<0 else "r"
    add(f"kira_earcup_{nm}", cyl(8,0.070,0.045, ax="Y", ang=math.pi/2), (sx*0.158,0.006,HELMZ-0.045), MLIGHT)
    add(f"kira_earring_{nm}", cyl(8,0.046,0.050, ax="Y", ang=math.pi/2), (sx*0.166,0.006,HELMZ-0.045), MCYAN)
# helmet back fins
for sx in (-1,1):
    nm="l" if sx<0 else "r"
    bm=box(0.010,0.050,0.075); rym(bm, math.radians(28))
    add(f"kira_fin_{nm}", bm, (sx*0.072,0.150,HELMZ+0.080), MDARK)

tris = sum(sum(len(p.vertices)-2 for p in o.data.polygons)
           for o in sc.objects if o.name.startswith("kira_") and o.type=="MESH")

# studio lighting (reference turntable look): key/fill/rim + neutral bg
for nm, rotv, e, sz in (("kira_key",(50,0,-25),3.2,1.0),
                        ("kira_fill",(45,0,150),1.4,1.4),
                        ("kira_rim",(35,0,-90),2.0,1.0)):
    ld = bpy.data.lights.new(nm,"AREA"); ld.energy=e; ld.size=sz
    o = bpy.data.objects.new(nm, ld); sc.collection.objects.link(o)
    o.location=(0,-4,1.6); o.rotation_euler=[math.radians(a) for a in rotv]
w = sc.world or bpy.data.worlds.new("World"); sc.world = w; w.use_nodes=True
bg = next(n for n in w.node_tree.nodes if n.type=="BACKGROUND")
bg.inputs[0].default_value=(0.62,0.63,0.65,1.0); bg.inputs[1].default_value=1.0
sc.view_settings.view_transform = "Standard"
print("BUILD objects:", len([o for o in sc.objects if o.name.startswith("kira_")]), "tris:", tris)
bpy.ops.wm.save_as_mainfile(filepath="/home/danielschmid/dev/github/skillset/output/kira-pulse/kira-pulse.blend")
print("saved")
