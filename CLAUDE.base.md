---
summary: "Unified image generation via Midjourney (Apiframe) and Gemini AI with prompt library and archive."
triggers: ["create image", "generate image", "midjourney", "gemini image", "image library"]
context: on_match
---

# Image Generation Module

## Purpose

Single interface for generating images using Midjourney (via Apiframe REST API) or Gemini AI. All images are archived with metadata, organized by date, and indexed for searchability. The slides module depends on this for Gemini image generation.

## Quick Start

> Say "create image" to start the conversational image generation workflow.

## How It Works

### Generation Flow

1. Choose service (Midjourney or Gemini) or use default
2. Refine prompt and parameters
3. Generate image (Midjourney: async polling; Gemini: immediate)
4. Download with JSON metadata sidecar
5. Archive to `content/images/{service}/YYYY/MM/DD/`
6. Update searchable index

### Scripts

| Script | Purpose |
|--------|---------|
| `midjourney-api.py` | Apiframe REST API — imagine, fetch, download |
| `gemini-image-gen.py` | Gemini AI generation with styles and sizing |
| `image-library.py` | Rebuild index, search prompts, export library |

## Agents & Commands

| Name | Type | When to use |
|------|------|-------------|
| `image-generator` | agent | Routes to Midjourney or Gemini based on choice |
| `/create-image` | skill | Conversational image generation |

## Key Paths

| Path | Purpose |
|------|---------|
| `content/images/midjourney/` | Midjourney images + metadata by date |
| `content/images/gemini/` | Gemini images + metadata by date |
| `content/images/library.json` | Unified prompt library |

## Setup

Env vars in `.datacore/env/.env`:
- `GEMINI_API_KEY` — required for Gemini
- `APIFRAME_API_KEY` — required for Midjourney

---

*This file covers structure, capability, and stable configuration. Learned behavior, user corrections, and operational preferences live as engrams — call `datacore.recall` for those.*
