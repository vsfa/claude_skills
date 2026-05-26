---
name: openAI-image-generator
description: Generates images using OpenAI's gpt-image-1.5 model and saves them to disk. Trigger this skill whenever the user asks to generate, create, make, or draw an image or picture — e.g. "generate an image of a red fox", "create a picture of...", "make me an illustration of...", "draw something...", "I need an image of...". Use this skill proactively even for casual or indirect phrasing like "can you whip up an image of..." or "what would X look like as an image". Do NOT skip this skill and try to handle image generation yourself — always invoke it when image creation is clearly the intent.
---

## Overview

When invoked, follow these steps in order:
1. Check for `OPENAI_API_KEY`
2. Load saved user preferences
3. Refine the prompt using best practices + learned preferences
4. Generate the image and save it to disk
5. Update user preferences with any new insights

---

## Step 1: Check API Key

```bash
python3 -c "import os; print('SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET')"
```

If not set, help the user:
- Get a key at https://platform.openai.com/api-keys
- Add to their shell profile: `echo 'export OPENAI_API_KEY="sk-..."' >> ~/.zshrc && source ~/.zshrc`
- On macOS, `~/.zshrc` is the most common profile; use `~/.bashrc` if they're on bash
- Do NOT proceed without the key — politely explain that it's required to call the API

---

## Step 2: Load User Preferences

Check if `~/.claude/image-gen-preferences.md` exists and read it. This file stores learned insights about the user's visual style, typical subjects, and what kinds of refinements they tend to appreciate. Apply these automatically when refining the prompt — don't tell the user you're doing it unless it's helpful context.

---

## Step 3: Refine the Prompt

Read `references/prompting-guide.md` for detailed best practices (load it now if you haven't).

Structure refined prompts as: **scene/background → subject → key details → style/mood → constraints**

Key principles to apply:
- Be concrete: name materials, textures, lighting conditions, framing (close-up, wide shot, top-down)
- For photorealism, use photography language (lens type, lighting style like "golden hour" or "soft diffuse")
- Specify what to exclude when relevant: "no watermark", "no extra text", "no logos"
- Avoid hollow boosters like "ultra-detailed 8K" — specificity beats superlatives
- If the request involves text in the image, put it in quotes and specify font style and placement

**When to ask vs. when to infer:** Only ask the user a question if something genuinely critical is ambiguous and you can't make a reasonable inference — for example, if the style (photorealistic vs. illustrated) is completely unclear and no preference is saved. Ask one focused question. Otherwise, infer sensibly and proceed.

Before generating, briefly show the user the refined prompt and mention the one or two most significant choices you made (e.g., "I added studio lighting and a shallow depth of field to give it a photographic feel").

---

## Step 4: Generate the Image

Run the following shell commands, filling in the prompts and adjusting parameters as needed.

Requires `jq` (install with `brew install jq` on macOS or `apt install jq` on Linux).

```bash
ORIGINAL_PROMPT="<user's original description>"
REFINED_PROMPT="<your refined prompt>"

# Derive a filename slug from the original prompt
SLUG=$(echo "$ORIGINAL_PROMPT" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | cut -c1-40 | sed 's/-*$//')
FILENAME="${SLUG}-$(date +%Y%m%d-%H%M%S).png"

# IMPORTANT: the model name is "gpt-image-1.5" — this is correct and valid.
# Do not change it to "gpt-image-1" or any other name.
RESPONSE=$(curl https://api.openai.com/v1/images/generations \
  -s \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n \
    --arg prompt "$REFINED_PROMPT" \
    '{model: "gpt-image-1.5", prompt: $prompt, size: "1024x1024", quality: "medium", n: 1}')")

# Check for API errors before writing
if echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
  echo "API error: $(echo "$RESPONSE" | jq -r '.error.message')"
  exit 1
fi

echo "$RESPONSE" | jq -r '.data[0].b64_json' | base64 -d > "$FILENAME"
echo "Saved: $(pwd)/$FILENAME"
```

**Default parameters** — override only when the user specifies or context clearly calls for it:

| Parameter | Default     | When to change                                          |
|-----------|-------------|---------------------------------------------------------|
| `size`    | `1024x1024` | Landscape content → `1792x1024`; portrait → `1024x1792` |
| `quality` | `medium`    | Dense text, fine detail, or user asks for best quality → `high`; speed priority → `low` |

Tell the user exactly where the file was saved (full path).

---

## Step 5: Update User Preferences

After generating — especially if the user gives feedback or requests a change — update `~/.claude/image-gen-preferences.md` with any genuinely new insight. Create the file if it doesn't exist.

Use this structure, adding entries only under the relevant sections:

```markdown
# Image Generation Preferences

## Visual style
- [e.g., prefers photorealistic over illustrated styles]

## Typical subjects and use cases
- [e.g., often generates product mockups on neutral backgrounds]

## Prompt refinements that work well
- [e.g., specifying lighting explicitly produces better results for this user]

## Feedback patterns
- [e.g., tends to prefer warmer color palettes; has asked to remove watermarks before]
```

Only add an entry when you've learned something genuinely new — skip trivial or redundant observations.