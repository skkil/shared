#!/usr/bin/env python3
"""blender: model in Blender headlessly, render previews you can look at, check the mesh, export for the web.

  python scripts/blender.py run model.py --name lamp                 # build from a bpy script, render, check, export GLB
  python scripts/blender.py run model.py --name lamp --look clay     # matte clay previews for block-out review
  python scripts/blender.py inspect asset.glb --name robot           # import any GLB/glTF/OBJ/FBX/STL/.blend, render, check
  python scripts/blender.py turntable asset.glb --name robot --frames 48   # PNG frames + MP4 orbit
  python scripts/blender.py run model.py --name lamp --views front,three-quarter,top,side --size 1024 --samples 64

The model script is plain bpy run inside an empty scene. It builds geometry and materials and should leave the
camera and lights to this tool unless the look depends on them (then name a camera "Camera" and lights; they are
kept). Outputs go to .design/3d/<name>/: <view>.png, sheet.png, report.json, <name>.blend, <name>.glb.

Checks (warn, never block): triangle budget, real-world size (metres), pivot on the ground, unapplied scale or
rotation, non-manifold edges, missing UVs on textured meshes, oversized textures, objects without materials.
Requires Blender 4.2+ on PATH (or $BLENDER). Spends nothing.
"""
import argparse, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

