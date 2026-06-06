# Mask 局部重绘 / Inpainting

> 用 PNG alpha mask 控制"哪些区域重生成"。不透明=保留,透明=重画。
> 注意: gpt-image 系列的 mask 控制不是 100% 精确,主体边缘要求高时配合 prompt 兜底。

> mask 文件生成:用 PIL / OpenCV / 任何图像工具都行。**必须是 .png 文件**
> (edit.py 会校验扩展名)。alpha 通道 = 0~255 的不透明度。

## I1 · 换天空
**size**: `landscape`  ·  **quality**: `high`

```
Replace the sky (the transparent region of the mask) with a vivid
aurora borealis: green and purple ribbons, scattered stars, deep navy
at the top fading to a soft horizon glow. Keep the foreground
(ground, trees, lake, mountain reflection) exactly the same. Match
the new sky's light color subtly on the foreground highlights, but
do not change the foreground composition.
```

## I2 · 换地板材质
**size**: `square`  ·  **quality**: `high`

```
Replace the floor (transparent region) with polished dark marble:
deep gray base with subtle white veining, realistic reflections of
the surrounding furniture, glossy surface. Keep the walls, the
furniture, the lighting direction, and the camera angle exactly
the same.
```

## I3 · 修补/去除物体
**size**: `1k`  ·  **quality**: `high`

```
In the masked region (around the trash can on the sidewalk), extend
the surrounding sidewalk texture naturally: same concrete color,
same weathering pattern, same shadow direction, no new objects, no
visible seam. Keep everything outside the mask exactly the same.
```

## I4 · 换衣服某一部分
**size**: `portrait`  ·  **quality**: `high`

```
Change only the mask region (the shirt area) to a navy blue linen
shirt with rolled-up sleeves, visible fabric texture, natural folds.
Keep the person's face, hair, pose, background, and the rest of the
outfit (pants, shoes, accessories) exactly the same.
```

## I5 · 换脸表情
**size**: `portrait`  ·  **quality**: `high`

```
Change only the mask region (the face) to a smiling expression: warm
natural smile showing slight teeth, eyes slightly crinkled at the
corners, relaxed forehead. Keep the hairstyle, head angle, body
pose, clothing, background, and lighting exactly the same. Do not
change the person's identity, age, or apparent ethnicity.
```

## I6 · 文字区域替换
**size**: `landscape`  ·  **quality**: `high`

```
Replace only the text in the masked region with EXACT TEXT: "SALE 50% OFF"
in the same large bold sans-serif white font, same size and color as
the original text. Keep the rest of the poster — the imagery, the
background, the supporting text, and the layout — exactly the same.
```

## I7 · 提亮/降亮局部
**size**: `landscape`  ·  **quality**: `high`

```
In the masked region (the underexposed foreground), add natural
fill light: brighten the subjects as if a soft reflector were held
just out of frame from camera left, matching the existing ambient
direction. Do not introduce new objects, do not change the
background, keep skin tones natural.
```
