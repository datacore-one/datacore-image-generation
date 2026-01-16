# /create-image

Generate images using AI services (Midjourney or Gemini) with unified interface and archive management.

## Workflow

### Step 1: Choose Service

If user hasn't specified a service or `settings.image-generation.default_service` is not set, ask:

"Which image generation service would you like to use?"

1. **Midjourney** - Via Discord API (high quality, artistic styles, slower)
2. **Gemini AI** - Google's models (fast, good quality, immediate)
3. **Search Library** - Search existing prompts and images

If `settings.image-generation.default_service` is set (e.g., `gemini`), skip menu and proceed with that service.

### Step 2: Route to Service Workflow

#### Option 1: Midjourney

1. **Check Discord Setup**:
   - Verify `MIDJOURNEY_DISCORD_TOKEN` and `MIDJOURNEY_CHANNEL_ID` are set
   - If missing, provide setup instructions (see Error Handling below)

2. **Get Prompt**:
   - Ask: "What would you like Midjourney to generate?"
   - User provides prompt (can be detailed or simple)

3. **Optional Parameters**:
   - Ask if user wants to specify Midjourney parameters (--ar, --style, --v, etc.)
   - Default: Use Midjourney defaults

4. **Send to Discord**:
   - Call `scripts/midjourney-discord.py imagine <prompt> [params]`
   - Show confirmation: "Sent to Midjourney. This may take 1-2 minutes..."

5. **Monitor and Download**:
   - Poll Discord channel for completion
   - When ready, download all variations
   - Save to archive with metadata
   - Show user: "Generated 4 variations. Saved to: [path]"

6. **Follow-up**:
   - "Would you like to upscale one of these? (U1/U2/U3/U4)"
   - "Would you like to generate variations? (V1/V2/V3/V4)"
   - "Generate another image?"

#### Option 2: Gemini AI

1. **Get Prompt**:
   - Ask: "What would you like Gemini to generate?"
   - User provides prompt

2. **Optional Parameters**:
   - Ask if user wants custom settings:
     - Model (default: `gemini-2.5-flash-image`)
     - Size/aspect ratio (default: `1920x1080`)
     - Style instructions (optional)

3. **Generate**:
   - Call `scripts/gemini-image-gen.py --prompt "<prompt>" --output <path>`
   - Show progress indicator

4. **Save and Show**:
   - Save to archive with metadata
   - If `settings.image-generation.auto_open_image: true`, open in viewer
   - Show path: "Image saved to: [path]"

5. **Follow-up**:
   - "Would you like to generate variations of this prompt?"
   - "Generate another image?"
   - "Add tags to organize this image?"

#### Option 3: Search Library

1. **Get Search Query**:
   - Ask: "What prompt keywords are you looking for?"

2. **Search**:
   - Call `scripts/image-library.py search "<query>"`
   - Show results with thumbnails/paths and prompts

3. **Actions**:
   - "Would you like to:"
     - "Reuse this prompt (with modifications)?"
     - "View the full-size image?"
     - "Generate a variation?"

### Step 3: Archive and Metadata

After successful generation:

1. **Save Image**:
   - Path: `{space}/2-datacore/2-projects/images/{service}/{YYYY}/{MM}/{DD}/image-{timestamp}.png`

2. **Create Metadata**:
   - JSON sidecar: same path with `.json` extension
   - Contains:
     ```json
     {
       "service": "midjourney|gemini",
       "prompt": "...",
       "parameters": {...},
       "created_at": "2026-01-15T12:34:56Z",
       "file": "image-001.png",
       "tags": []
     }
     ```

3. **Update Index**:
   - If `settings.image-generation.archive.build_searchable_index: true`
   - Append to `{service}/index.json` for searchability

### Step 4: Follow-up Actions

After each generation, offer:

- "Would you like to generate another image?"
- "Tag this image for organization?"
- "Use this in a presentation?" (if slides module installed)
- "Done for now?"

## Auto-Run Mode

If `settings.image-generation.default_service` is set to `midjourney` or `gemini`:
- Skip service selection menu
- Go straight to prompt input for that service

Example:
```yaml
image-generation:
  default_service: "gemini"  # Always use Gemini
  auto_open_image: true      # Auto-open after generation
```

## Settings Reference

User can configure in `~/.datacore/settings.local.yaml`:

