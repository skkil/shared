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
| Blender via Python (`bpy`) in Claude Code, if installed | free | Turntables, product renders, baking, format conversion |
| Spline | free tier | Designer-editable scenes the user wants to tweak visually |

## 3. Image-to-3D pipeline

1. Concept image (generated or provided): one object, three-quarter view, even neutral light, no cast shadows,
   plain background, the whole object in frame. Key it (`post.py key`).
2. Plan and approve the 3D job (`media.py plan`), run, download the GLB.
3. Inspect: load in a quick R3F viewer or `npx @gltf-transform/cli inspect model.glb`. Check scale, pivot, normals, texture size.
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
