# Datafund / Verity - Midjourney Brand Prompts

## Brand DNA

### Datafund Core
- **Primary Color**: Pure Blue `#0000FF`
- **Secondary**: Black, White, Gray
- **Style**: Clean, minimal, professional
- **Themes**: Data sovereignty, fair data economy, ownership, privacy

### Verity Extension
- **Primary Colors**: Emerald/Teal gradients (`#A0FF7F` → `#7FDFAF`)
- **Secondary**: Slate grays, purple accents
- **Style**: Modern tech, glassmorphism, institutional
- **Themes**: AI agents, blockchain, provenance, tokenization

---

## Prompt Templates

### Style Suffix (append to all prompts)

**Datafund style:**
```
clean minimal design, pure blue (#0000FF) accent color,
black and white base, geometric shapes, professional tech aesthetic,
data sovereignty theme, modern sans-serif feel --ar 16:9
```

**Verity style:**
```
modern tech aesthetic, emerald and teal gradients,
dark slate background, glassmorphic elements, soft glow effects,
institutional fintech design, AI and blockchain theme --ar 16:9
```

---

## Ready-to-Use Prompts

### Presentation Backgrounds

**Hero/Title Slides:**
```
abstract data flow visualization, pure blue light streams on black background,
minimal geometric network nodes, depth of field, cinematic lighting,
clean professional tech aesthetic --ar 16:9
```

```
futuristic data marketplace concept, emerald teal holographic interface,
dark environment, soft glowing data particles, institutional design,
premium fintech aesthetic --ar 16:9
```

**Section Dividers:**
```
abstract geometric pattern, interlocking hexagons and lines,
pure blue (#0000FF) on white, minimal clean design,
data ownership symbolism --ar 16:9
```

```
flowing data streams, teal cyan gradient ribbons,
dark slate background, subtle grid pattern,
modern blockchain aesthetic --ar 16:9
```

### Concept Illustrations

**Data Sovereignty:**
```
person surrounded by protective data shield, glowing blue energy,
geometric fortress of personal information, ownership symbolism,
clean minimal illustration style, professional --ar 16:9
```

**AI Agents:**
```
abstract AI entity, emerald glowing neural pathways,
conversational interface visualization, friendly yet powerful,
modern tech illustration, dark background --ar 16:9
```

**Tokenization/RWA:**
```
data transforming into golden token, blue energy conversion process,
abstract blockchain visualization, clean geometric style,
institutional fintech aesthetic --ar 16:9
```

**Provenance/Trust:**
```
chain of verified data blocks, cryptographic seals glowing blue,
transparent trust visualization, minimal tech illustration,
professional institutional style --ar 16:9
```

### Conference/Undavos Specific

**Swiss Alps Tech:**
```
futuristic conference hall in Swiss Alps mountains,
holographic displays with teal data visualizations,
glass walls showing snowy peaks, warm interior lighting,
premium corporate aesthetic --ar 16:9
```

**Davos Keynote:**
```
speaker silhouette on stage, massive blue data visualization behind,
abstract network connecting audience, institutional setting,
cinematic conference photography style --ar 16:9
```

**Web3 Future:**
```
decentralized network visualization, nodes connecting globally,
emerald teal color scheme, earth from space view,
data flowing between continents, hopeful futuristic tone --ar 16:9
```

---

## Color Combinations

### Datafund Palette
| Use | Colors |
|-----|--------|
| Primary accent | `#0000FF` (pure blue) |
| Background dark | `#000000` (black) |
| Background light | `#FFFFFF` (white) |
| Subtle bg | `#F3F4F6` (gray-100) |

### Verity Palette
| Use | Colors |
|-----|--------|
| Primary gradient | `#A0FF7F` → `#7FDFAF` (emerald) |
| Dark bg | slate-900 to slate-800 |
| Accent | purple-600 |
| Highlight | amber/orange accents |

---

## Parameter Guidelines

### Aspect Ratios
- `--ar 16:9` - Presentations, hero images
- `--ar 1:1` - Social media, icons
- `--ar 9:16` - Mobile, stories
- `--ar 21:9` - Ultra-wide banners

### Style Modifiers
- `--style raw` - More photorealistic
- `--v 6.1` - Latest Midjourney version
- `--q 2` - Higher quality (more GPU time)

### Negative Prompts (avoid)
- Cluttered, busy compositions
- Warm/orange dominant colors (unless Verity accent)
- Cartoon or playful styles
- Serif fonts or old-fashioned aesthetics

---

## Usage Examples

### Generate a Datafund presentation background:
```bash
python midjourney-api.py imagine "abstract data sovereignty concept, person at center of protective blue energy field, geometric data nodes orbiting, clean minimal illustration, pure blue (#0000FF) accents on dark background, professional tech aesthetic" --ar 16:9
```

### Generate a Verity hero image:
```bash
python midjourney-api.py imagine "institutional data marketplace interface, emerald teal holographic dashboard, AI agent conversation visualization, dark slate environment, glassmorphic UI elements, premium fintech design" --ar 16:9
```

---

## Quick Reference Card

**Always include:**
- Color reference (blue #0000FF or emerald/teal)
- "clean minimal" or "professional tech aesthetic"
- Specific theme (data sovereignty, AI, blockchain, provenance)
- Aspect ratio `--ar 16:9`

**Avoid:**
- Warm colors as primary
- Busy/cluttered compositions
- Cartoon/playful styles
- Generic "tech" imagery without brand direction
