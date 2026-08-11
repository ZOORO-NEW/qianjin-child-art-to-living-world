# 提示词库 · 童画活化

所有模板的第一句都是 **画风锁定约束**，务必保留。把 `<...>` 替换成实际内容。

---

## A. 整幅画 → 立体实景渲染（ImageGen 图生图，input_fidelity=0.85）

通用版（蜡笔/马克笔/水彩手绘）：

> Keep the child's exact art style — identical crayon/marker strokes, identical color palette, identical naive proportions and outlines, identical charm. Do NOT make it photorealistic. Turn this drawing into a charming 3D miniature diorama with real depth and gentle volumetric lighting, as if the paper drawing became a small tactile world you could pick up and rotate. Add only: soft rounded 3D volume, believable cast shadows, gentle ambient light, a subtle ground plane. Materials feel like the original medium (crayon = soft waxy, marker = flat bold, watercolor = soft). Keep every element in the same position and recognizable. Whimsical, warm, storybook mood.

照片 → 同风格 3D 小世界（当输入是照片时）：

> Keep the exact visual style, colors and mood of this photo. Transform it into a charming 3D miniature diorama / tiny world with real depth, soft rounded volume, gentle volumetric lighting and believable cast shadows, as if the scene became a small tactile model. Do NOT make it photorealistic or change the color palette. Warm, whimsical, storybook mood.

---

## B. 单主体 → 可旋转 3D 模型（图生3D，--generate-type LowPoly/Normal）

房子（童趣低面数）：

> A chibi / low-poly 3D model of the child's drawn house, preserving the child's crayon colors and chunky proportions, soft clay-and-papercraft look, clean white background, game-asset style, centered, full object visible.

动物（单只）：

> A chibi / low-poly 3D model of the child's drawn <cat>, preserving the exact crayon colors and round naive proportions from the drawing, soft clay/papercraft toy look, clean white background, game-asset style, centered, full body visible.

---

## C. 让动物「活过来」（VideoGen 图生视频，image=原图或渲染图）

单只动物：

> Gently bring this drawing to life. The <animal> slowly blinks, its ears/tail sway with a soft breeze, it breathes with a tiny rise and fall of the chest, and looks around with curiosity. CRITICAL: keep the exact childlike art style and colors of the original — it must look like the drawing itself came alive, not a photoreal animal. Add a slow dreamy camera drift to reveal gentle 3D depth. Soft warm lighting, whimsical children's-book mood. Smooth and tender, no sudden jumps.

negative_prompt: `photorealistic, realistic photo, deformed, extra limbs, jitter, flicker, style change, morph`

---

## D. 整幅世界活起来（VideoGen 图生视频，image=立体渲染图）

> Animate this child's drawing into a living storybook world. The <house> sits warmly with a wisp of smoke from the chimney, the <animal> blinks and sways, clouds drift across the sky, leaves rustle on the tree, the sun's rays shimmer. CRITICAL: keep the exact original art style — like the paper itself is breathing, not a realistic render. Slow parallax camera move to show depth. Warm, magical, gentle.

negative_prompt: `photorealistic, realistic photo, deformed, extra limbs, jitter, flicker, style change`

---

## E. 辅助：补色彩 / 去背景（ImageGen 图生图）

画面太淡、对比低，先补一下（input_fidelity=0.7）：

> Enhance this child's drawing: boost color saturation and line contrast slightly, keep the exact same art style, shapes and composition. Do not add new elements.

单主体抠图（为图生3D 准备干净背景）：

> Isolate the <house> from this drawing onto a clean plain white background, keep its exact art style and colors, remove everything else.
