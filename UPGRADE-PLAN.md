# Image Generation Module Upgrade Plan

## Current State Overview

### What's Working
- **Gemini AI Integration**: Direct API, fast, reliable
- **Archive System**: Date-organized structure with JSON metadata sidecars
- **Prompt Library**: Searchable index with 72 cached Midjourney prompts
- **Scripts**: `gemini-image-gen.py`, `image-library.py` fully functional

### What's Not Working Well
- **Midjourney via Discord**: The `midjourney-discord.py` approach is fragile
  - Requires user Discord token (security risk, ToS violation)
  - Scraping DMs is unreliable and rate-limited
  - Bot interactions frequently break
  - Account ban risk

---

## Upgrade Strategy: Midjourney API via Third-Party Provider

Since Midjourney has **no official API** (as of January 2026), we must use a third-party provider. After research, the recommended options are:

### Option A: Apiframe.ai (Recommended)
| Aspect | Details |
|--------|---------|
| **Pricing** | $39/month (Basic) - 900 credits |
| **Why Choose** | Multi-model support (Flux, SDXL, Sora), enterprise reliability |
| **Features** | No Discord needed, account managed for you, no ban risk |
| **Best For** | Production use, batch generation, future expansion |

### Option B: ImagineAPI.dev
| Aspect | Details |
|--------|---------|
| **Pricing** | $30/month unlimited generations |
| **Why Choose** | Simpler, unlimited, Midjourney-focused |
| **Features** | REST API, CDN included, self-hosted option |
| **Best For** | High-volume Midjourney-only use |

### Option C: UseAPI.net
| Aspect | Details |
|--------|---------|
| **Pricing** | $10/month flat |
| **Why Choose** | Cheapest option |
| **Features** | Basic API access |
| **Best For** | Light usage, experimentation |

**Recommendation**: Start with **Apiframe.ai** for reliability and multi-model future-proofing.

---

## Implementation Plan

### Phase 1: API Integration (Week 1)

#### 1.1 Create New Script: `midjourney-api.py`
Replace Discord scraping with clean REST API integration.

```python
# Core functions needed:
- generate_image(prompt, params) -> job_id
- check_status(job_id) -> status, image_urls
- download_result(job_id, output_dir) -> local_paths
- list_generations(limit) -> recent jobs
```

#### 1.2 Update Configuration
Add to `module.yaml`:
```yaml
settings:
  midjourney:
    provider: "apiframe"  # or "imagineapi", "useapi"
    api_key: ""           # From MIDJOURNEY_API_KEY env
    # Remove discord_token and channel_id
```

#### 1.3 Maintain Backwards Compatibility
- Keep existing archive structure (`midjourney/YYYY/MM/DD/`)
- Keep JSON metadata format
- Keep library integration

### Phase 2: Command Updates (Week 1-2)

#### 2.1 Update `/create-image` Command
- Remove Discord-specific prompts
- Add API provider selection (if multiple configured)
- Streamline workflow

#### 2.2 Update `image-generator` Agent
- Remove Discord bot interaction logic
- Add async job handling for API
- Improve error handling

### Phase 3: Migration & Cleanup (Week 2)

#### 3.1 Deprecate Discord Integration
- Mark `midjourney-discord.py` as deprecated
- Keep for historical fetch only (one-time migration)
- Document migration path

#### 3.2 Environment Variable Changes
```bash
# OLD (remove)
MIDJOURNEY_DISCORD_TOKEN
MIDJOURNEY_CHANNEL_ID

# NEW (add)
MIDJOURNEY_API_KEY        # Provider API key
MIDJOURNEY_API_PROVIDER   # Optional: apiframe|imagineapi|useapi
```

---

## File Changes Summary

| File | Action | Description |
|------|--------|-------------|
| `scripts/midjourney-api.py` | CREATE | New REST API integration |
| `scripts/midjourney-discord.py` | DEPRECATE | Keep for migration only |
| `module.yaml` | UPDATE | New settings structure |
| `commands/create-image.md` | UPDATE | Remove Discord references |
| `agents/image-generator.md` | UPDATE | API-based workflow |
| `CLAUDE.base.md` | UPDATE | Document new approach |
| `README.md` | UPDATE | Setup instructions |
| `requirements.txt` | UPDATE | Add any new dependencies |

---

## Immediate Task: Undavos Talk Images

### Priority: Generate images for your Undavos presentation FIRST

Before implementing the full upgrade, you can:

1. **Use Gemini** (already working) for immediate needs
2. **Use Midjourney web interface** directly for complex artistic images
3. **Manual workflow**: Generate on Midjourney website, save to archive with metadata

### Suggested Approach for Talk Images

```bash
# Use Gemini for quick iterations
python scripts/gemini-image-gen.py \
  --prompt "Your prompt here" \
  --output undavos-slide-1.png \
  --style "professional, clean, tech conference aesthetic"

# Or invoke via command
/create-image
```

### Image Themes for Undavos (Suggestions)
- Data sovereignty / personal data ownership visuals
- Decentralized network aesthetics
- Web3 / blockchain abstract backgrounds
- Swiss Alps / Davos winter themes for local flavor

---

## Timeline

| Phase | Task | Status |
|-------|------|--------|
| **NOW** | Generate Undavos images (Gemini) | 🔴 Ready to start |
| Phase 1 | API integration script | ⚪ Pending |
| Phase 2 | Command/agent updates | ⚪ Pending |
| Phase 3 | Migration & cleanup | ⚪ Pending |

---

## Questions to Decide

1. **Which API provider?** Apiframe ($39/mo) vs ImagineAPI ($30/mo unlimited)?
2. **Multi-model support?** Do you want Flux/SDXL/Sora access too?
3. **Undavos images**: What's the talk topic? I can help craft prompts.

---

## References

- [Apiframe Pricing](https://apiframe.ai/pricing)
- [ImagineAPI Documentation](https://docs.imagineapi.dev/)
- [Midjourney Plans Comparison](https://docs.midjourney.com/hc/en-us/articles/27870484040333-Comparing-Midjourney-Plans)
- [Best Midjourney APIs 2026](https://www.myarchitectai.com/blog/midjourney-apis)
