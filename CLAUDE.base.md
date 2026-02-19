# Module: image-generation

Unified image generation system supporting multiple AI services with prompt library and archive management.

## Overview

This module provides a single interface for generating images using:
- **Midjourney** - Via Discord API (fetch history, send prompts, download results)
- **Gemini AI** - Google's image generation models (fast, integrated)

All images are archived with metadata, organized by date/project, and indexed for searchability.

## Commands

### /create-image

Conversational command for generating images. Asks user which service to use (Midjourney or Gemini), then handles the full workflow:
- Prompt refinement and parameter selection
- Image generation and monitoring
- Download with metadata (prompt, params, timestamp)
- Archive organization and indexing
- Optional auto-open in default viewer

**Use cases:**
- Generate marketing images and graphics
- Create custom profile pictures and avatars
- Build presentation backgrounds
- Quick visual content creation

## Agents

### image-generator

Routes image generation requests to appropriate service based on user choice. Handles:
- Midjourney workflow (Discord API, polling for completion)
- Gemini workflow (direct API, immediate results)
- Archive organization and metadata
- Prompt library updates

## Scripts

### midjourney-api.py

Discord API integration for Midjourney bot:
- Fetch historical prompts and images from DM channel
- Send new `/imagine` commands to Midjourney bot
- Monitor for completion and download results
- Extract metadata from Discord messages

**Usage:**
```bash
# Fetch all historical images
python scripts/midjourney-api.py fetch --all

# Send new prompt
python scripts/midjourney-api.py imagine "a serene mountain landscape at sunset"

# Monitor and download when ready
python scripts/midjourney-api.py download --prompt-id <id>
```

### gemini-image-gen.py

Reusable Gemini AI image generation (extracted from slides module):
- Generate images from text prompts
- Support custom styles and parameters
- Handle aspect ratios and sizing
- Save with metadata

**Usage:**
```bash
# Generate single image
python scripts/gemini-image-gen.py --prompt "futuristic cityscape" --output ./output.png

# With custom parameters
python scripts/gemini-image-gen.py --prompt "abstract art" --model gemini-3-pro-image-preview --size 1920x1080
```

### image-library.py

Manage image archive and prompt library:
- Index all images with metadata
- Search by prompt keywords, date, service
- Rebuild searchable index
- Export prompt library

**Usage:**
```bash
# Rebuild index
python scripts/image-library.py rebuild

# Search prompts
python scripts/image-library.py search "mountain landscape"

# Export library
python scripts/image-library.py export --format json
```

## Archive Structure

```
2-projectspace/2-projects/images/
├── midjourney/
│   ├── 2026/
│   │   ├── 01/
│   │   │   ├── 15/
│   │   │   │   ├── image-001.png
│   │   │   │   ├── image-001.json  # metadata
│   │   │   │   └── ...
│   └── index.json  # searchable index
├── gemini/
│   ├── 2026/
│   │   └── 01/
│   │       └── 15/
│   │           ├── image-001.png
│   │           ├── image-001.json
│   │           └── ...
│   └── index.json
└── library.json  # unified prompt library
```

## Metadata Format

Each image has a JSON sidecar file:
```json
{
  "service": "midjourney|gemini",
  "prompt": "original prompt text",
  "parameters": {
    "model": "...",
    "size": "1920x1080",
    "style": "..."
  },
  "created_at": "2026-01-15T12:00:00Z",
  "file": "image-001.png",
  "tags": ["marketing", "landscape"]
}
```

## Settings

Configure in `~/.datacore/settings.local.yaml`:

```yaml
image-generation:
  midjourney:
    auto_fetch_on_start: true  # Fetch latest images when command runs

  gemini:
    model: "gemini-3-pro-image-preview"

  archive:
    organize_by_date: true
    organize_by_project: false
    save_metadata: true
    build_searchable_index: true

  auto_open_image: true
  default_service: "gemini"  # Skip the menu, use Gemini by default
```

## Integration with Other Modules

### Slides Module

The slides module depends on this module for Gemini image generation:
- Shares `gemini-image-gen.py` script
- Uses same API key and configuration
- Backgrounds generated via this module

### Future Integrations

- GTD module: AI tasks for batch image generation (`:AI:images:`)
- CRM module: Profile picture generation
- Content module: Blog post featured images

## Environment Variables

Set in `.datacore/env/.env`:

```bash
# Required for Gemini
GEMINI_API_KEY=AIza...

# Optional for Midjourney
MIDJOURNEY_DISCORD_TOKEN=...
MIDJOURNEY_CHANNEL_ID=...
```

## Installation

```bash
git clone https://github.com/datacore-one/module-image-generation ~/.datacore/modules/image-generation
```

Set environment variables in `.datacore/env/.env`, then run:

```bash
/create-image
```

## Dependencies

- Python 3.9+
- `google-generativeai` (Gemini)
- `discord.py` (Midjourney)
- `Pillow` (image processing)
- `python-dotenv` (env management)
