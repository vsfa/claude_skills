# GPT-Image-1.5 Prompting Guide

Source: OpenAI Cookbook — Image Generation 1.5 Prompting Guide

---

## Prompt Structure

Organize prompts consistently:
**background/scene → subject → key details → constraints**

Use labeled segments or line breaks for complex requests rather than a single paragraph. Include the intended use case (ad, UI mock, infographic) to establish the appropriate polish level.

---

## Specificity & Quality Cues

- Be concrete about materials, shapes, textures, and visual medium (photo, watercolor, 3D render)
- Add targeted quality indicators sparingly — for photorealism, camera terminology (lens type, aperture feel, lighting style) steers results more effectively than generic phrases like "8K/ultra-detailed"

---

## Composition Control

- Specify framing and viewpoint: close-up, wide, top-down
- Name perspective and angle: eye-level, low-angle
- Describe lighting and mood: soft diffuse, golden hour, high-contrast
- Call out placement when layout matters: "logo top-right," "subject centered with negative space on left"

---

## Constraints (What to Preserve vs. Change)

- State what to exclude explicitly: "no watermark," "no extra text," "no logos/trademarks"
- For edits, use formulas like "change only X" + "keep everything else the same"
- Repeat preserve lists across iterations to minimize drift

---

## Text Rendering

- Put literal text in **quotes** or ALL CAPS
- Specify typography: font style, size, color, placement
- For difficult spellings or brand names, spell them letter-by-letter for improved accuracy

---

## Multi-Image Inputs

- Reference each input by index and description
- Describe interaction: "apply Image 2's style to Image 1"
- For compositing, be explicit: "put the bird from Image 1 on the elephant in Image 2"

---

## Iterative Refinement

- Start with clean base prompts, then refine with single-change follow-ups ("make lighting warmer," "remove the extra tree")
- Reuse context references but re-specify critical details if drift appears

---

## Quality & Latency Tradeoffs

- For latency-sensitive cases, test `quality="low"` first — often sufficient with faster generation
- Use `quality="high"` for dense layouts, heavy text, or detail-critical work

---

## Photorealism Best Practices

- Prompt as if capturing a real photo "in the moment"
- Use photography language: lens, lighting, framing
- Request real texture: pores, wrinkles, fabric wear, imperfections
- Avoid studio-polish language; favor "honest and unposed" framing with "everyday detail"

---

## Identity & Fidelity Preservation

- For edits involving people, explicitly lock facial features, body shape, pose, and expression
- Use `input_fidelity="high"` when larger scene changes accompany identity-critical edits
- Restate preservation constraints on each iteration

---

## Examples of Prompt Transformations

**Weak:** "a fox in the snow"

**Strong:** "Wide shot of a red fox sitting still in a snowy pine forest, golden late-afternoon light filtering through the trees, soft shadows on the snow, shallow depth of field, photorealistic, no text, no watermark"

---

**Weak:** "a product photo of a bottle"

**Strong:** "Studio product photo of a matte black glass bottle on a white background, soft diffuse overhead lighting, subtle shadow below the bottle, centered composition with negative space on both sides, no labels, no watermark, photorealistic"