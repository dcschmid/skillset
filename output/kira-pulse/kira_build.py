# Kira Pulse low-poly driver - faces -Y (project convention), Z-up, meters.
# CONNECTED GEOMETRY RULE: every part overlaps its neighbour by >=8mm.
# Head = concentric shells on ONE center: skull(13mm) < hair(12mm) < helmet(14mm);
# windows narrow outward so hair never plugs the helmet window.
# Run: blender -b --python kira_build.py
import bpy, bmesh, math
from mathutils import Matrix

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for m in list(bpy.data.meshes):
    bpy.data.meshes.remove(m)

sc = bpy.context.scene

def mat(name, rgb, rough=0.5):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1.0)
    b.inputs["Roughness"].default_value = rough
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
MEYE   = mat("kira_eye", (0.92,0.92,0.95), 0.35)

root = bpy.data.objects.new("kira_root", None)
sc.collection.objects.link(root)

def add(name, bm, loc, material, rot=(0.0,0.0,0.0)):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = False
    me.update()
    o = bpy.data.objects.new(name, me)
    sc.collection.objects.link(o)
    o.parent = root
    o.location = loc
    o.rotation_euler = rot
    me.materials.append(material)
    return o

def box(*s):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co.x*=s[0]; v.co.y*=s[1]; v.co.z*=s[2]
    return bm
def ball(u, v, r):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=r); return bm
def cone(seg, r1, r2, d):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r1, radius2=r2, depth=d)
    return bm
def cyl(seg, r, d):
    return cone(seg, r, r, d)
def rz(bm, a): bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(a,3,"Z"), verts=bm.verts[:])
def ry(bm, a):  bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(a,3,"Y"), verts=bm.verts[:])
def rx(bm, a):  bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(a,3,"X"), verts=bm.verts[:])

# ================= SKELETON (feet 0, -Y facing) =================
ANK,KNEE,HIP,SHLDR = 0.09,0.50,0.870,1.250
HEADC = 1.530                      # head cluster center (all shells share it)
# head top ~1.745 -> head share 24% of 1.745 (stylized big head, ref-consistent)

# ---- legs into torso (top 0.90 inside torso 0.87..1.25), boots around ankles ----
for sx in (-1,1):
    nm="l" if sx<0 else "r"
    add(f"kira_leg_{nm}", cyl(6,0.055,0.81), (sx*0.075,0.005,0.495), MDARK)
    add(f"kira_knee_{nm}", box(0.055,0.050,0.062), (sx*0.075,-0.046,KNEE+0.005), MLIGHT)
    bm=box(0.012,0.030,0.150); rz(bm, math.radians(6*sx))
    add(f"kira_thighmag_{nm}", bm, (sx*0.126,-0.012,KNEE+0.150), MMAG)   # half in leg shell
    bm=box(0.012,0.026,0.160); rz(bm, math.radians(9*sx))
    add(f"kira_thighcy_{nm}",  bm, (sx*0.126, 0.012,KNEE+0.020), MCYAN)
    add(f"kira_boot_{nm}", box(0.072,0.150,0.095), (sx*0.075,-0.020,0.050), MDARK)
    bm=ball(6,4,1)
    for v in bm.verts: v.co.x*=0.040; v.co.y*=0.040; v.co.z*=0.060
    add(f"kira_calf_{nm}", bm, (sx*0.075,0.055,0.30), MDARK)  # top 0.0975 in leg
    add(f"kira_toe_{nm}",  box(0.058,0.050,0.036), (sx*0.075,-0.105,0.030), MCYAN)  # in boot front

# ---- torso: single connected mass 0.870..1.255 (ref: waist < head-half width) ----
bm=bmesh.new(); bmesh.ops.create_cube(bm,size=1.0)
bmesh.ops.subdivide_edges(bm,edges=bm.edges[:],cuts=3,use_grid_fill=True)
for v in bm.verts:
    z=v.co.z+0.5; wz=0.870+z*0.385
    if wz<0.96: w=0.42          # hips  (x half 0.21)
    elif wz<1.04: w=0.31        # waist (0.155, narrower than head)
    elif wz<1.17: w=0.46        # chest (0.23)
    else: w=0.40                # shoulders (0.20)
    v.co.x*=w; v.co.y*=(0.160 if wz<0.96 else 0.125 if wz<1.04 else 0.150 if wz<1.17 else 0.130); v.co.z*=0.385
TORSO_F = 0.005-0.115            # flat chest plane
add("kira_torso", bm, (0,0.005,1.0625), MDARK)
add("kira_belt", box(0.19,0.150,0.055), (0,0.005,HIP+0.015), MDARK)
add("kira_buckle", box(0.030,0.016,0.028), (0,TORSO_F-0.008,HIP+0.015), MCYAN)
bm=box(0.060,0.020,0.105); ry(bm, math.radians(10)); rz(bm, math.radians(20))
add("kira_gem_cyan", bm, (-0.040,TORSO_F-0.006,1.125), MCYAN)          # 8mm embedded
bm=box(0.042,0.020,0.125); ry(bm, math.radians(10)); rz(bm, math.radians(-16))
add("kira_gem_mag",  bm, ( 0.045,TORSO_F-0.006,1.120), MMAG)

