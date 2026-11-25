# 3D assets and scenes

## Contents
1. Is 3D the right medium?
2. Paths to a 3D asset
3. Image-to-3D pipeline
4. Look development (avoiding the default 3D look)
5. Optimization and delivery
6. 3D on native platforms and in video

## 1. Is 3D the right medium?

Use real-time 3D when the product is physical, when space is the metaphor (a world, a map, a machine), or when
direct manipulation is the signature moment. Otherwise a **3D-render-style image** gives the look at a fraction of
the cost, weight, and risk. Decide per surface; record it in DESIGN.md.

## 2. Paths

| Path | Cost | Best for |
|---|---|---|
| 3D-render-style image (GPT Image 2 / Nano Banana Pro) | ~$0.05-0.25 per image | Heroes, product shots, icons with depth; no interaction |
| Code-native 3D (three.js/R3F primitives, extrusions, procedural geometry, toon/matcap shaders) | free | Stylized objects, abstract product metaphors, data-driven scenes |
| Image → 3D (`fal-ai/trellis-2`, `fal-ai/hunyuan3d/v2`) | ~$0.16-0.30 per model | A specific object from an approved concept image |
| Retro Diffusion low-poly (rigged, animatable, pixel-textured) | $0.25-3 by size; free estimate | Characters, props and worlds in a low-poly/pixel direction |
| **Blender via `scripts/blender.py`** (Claude Code, Blender 4.2+) | free | Real modeling: products, props, architecture, exploded views, cleanup of generated models, turntables, hero renders. Full guide: blender.md |
| Spline | free tier | Designer-editable scenes the user wants to tweak visually |

### 2b. Procedural three.js (models written as code in the page)

No build step needed: pin `three@0.169.0` (or the project's version) through an import map.
- Collect real dimensions first and write them as metre constants; block out in boxes, then detail by kind.
- **Lathe** `[[r, y], ...]` for anything turned: columns, vases, knobs, wheels, domes.
- **Sweep** a 2D profile along a path (`ExtrudeGeometry` with `extrudePath`, or a custom mitred sweep) for trims,
  kerbs, handles, rails.
- **Kits:** define a part once, place it with matrices, one `InstancedMesh` per part; merge static parts with
  `BufferGeometryUtils.mergeGeometries`.
- **Textures drawn in code** (canvas + seeded RNG, or `draw.py` output) instead of downloaded images.
- Shader tweaks via `onBeforeCompile`; if you move vertices, patch `customDepthMaterial` too or shadows stay still.
- **Exploded views:** per part `userData = {stage, explode: [x, y, z]}`; `set(t)` from 0 (assembled) to 1;
  stage 0 moves first and each later stage starts when the previous is half done. Labels in two screen-edge
  columns with leader lines; x-ray shells at ~14% opacity with `depthWrite: false`; a clipping plane for sections.
  Product look: `RoomEnvironment` PMREM, `ShadowMaterial` floor, ACES, metals roughness 0.3-0.45, metalness 0.8-0.95.
- **Budget** (laptop GPU at 1440×900): < 10 ms/frame, < 300 draw calls, < 2M triangles. Expose
  `window.__app = {renderer}` so checks can read `renderer.info`. Quality tiers: high (DPR ≤ 2, GTAO, 4096
  shadows), balanced (DPR 1.5), fast (DPR 1, no AO, 2048 shadows); drop a tier when frame time is over budget.
- **Frame-accurate capture:** replace `performance.now`, `Date.now` and `requestAnimationFrame` with a virtual
  clock that advances 1/60 s per captured frame, so recordings never stutter (or render through `@remotion/three`).

## 3. Image-to-3D pipeline

1. Concept image (generated or provided): one object, three-quarter view, even neutral light, no cast shadows,
   plain background, the whole object in frame. Key it (`post.py key`).
2. Plan and approve the 3D job (`media.py plan`), run, download the GLB.
3. Inspect: `python scripts/blender.py inspect model.glb --name x` (renders + scale, pivot, normals, budget
   checks), or `npx @gltf-transform/cli inspect model.glb`. Clean up in Blender (blender.md §5).
4. Optimize (section 5), then light and frame it in the page's look (section 4).

## 4. Look development

The default 3D look (glossy plastic, gradient background, orbit controls, 75° FOV, floating, blue rim light) is a
tell. Instead:
- **Material language from the world**: matte clay, enamel, paper, frosted acrylic, pixel textures (nearest filtering), toon shading.
- **Camera**: narrower FOV (25-35°) reads like a product lens; fixed, purposeful angles; limit orbit to a small range or none.
- **Light**: one clear key direction that matches the page's illustrations; an environment map for reflections;
  grounded contact shadows (drei `ContactShadows`/`AccumulativeShadows`).
- **Ground**: the object sits on the page's ground color, not in a void.
- **Post-processing** sparingly: subtle grain or none; avoid default bloom.
- **Interaction**: one meaningful manipulation (turn it, open it, configure it), not orbit-for-its-own-sake.

## 5. Optimization and delivery

- `npx @gltf-transform/cli optimize in.glb out.glb --compress meshopt --texture-compress webp` (or draco/ktx2).
  Targets: hero model < 2-3 MB, textures 1-2k (pixel textures stay small with nearest filtering).
- R3F: `<Canvas dpr={[1, 2]}>`, `useGLTF` + `<Suspense>` with a poster fallback, lazy-mount after LCP,
  `frameloop="demand"` for static scenes, pause offscreen.
- Provide a static render (poster) for reduced motion, low-power devices, and social cards.

## 6. Native and video

- iOS/visionOS: convert to USDZ (Reality Converter or `usdzconvert`), RealityKit/SceneKit, AR Quick Look for "view in your room".
- Android: SceneView/Filament with GLB. Flutter: `model_viewer_plus` (web view) or emerging `flutter_scene`; keep 3D optional.
- Video: `@remotion/three` renders R3F scenes frame-accurately; drive camera and animation from `useCurrentFrame()`.