DRIVER = r'''
import bpy, bmesh, json, math, sys
from mathutils import Vector

cfg = json.loads(sys.argv[sys.argv.index("--") + 1])
out = cfg["out"]

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def load_source(src):
    ext = src.rsplit(".", 1)[-1].lower()
    if ext == "py":
        code = open(src, encoding="utf-8").read()
        exec(compile(code, src, "exec"), {"__name__": "__main__", "bpy": bpy})
    elif ext == "blend":
        bpy.ops.wm.open_mainfile(filepath=src)
    elif ext in ("glb", "gltf"):
        bpy.ops.import_scene.gltf(filepath=src)
    elif ext == "obj":
        bpy.ops.wm.obj_import(filepath=src)
    elif ext == "fbx":
        bpy.ops.import_scene.fbx(filepath=src)
    elif ext == "stl":
        bpy.ops.wm.stl_import(filepath=src)
    else:
        raise SystemExit(f"unsupported source: {src}")

def meshes():
    return [o for o in bpy.context.scene.objects if o.type == "MESH" and o.visible_get()]

def world_bounds(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    if not pts:
        return Vector((0, 0, 0)), Vector((0, 0, 0))
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi

def stats(objs):
    dg = bpy.context.evaluated_depsgraph_get()
    tris, warns, per = 0, [], []
    for o in objs:
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        me.calc_loop_triangles()
        t = len(me.loop_triangles)
        bm = bmesh.new(); bm.from_mesh(me)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
        nonman = sum(1 for e in bm.edges if not e.is_manifold)
        bm.free()
        textured = any(n.type == "TEX_IMAGE" for s in o.material_slots if s.material and s.material.use_nodes for n in s.material.node_tree.nodes)
        if textured and not me.uv_layers:
            warns.append(f"{o.name}: textured but has no UV map")
        ev.to_mesh_clear()
        tris += t
        if any(abs(s - 1) > 1e-4 for s in o.scale):
            warns.append(f"{o.name}: unapplied scale {tuple(round(s, 3) for s in o.scale)} (apply before export)")
        if any(abs(r) > 1e-4 for r in o.rotation_euler) and o.parent is None:
            warns.append(f"{o.name}: unapplied rotation (apply unless it animates)")
        if nonman:
            warns.append(f"{o.name}: {nonman} non-manifold edges (holes or internal faces; fine for open shells, bad for 3D print and booleans)")
        if not any(s.material for s in o.material_slots):
            warns.append(f"{o.name}: no material")
        per.append({"name": o.name, "tris": t, "nonmanifold_edges": nonman})
    imgs = []
    for img in bpy.data.images:
        if img.size[0] and img.users:
            imgs.append({"name": img.name, "size": list(img.size)})
            if max(img.size) > cfg["max_texture"]:
                warns.append(f"texture {img.name} is {img.size[0]}x{img.size[1]} (web target <= {cfg['max_texture']})")
    lo, hi = world_bounds(objs)
    dims = hi - lo
    if tris > cfg["max_tris"]:
        warns.append(f"{tris} triangles exceeds budget {cfg['max_tris']} (decimate, bake detail into normals, or instance repeats)")
    if objs and abs(lo.z) > 0.01 * max(dims.z, 1e-6) + 1e-4:
        warns.append(f"lowest point is z={lo.z:.3f}, not on the ground (z=0)")
    if objs and (max(dims) > 500 or max(dims) < 0.005):
        warns.append(f"size {tuple(round(d, 3) for d in dims)} m looks wrong for real-world units")
    return {"triangles": tris, "objects": per, "dimensions_m": [round(d, 4) for d in dims],
            "bounds_min": [round(v, 4) for v in lo], "bounds_max": [round(v, 4) for v in hi],
            "textures": imgs, "materials": len([m for m in bpy.data.materials if m.users]), "warnings": warns}

def set_engine(scene):
    for e in cfg["engines"]:
        try:
            scene.render.engine = e
            return e
        except TypeError:
            continue
    return scene.render.engine

def clay():
    m = bpy.data.materials.new("rebecca-clay")
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (0.42, 0.40, 0.37, 1)
    b.inputs["Roughness"].default_value = 0.85
    for o in meshes():
        o.data.materials.clear(); o.data.materials.append(m)

def stage(objs):
    scene = bpy.context.scene
    lo, hi = world_bounds(objs)
    center = (lo + hi) / 2
    radius = max((hi - lo).length / 2, 0.01)
    if scene.world is None:
        scene.world = bpy.data.worlds.new("World")
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get("Background")
    g = cfg["ground_rgb"]
    bg.inputs[0].default_value = (*g, 1)
    bg.inputs[1].default_value = 1.0
    if not any(o.type == "LIGHT" for o in scene.objects):
        for name, kind, energy, loc, size in [("Key", "AREA", 900, (1.2, -1.4, 1.8), 1.5),
                                              ("Fill", "AREA", 250, (-1.6, -0.6, 0.9), 2.5),
                                              ("Rim", "AREA", 400, (-0.4, 1.6, 1.4), 1.0)]:
            ld = bpy.data.lights.new(name, kind); ld.energy = energy * radius * radius; ld.size = size * radius
            lo_ = bpy.data.objects.new(name, ld); scene.collection.objects.link(lo_)
            lo_.location = center + Vector(loc) * radius * 2.2
            lo_.rotation_euler = (center - lo_.location).to_track_quat("-Z", "Y").to_euler()
    if cfg["floor"] and not bpy.data.objects.get("rebecca-floor"):
        bpy.ops.mesh.primitive_plane_add(size=radius * 400, location=(center.x, center.y, lo.z))
        f = bpy.context.active_object; f.name = "rebecca-floor"
        fm = bpy.data.materials.new("rebecca-floor"); fm.use_nodes = True
        fb = fm.node_tree.nodes.get("Principled BSDF")
        fb.inputs["Base Color"].default_value = (*g, 1); fb.inputs["Roughness"].default_value = 1.0
        f.data.materials.append(fm)
    return center, radius

VIEWS = {"front": (0, -1, 0.12), "three-quarter": (0.62, -0.78, 0.42), "side": (1, 0, 0.12),
         "back": (0, 1, 0.12), "top": (0.0001, -0.0001, 1), "low": (0.5, -0.85, -0.05)}

def camera(center, radius):
    scene = bpy.context.scene
    cam = bpy.data.objects.get("Camera")
    if cam is None or cam.type != "CAMERA":
        cd = bpy.data.cameras.new("rebecca-cam")
        cam = bpy.data.objects.new("rebecca-cam", cd); scene.collection.objects.link(cam)
    cam.data.lens_unit = "FOV"; cam.data.angle = math.radians(cfg["fov"])
    cam.data.clip_start = radius / 100; cam.data.clip_end = radius * 200
    scene.camera = cam
    return cam

def aim(cam, center, radius, d):
    dist = radius / math.sin(cam.data.angle / 2) * 1.08
    v = Vector(d).normalized()
    cam.location = center + v * dist
    cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()

def render(path):
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)

reset()
load_source(cfg["source"])
scene = bpy.context.scene
objs = [o for o in meshes() if not o.name.startswith("rebecca-")]
report = stats(objs)
if cfg.get("blend"):
    bpy.ops.wm.save_as_mainfile(filepath=cfg["blend"])
if cfg.get("glb"):
    for o in scene.objects:
        o.select_set(o in objs or o.type == "EMPTY" or o.type == "ARMATURE")
    bpy.ops.export_scene.gltf(filepath=cfg["glb"], export_format="GLB", use_selection=True, export_apply=True)
if cfg["look"] == "clay":
    clay()
center, radius = stage(objs)
cam = camera(center, radius)
scene.render.resolution_x = scene.render.resolution_y = cfg["size"]
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = cfg["transparent"]
report["engine"] = set_engine(scene)
if hasattr(scene, "eevee") and hasattr(scene.eevee, "taa_render_samples"):
    scene.eevee.taa_render_samples = cfg["samples"]
if hasattr(scene, "cycles"):
    scene.cycles.samples = cfg["samples"]; scene.cycles.device = "CPU"
try:
    scene.view_settings.view_transform = "AgX"
except TypeError:
    pass
rendered = []
if cfg["turntable"]:
    n = cfg["turntable"]
    for i in range(n):
        a = 2 * math.pi * i / n
        aim(cam, center, radius, (math.sin(a) * 0.9, -math.cos(a) * 0.9, 0.35))
        p = f"{out}/turntable/f{i:04d}.png"; render(p); rendered.append(p)
else:
    keep = cam.name == "Camera"
    for v in cfg["views"]:
        if keep and v == "camera":
            p = f"{out}/camera.png"; render(p); rendered.append(p); continue
        aim(cam, center, radius, VIEWS.get(v, VIEWS["three-quarter"]))
        p = f"{out}/{v}.png"; render(p); rendered.append(p)
report["renders"] = rendered
json.dump(report, open(f"{out}/report.json", "w"), indent=2)
'''