# ---- arms: clear A-pose 40deg, chain overlaps, hands OUTSIDE torso (0.20) ----
A=math.radians(40)
for sx in (-1,1):
    nm="l" if sx<0 else "r"
    sb=ball(6,4,1)
    for v in sb.verts: v.co.x*=0.090; v.co.y*=0.090; v.co.z*=0.090
    add(f"kira_shoulder_{nm}", sb, (sx*0.170,0.005,SHLDR+0.005), MLIGHT)  # 3cm in torso edge
    def at(t): return (sx*(0.170+t*math.sin(A)), 0.005, SHLDR+0.005-t*math.cos(A))
    bm=cyl(6,0.028,0.44); ry(bm,-A*sx)
    add(f"kira_arm_{nm}", bm, at(0.215), MPURP)           # spans 0..0.44 in shoulder ball
    bm=cyl(6,0.034,0.026); ry(bm,-A*sx)
    add(f"kira_cuff_{nm}", bm, at(0.437), MLIGHT)         # overlaps sleeve end 0.43
    bm=box(0.042,0.052,0.080); ry(bm,-A*sx)
    add(f"kira_glove_{nm}", bm, at(0.478), MGLOVE)        # starts inside cuff

# ---- neck (in torso AND skull) + collar ----
add("kira_neck", cyl(6,0.036,0.16), (0,0.006,1.330), MDARK)             # 1.250..1.410
add("kira_collar", cyl(8,0.055,0.040), (0,0.006,SHLDR+0.015), MLIGHT)   # on torso top

# ====== HEAD: concentric half-axes (SEMM) @ HEADC=1.530, big stylized head ======
# skull 115/135/150  hair 130/150/162  helmet 160/150/162  (y+0.010 all)
SKULL_F = 0.010-0.135
bm=ball(10,8,1)
for v in bm.verts:
    v.co.x*=0.115; v.co.y*=0.135; v.co.z*=0.150
    if v.co.y<0 and v.co.z<-0.06: v.co.x*=0.84
add("kira_head", bm, (0,0.010,HEADC), MSKIN)

bm=ball(10,7,1)
for v in bm.verts:
    v.co.x*=0.130; v.co.y*=0.150; v.co.z*=0.162
    if v.co.z<-0.05: v.co.z*=1.05
hair=add("kira_hair", bm, (0,0.010,HEADC), MHAIR)
bm=bmesh.new(); bm.from_mesh(hair.data)
for f in list(bm.faces):
    c=f.calc_center_median()
    if c.y<-0.035 and abs(c.x)<0.070 and c.z<0.020:
        bm.faces.remove(f)
bm.to_mesh(hair.data); bm.free(); hair.data.update()

hel=add("kira_helmet", ball(12,8,1), (0,0.010,HEADC), MDARK)
for v in hel.data.vertices:
    v.co.x*=0.160; v.co.y*=0.150; v.co.z*=0.162
    if v.co.z>0.10: v.co.z*=0.90
bm=bmesh.new(); bm.from_mesh(hel.data)
for f in list(bm.faces):
    c=f.calc_center_median()
    if abs(c.x)<0.062 and c.y<-0.080 and c.z<0.010:
        bm.faces.remove(f)
bm.to_mesh(hel.data); bm.free(); hel.data.update()

# fringe across helmet-window top, overlaps hair front (connected shell)
add("kira_fringe", box(0.120,0.030,0.040), (0,-0.138,HEADC+0.085), MHAIR)
# nape spikes: base in hair back shell (y 0.150), tips below helmet rim
bm=cone(4,0.055,0.010,0.110); rx(bm,math.radians(112))
add("kira_spike_c", bm, (0,0.135,HEADC-0.140), MHAIR)
bm=cone(4,0.048,0.008,0.095); rx(bm,math.radians(112))
add("kira_spike_l", bm, (-0.075,0.128,HEADC-0.130), MHAIR)
bm=cone(4,0.048,0.008,0.095); rx(bm,math.radians(112))
add("kira_spike_r", bm, ( 0.075,0.128,HEADC-0.130), MHAIR)

# visor band across window top (over fringe), width = helmet window 124mm
add("kira_visor", box(0.124,0.026,0.028), (0,-0.150,HEADC+0.105), MCYAN)
# earcups: from hair side (130) through helmet side (150) -> cup 138..190
for sx in (-1,1):
    nm="l" if sx<0 else "r"
    bm=cyl(8,0.052,0.052); ry(bm,math.pi/2)
    add(f"kira_earcup_{nm}", bm, (sx*0.164,0.010,HEADC-0.035), MLIGHT)
    bm=cyl(8,0.056,0.058); ry(bm,math.pi/2)
    add(f"kira_earring_{nm}", bm, (sx*0.168,0.010,HEADC-0.035), MCYAN)

