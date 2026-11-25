# Modeling in Blender

Blender runs headless from Claude Code through `scripts/blender.py`. You write a bpy script, the tool builds it in
an empty scene, renders previews you look at, checks the mesh, and exports a GLB and a .blend. Free and local.
Check availability first: `blender --version` (4.2+). Not available in Chat or Design (environments.md).

## 1. When to model, when not to

| Subject | Route |
|---|---|
| Products, devices, furniture, architecture, packaging, icons with depth, mechanical parts | **Model in Blender** (hard-surface: primitives, booleans, bevels, modifiers) |
| Stylized props and low-poly worlds | Model in Blender, or Retro Diffusion low-poly when it must be pixel-textured and rigged |
| Abstract metaphors, data-driven scenes, anything the page animates live | Procedural three.js in the page (three-d.md §2b) |
| Organic characters, creatures, sculpted faces | Generate (image → 3D, spend protocol), then **clean up in Blender** (§5) |
| A hero image with depth and no interaction | 3D-render-style image, or a Blender render (free, and exact) |

## 2. The loop (with gates)

1. **Reference and dimensions.** Collect real measurements (or the product's own CAD/photos). Write them as metre
   constants at the top of the script. A desk lamp base is ~0.18 m, not 2.
2. **Block-out.** Primitives only, correct proportions, no detail. `blender.py run model.py --name x --look clay`.
   **Gate:** show the clay sheet (front, three-quarter, top) before detailing. Proportion is 80% of the result.
3. **Refine.** Bevels on every hard edge (real objects have no knife edges), booleans for cut-outs, solidify for
   shells, arrays and mirrors for repeats, subdivision only where surfaces must read smooth.
4. **Materials** from the world in DESIGN.md: matte enamel, anodized metal, paper, frosted acrylic. Name them.
5. **Look and render.** Ground color = the page's ground token (`--ground "#hex"`), FOV 25-35°, one key light
   direction that matches the illustrations. Render, open `sheet.png`, compare against the reference, fix the worst
   difference, re-run. Stop at the critic bar (critique-qa.md) or after 3 rounds.
6. **Export** GLB (automatic), optimize with gltf-transform (three-d.md §5), check it loads in the page.

## 3. Script recipes

```python
import bpy, math

M = 1.0
BASE_R, BASE_H, STEM_H = 0.09 * M, 0.02 * M, 0.32 * M

def material(name, rgb, rough=0.5, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m

def finish(o, bevel=0.003):
    b = o.modifiers.new("bevel", "BEVEL"); b.width = bevel; b.segments = 3; b.limit_method = "ANGLE"
    o.modifiers.new("normals", "WEIGHTED_NORMAL")
    bpy.ops.object.shade_smooth()

bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=BASE_R, depth=BASE_H, location=(0, 0, BASE_H / 2))
base = bpy.context.active_object; base.name = "base"; finish(base)
```

- **Booleans:** `mod = obj.modifiers.new("cut", "BOOLEAN"); mod.operation = "DIFFERENCE"; mod.object = cutter;
  cutter.hide_render = True; cutter.display_type = "WIRE"`. Bevel after the boolean in the stack.
- **Lathe (vases, knobs, bottles):** a profile curve + Screw modifier (`angle=2π`, `steps=64`), or bmesh spin.
- **Sweep (handles, cables, trims):** a bezier curve with `bevel_depth` or a profile object as `bevel_object`.
- **Repeats:** Array modifier (+ Curve modifier to follow a path); instance collections for hundreds of copies.
- **Exploded views:** build each part as its own object with origin at its assembly point; store
  `obj["explode"] = (x, y, z)` and keyframe location from 0 to that offset, staged parts first.
- **Text:** `bpy.ops.object.text_add()` then convert to mesh; real fonts via `bpy.data.fonts.load(path)`.
- **Rigging (simple):** armature + automatic weights for mechanical hinges; keyframe rotations; GLB keeps actions.
- Keep the object on the ground (lowest point z = 0), apply scale and rotation before export
  (`bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)`), one material per look.

## 4. Reading the report

`blender.py` warns (never blocks) on: triangle budget (default 100k; hero web model target < 50k after decimate),
real-world size, pivot off the ground, unapplied scale or rotation, non-manifold edges (fine for open shells,
bad for printing and booleans), textured meshes without UVs, textures over 2048 px, objects without materials.
Fix what matters for the target: web, print, game engine or still render.

## 5. Cleaning up generated or downloaded models

`blender.py inspect model.glb --name x` first. Then a cleanup script that opens the file and:
merge by distance, recalculate normals, Decimate (ratio to hit the budget), set origin to bottom center and move to
z = 0, scale to real size, apply transforms, Weld + Smooth by Angle, replace generated materials with the DESIGN.md
materials, bake detail to a normal map if the high-poly look must survive decimation. Re-inspect, then export.

## 6. Turntables, stills and video

- `blender.py turntable model.glb --name x --frames 72` renders an orbit and an MP4; check it with
  `video_check.py --sheet 8`.
- Hero still: own camera named `Camera` in the script plus `--views camera` (kept as is), `--size 2048`,
  `--samples 128`, `--transparent` to composite onto the page ground in post.py.
- Poster frames for reduced motion and social cards come from the same scene, so the 3D and the stills match.

## 7. Optional: live Blender over MCP

A Blender MCP server (for example `blender-mcp`) lets you drive an open Blender interactively. It needs the user to
run Blender with the add-on and approve the connector; the script route above is the default because it is
reproducible, reviewable in git, and runs without a window.