def blender_bin():
    b = os.environ.get("BLENDER") or shutil.which("blender")
    if not b:
        sys.exit("Blender not found. Install Blender 4.2+ and put it on PATH, or set $BLENDER.")
    return b


def sheet(paths, dest):
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return None
    ims = [Image.open(p).convert("RGB") for p in paths if Path(p).exists()]
    if not ims:
        return None
    w, h = ims[0].size
    s = Image.new("RGB", (w * len(ims), h + 28), (250, 250, 248))
    d = ImageDraw.Draw(s)
    for i, (im, p) in enumerate(zip(ims, paths)):
        s.paste(im, (i * w, 28))
        d.text((i * w + 10, 8), Path(p).stem, fill=(30, 30, 30))
    s.save(dest)
    return dest


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    for c in ("run", "inspect", "turntable"):
        p = sp.add_parser(c)
        p.add_argument("source")
        p.add_argument("--name", required=True)
        p.add_argument("--out-root", default=".design/3d")
        p.add_argument("--views", default="front,three-quarter,top")
        p.add_argument("--size", type=int, default=768)
        p.add_argument("--samples", type=int, default=32)
        p.add_argument("--fov", type=float, default=30.0, help="degrees; 25-35 reads like a product lens")
        p.add_argument("--look", choices=["material", "clay"], default="material")
        p.add_argument("--ground", default="#efece6", help="ground/world color; use the page's ground token")
        p.add_argument("--no-floor", action="store_true")
        p.add_argument("--transparent", action="store_true")
        p.add_argument("--engine", choices=["eevee", "cycles", "workbench"], default="eevee")
        p.add_argument("--max-tris", type=int, default=100_000)
        p.add_argument("--max-texture", type=int, default=2048)
        p.add_argument("--no-export", action="store_true")
        p.add_argument("--timeout", type=int, default=900)
        if c == "turntable":
            p.add_argument("--frames", type=int, default=48)
            p.add_argument("--fps", type=int, default=24)
    a = ap.parse_args()
    src = Path(a.source).resolve()
    if not src.exists():
        sys.exit(f"not found: {src}")
    out = (Path(a.out_root) / a.name).resolve()
    out.mkdir(parents=True, exist_ok=True)
    order = {"eevee": ["BLENDER_EEVEE", "BLENDER_EEVEE_NEXT", "CYCLES"], "cycles": ["CYCLES"],
             "workbench": ["BLENDER_WORKBENCH"]}[a.engine]
    g = a.ground.lstrip("#")
    srgb = [int(g[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    ground = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]
    cfg = {"source": str(src), "out": str(out), "views": a.views.split(","), "size": a.size, "samples": a.samples,
           "fov": a.fov, "look": a.look, "ground_rgb": ground, "floor": not a.no_floor, "transparent": a.transparent,
           "engines": order, "max_tris": a.max_tris, "max_texture": a.max_texture,
           "turntable": a.frames if a.cmd == "turntable" else 0,
           "blend": None if src.suffix == ".blend" else str(out / f"{a.name}.blend"),
           "glb": None if a.no_export else str(out / f"{a.name}.glb")}
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(DRIVER)
        driver = f.name
    cmd = [blender_bin(), "-b", "--factory-startup", "--python-exit-code", "1", "-P", driver, "--", json.dumps(cfg)]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=a.timeout)
    finally:
        os.unlink(driver)
    if r.returncode != 0 or not (out / "report.json").exists():
        tail = "\n".join((r.stdout + r.stderr).splitlines()[-30:])
        sys.exit(f"Blender failed (exit {r.returncode}). Last output:\n{tail}")
    rep = json.loads((out / "report.json").read_text())
    if a.cmd == "turntable":
        if shutil.which("ffmpeg"):
            mp4 = out / f"{a.name}-turntable.mp4"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(a.fps), "-i",
                            str(out / "turntable" / "f%04d.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                            "-crf", "18", "-movflags", "+faststart", str(mp4)], check=False)
            print(f"turntable: {mp4}")
    else:
        s = sheet(rep["renders"], out / "sheet.png")
        if s:
            print(f"sheet: {s}  (open it and look before judging)")
    print(f"engine {rep['engine']} | {rep['triangles']} tris | {rep['dimensions_m']} m | {rep['materials']} materials")
    for p in (cfg["glb"], cfg["blend"]):
        if p and Path(p).exists():
            print(f"saved: {p}")
    for w in rep["warnings"]:
        print(f"WARN  {w}")
    print(f"report: {out / 'report.json'}")


if __name__ == "__main__":
    main()