# ---- FACE ROUND 2: boolean eye sockets in the skull, recessed iris ----
# anime eye = dark socket rim (lid liner) + amber iris 8mm BEHIND skin plane
EYEZ=HEADC-0.022
head_obj=bpy.data.objects["kira_head"]
head_obj.data.materials.append(MDARK)          # slot 1 = socket walls
cutters=[]
for sx in (-1,1):
    nm="l" if sx<0 else "r"
    ex, ey = sx*0.050, SKULL_F+0.006
    # socket cutter: vertical-ellipse cylinder along Y, open front at skin-25mm
    cut=cyl(10,0.034,0.075); rx(cut,math.pi/2)
    for v in cut.verts: v.co.x*=0.88           # vertical ellipse (anime)
    co=add(f"kira_cut_{nm}", cut, (ex,SKULL_F-0.012,EYEZ), MEYE)
    cutters.append((nm,co))
bpy.ops.object.select_all(action="DESELECT")
for nm,co in cutters:
    head_obj=bpy.data.objects["kira_head"]
    bpy.context.view_layer.objects.active=head_obj
    mod=head_obj.modifiers.new("bool","BOOLEAN"); mod.operation="DIFFERENCE"
    mod.object=co; mod.solver='EXACT'
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(co,do_unlink=True)
# mark socket cavity: walls/back face NOT frontward, inside ellipse window
me=bpy.data.objects["kira_head"].data
lz=EYEZ-HEADC
for p in me.polygons:
    if p.normal.y>-0.5 and abs(p.center.x)<0.095 and abs(p.center.z-lz)<0.052 \
       and p.center.y<-0.100:
        p.material_index=1
for sx in (-1,1):
    nm="l" if sx<0 else "r"
    ex, ey = sx*0.050, SKULL_F+0.006
    disc=cyl(10,0.028,0.010); rx(disc,math.pi/2)
    add(f"kira_iris_{nm}", disc, (sx*0.050,SKULL_F-0.006,EYEZ), MIRIS)
    pup=cyl(8,0.012,0.010); rx(pup,math.pi/2)
    add(f"kira_pupil_{nm}", pup, (sx*0.050,SKULL_F-0.013,EYEZ), MDARK)
    gl=cyl(6,0.005,0.008); rx(gl,math.pi/2)
    add(f"kira_glint_{nm}", gl, (sx*0.044,SKULL_F-0.018,EYEZ+0.014), MEYE)
    add(f"kira_brow_{nm}", box(0.044,0.010,0.008), (sx*0.052,ey-0.014,EYEZ+0.075), MHAIR)
    # side hair locks framing the cheeks (overlap hair shell + face edge)
    lock=box(0.020,0.030,0.075)
    add(f"kira_lock_{nm}", lock, (sx*0.108,-0.098,EYEZ-0.030), MHAIR)
add("kira_mouth", box(0.028,0.010,0.008), (0,SKULL_F-0.001,EYEZ-0.098), MMAG)
add("kira_lip", box(0.020,0.008,0.005), (0,SKULL_F-0.005,EYEZ-0.110), MLIGHT)
bm=cone(4,0.011,0.002,0.022); rx(bm,math.radians(90))
add("kira_nose", bm, (0,SKULL_F-0.004,EYEZ-0.052), MSKIN)
for sx in (-1,1):
    bm=cone(6,0.055,0.005,0.030); rx(bm,math.radians(-90))
    add(f"kira_bust_{'l' if sx<0 else 'r'}", bm, (sx*0.055,TORSO_F-0.012,1.150), MDARK)
    # flank facet strips: angled light plates catching rim light (armor chamfer)
    f=box(0.008,0.060,0.150)
    add(f"kira_flank_{'l' if sx<0 else 'r'}", f, (sx*0.205,0.010,1.100), MDARK)

# ================= presentation =================
for nm,rotv,e,sz in (("kira_key",(50,0,-25),3.2,1.0),
                     ("kira_fill",(45,0,150),1.4,1.4),
                     ("kira_rim",(35,0,-90),2.0,1.0)):
    ld=bpy.data.lights.new(nm,"AREA"); ld.energy=e; ld.size=sz
    o=bpy.data.objects.new(nm,ld); sc.collection.objects.link(o)
    o.location=(0,-4,1.6); o.rotation_euler=[math.radians(a) for a in rotv]
w=sc.world or bpy.data.worlds.new("World"); sc.world=w; w.use_nodes=True
bg=next(n for n in w.node_tree.nodes if n.type=="BACKGROUND")
bg.inputs[0].default_value=(0.62,0.63,0.65,1.0); bg.inputs[1].default_value=1.0
sc.view_settings.view_transform="Standard"

tris=sum(sum(len(p.vertices)-2 for p in o.data.polygons)
         for o in sc.objects if o.name.startswith("kira_") and o.type=="MESH")
print("BUILD objects:",len([o for o in sc.objects if o.name.startswith("kira_")]),"tris:",tris)
bpy.ops.wm.save_as_mainfile(filepath="/home/danielschmid/dev/github/skillset/output/kira-pulse/kira-pulse.blend")
print("saved")
