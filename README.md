# Image Generation Module

Unified image generation system for Datacore supporting multiple AI services with prompt library and archive management.

## Features

- **Midjourney Integration** - Via Discord API
  - Fetch historical prompts and images
  - Send new `/imagine` commands
  - Monitor generation and download results
  - Build searchable prompt library

- **Gemini AI Integration** - Google's image models
  - Fast, immediate generation
  - Custom styles and parameters
  - High quality output

- **Unified Archive**
  - Organized by date and service
  - Metadata tracking (prompts, params, timestamps)
  - Searchable prompt library
  - Export capabilities

## Installation

```bash
# Clone to modules directory
git clone https://github.com/datacore-one/module-image-generation \
  ~/.datacore/modules/image-generation

# Install Python dependencies
cd ~/.datacore/modules/image-generation
pip install -r requirements.txt
```

## Configuration

Set environment variables in `.datacore/env/.env`:

```bash
# Required for Gemini
GEMINI_API_KEY=AIza...

# Optional for Midjourney
MIDJOURNEY_DISCORD_TOKEN=your_discord_token
MIDJOURNEY_CHANNEL_ID=your_channel_id
```

### Settings

Customize in `~/.datacore/settings.local.yaml`:

```yaml
image-generation:
  # Service selection
  default_service: "gemini"  # null (ask), "midjourney", or "gemini"

  # Midjourney
  midjourney:
    download_path: "2-datacore/2-projects/images/midjourney"
    auto_fetch_on_start: false

  # Gemini
  gemini:
    model: "gemini-2.5-flash-image-preview"
    download_path: "2-datacore/2-projects/images/gemini"

  # Archive
  archive:
    organize_by_date: true
    save_metadata: true
    build_searchable_index: true

  # UX
  auto_open_image: true
```

## Usage

### Command: /create-image

Interactive image generation:

```
/create-image
```

Follows conversational workflow:
1. Choose service (Midjourney or Gemini)
2. Enter prompt
3. Optional parameters
4. Generation and download
5. Archive with metadata

### Direct Script Usage

**Gemini:**
```bash
# Generate image
python scripts/gemini-image-gen.py --prompt "mountain landscape" --output image.png

# With custom model
python scripts/gemini-image-gen.py \
  --prompt "abstract art" \
  --model gemini-3-pro-image-preview \
  --save-metadata
```

**Midjourney:**
```bash
# Fetch historical images
python scripts/midjourney-discord.py fetch --all --download

# Send new prompt
python scripts/midjourney-discord.py imagine "serene landscape" --ar 16:9

# Check status
python scripts/midjourney-discord.py status --prompt-id <message_id>
```

**Library Management:**
```bash
# Rebuild index
python scripts/image-library.py rebuild

# Search prompts
python scripts/image-library.py search "mountain"

# List recent images
python scripts/image-library.py list --limit 10

# Export library
python scripts/image-library.py export --format markdown --output library.md
```

## Archive Structure

```
2-datacore/2-projects/images/
├── midjourney/
│   ├── 2026/01/15/
│   │   ├── image-001.png
│   │   ├── image-001.json  # metadata
│   │   └── ...
│   └── index.json
├── gemini/
│   ├── 2026/01/15/
│   │   ├── image-001.png
│   │   ├── image-001.json
│   │   └── ...
│   └── index.json
└── library.json  # unified library
```

## Metadata Format

Each image has a JSON sidecar:

```json
{
  "service": "midjourney|gemini",
  "prompt": "original prompt text",
  "parameters": {
    "model": "...",
    "size": "1920x1080"
  },
  "created_at": "2026-01-15T12:00:00Z",
  "file": "image-001.png",
  "tags": []
}
```

## Integration

### With GTD Module

Tag tasks with `:AI:image:` for automated generation:

```org
** TODO Generate hero images :AI:image:
PROMPTS:
- "futuristic cityscape"
- "abstract data flow"
SERVICE: gemini
```

### With Slides Module

The slides module depends on this module for Gemini image generation. Backgrounds can be generated via this module and used in presentations.

## Security Note

**Discord Token:** Your Discord token provides full account access. Never share it or commit it to git. Store only in `.datacore/env/.env` which is gitignored.

## License

MIT

## Repository

https://github.com/datacore-one/module-image-generation