```yaml
image-generation:
  # Service selection
  default_service: "gemini"  # null (ask), "midjourney", or "gemini"

  # Midjourney settings
  midjourney:
    discord_token: ""  # Set via MIDJOURNEY_DISCORD_TOKEN env var
    channel_id: ""     # Set via MIDJOURNEY_CHANNEL_ID env var
    download_path: "2-datacore/2-projects/images/midjourney"
    auto_fetch_on_start: false

  # Gemini settings
  gemini:
    api_key: ""  # Set via GEMINI_API_KEY env var
    model: "gemini-2.5-flash-image"
    download_path: "2-datacore/2-projects/images/gemini"
    default_size: "1920x1080"

  # Archive behavior
  archive:
    organize_by_date: true
    save_metadata: true
    build_searchable_index: true

  # UX
  auto_open_image: true  # Open in default viewer after generation
```

## Error Handling

**Missing Discord credentials (Midjourney):**
```
Error: Midjourney Discord credentials not configured.

Solution:
  1. Get your Discord user token:
     - Open Discord in browser
     - Open DevTools (F12) > Network tab
     - Look for any XHR request
     - Find "authorization" header
     - Copy the token (starts with "MTk...")

  2. Get your Midjourney DM channel ID:
     - Right-click Midjourney bot in DMs
     - Copy ID (enable Developer Mode in Settings)

  3. Add to .datacore/env/.env:
     MIDJOURNEY_DISCORD_TOKEN=your_token_here
     MIDJOURNEY_CHANNEL_ID=your_channel_id_here

Warning: Never share your Discord token with anyone.
```

**Missing Gemini API key:**
```
Error: GEMINI_API_KEY not found.

Solution:
  1. Get API key from: https://aistudio.google.com/apikey
  2. Add to .datacore/env/.env:
     GEMINI_API_KEY=AIza...
```

**Midjourney timeout:**
```
Warning: Midjourney generation taking longer than expected (>2 min).

The image is still being generated. Options:
  1. Keep waiting (status checks every 15s)
  2. Cancel and check Discord manually
  3. Check later with: /create-image --fetch-latest
```

**Archive directory doesn't exist:**
```
Error: Archive directory not found.

Solution:
  Creating directory: ~/Data/2-datacore/2-projects/images/{service}/

  Done! Generated images will be saved here.
```

## Your Boundaries

**YOU CAN:**
- Generate images via Midjourney (Discord API)
- Generate images via Gemini AI
- Save images with metadata to archive
- Organize and index image library
- Search past prompts and images
- Fetch Midjourney history from Discord
- Offer variations and refinements
- Auto-open images in default viewer

**YOU CANNOT:**
- Generate images without user prompts
- Edit or modify existing images (use external tools)
- Access user's Discord account beyond Midjourney bot interactions
- Generate NSFW or harmful content (both services have filters)
- Override service content policies

**YOU MUST:**
- Save metadata with every generated image
- Update searchable index when configured
- Respect user's service preference settings
- Handle missing credentials gracefully with clear setup instructions
- Warn user about Discord token security

## Integration Notes

**Slides Module:**
If the slides module is installed, after generating an image offer:
- "Would you like to use this as a slide background?"
- "Create a presentation with this image?"

**GTD Module:**
Support AI task tags like `:AI:images:` for batch generation:
```org
** TODO Generate marketing images for Q1 campaign :AI:images:
PROMPT: "futuristic cityscape", "tech startup office", "data visualization"
```

## Scripts Reference

**Midjourney Discord:**
```bash
# Fetch all historical images
python scripts/midjourney-discord.py fetch --all

# Send new prompt
python scripts/midjourney-discord.py imagine "prompt" --ar 16:9 --v 6

# Check status
python scripts/midjourney-discord.py status --prompt-id <id>
```

**Gemini:**
```bash
# Generate image
python scripts/gemini-image-gen.py --prompt "prompt" --output path.png

# With custom model
python scripts/gemini-image-gen.py --prompt "prompt" --model gemini-3-pro-image-preview
```

**Library:**
```bash
# Search prompts
python scripts/image-library.py search "keyword"

# Rebuild index
python scripts/image-library.py rebuild

# Export library
python scripts/image-library.py export --format json --output library.json
```

---

**Remember**: You provide a unified interface to multiple image generation services. Always save metadata for future searchability and prompt reuse.
