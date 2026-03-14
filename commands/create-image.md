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

1. **Check API Setup**:
   - Verify `APIFRAME_API_KEY` is set
   - If missing, provide setup instructions (see Error Handling below)

2. **Get Prompt**:
   - Ask: "What would you like Midjourney to generate?"
   - User provides prompt (can be detailed or simple)

3. **Optional Parameters**:
   - Ask if user wants to specify Midjourney parameters (--ar, --style, --v, --mode, etc.)
   - Default: Use Midjourney defaults

4. **Submit to Apiframe**:
   - Call `scripts/midjourney-api.py imagine "<prompt>" [--ar 16:9] [--mode fast]`
   - Show confirmation: "Submitted to Midjourney. This may take 1-2 minutes..."

5. **Monitor and Download**:
   - Poll Apiframe API for completion
   - When ready, download all 4 variations
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
     - Model (default: `gemini-3-pro-image-preview`)
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
   - Path: `{space}/content/images/{service}/{YYYY}/{MM}/{DD}/image-{timestamp}.png`

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

  # Midjourney settings (via Apiframe)
  midjourney:
    api_key: ""  # Set via APIFRAME_API_KEY env var
    download_path: "content/images/midjourney"
    default_mode: "fast"  # fast or turbo

  # Gemini settings
  gemini:
    api_key: ""  # Set via GEMINI_API_KEY env var
    model: "gemini-3-pro-image-preview"
    download_path: "content/images/gemini"
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

**Missing Apiframe API key (Midjourney):**
```
Error: APIFRAME_API_KEY not found.

Solution:
  1. Sign up at https://apiframe.ai
  2. Get your API key from the dashboard
  3. Add to .datacore/env/.env:
     APIFRAME_API_KEY=your_key_here
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
Warning: Midjourney generation taking longer than expected (>5 min).

The image is still being generated. Options:
  1. Keep waiting (status checks every 10s)
  2. Cancel and check later with task ID
  3. Check status: python scripts/midjourney-api.py status <task_id>
```

**Archive directory doesn't exist:**
```
Error: Archive directory not found.

Solution:
  Creating directory: ~/Data/content/images/{service}/

  Done! Generated images will be saved here.
```

## Your Boundaries

**YOU CAN:**
- Generate images via Midjourney (Apiframe API)
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

**Midjourney (via Apiframe):**
```bash
# Generate image (waits for completion)
python scripts/midjourney-api.py imagine "prompt" --ar 16:9

# Submit without waiting
python scripts/midjourney-api.py imagine "prompt" --no-wait

# Check status
python scripts/midjourney-api.py status <task_id> --download
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
