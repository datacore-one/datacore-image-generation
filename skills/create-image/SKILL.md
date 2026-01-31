---
name: create-image
description: Generate images via Midjourney or Gemini with prompt crafting and archive management
user-invocable: true
---

# Create Image

## Instructions

Follow the full workflow in `~/Data/.datacore/modules/image-generation/commands/create-image.md`.

Usage: `/create-image [description]`

Parse `$ARGUMENTS` for image description. If provided, skip the intent question and proceed to prompt crafting.

Routes to Midjourney (via Apiframe) or Gemini based on user choice. Manages prompt library and image archive.
