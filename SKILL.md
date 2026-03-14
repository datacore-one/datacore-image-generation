---
name: Image Generation for Datacore
description: "AI image generation — Midjourney, Gemini, prompt management, and library"
version: 0.2.0
author: datacore-one
license: MIT
tags: [images, midjourney, gemini, ai-art, generation]
x-datacore:
  module: image-generation
  tools: 0
  skills: 1
  agents: 1
  commands: 0
  workflows: 0
  engram_count: 0
  injection_policy: on_match
  match_terms: [image, midjourney, gemini, generate, art, picture, visual]
---

# Image Generation for Datacore

AI image generation — route to Midjourney (via Apiframe) or Gemini,
manage prompt library, and archive generated images.

## What This Module Provides

**Skills**: create-image

**Agents**: image-generator (routes to appropriate backend)

## When to Use

Triggers: image, midjourney, gemini, generate, art, picture, visual.
