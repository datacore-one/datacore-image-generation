#!/usr/bin/env python3
"""
Complete Slide Generator v6 - FINAL PRODUCTION
- Minimal text (story without narration)
- Akzidenz Grotesk typography
- Text on negative space
- Quality validation with retry
- Sequential naming

Usage:
    python generate-slides-v6-final.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path.home() / "Data/.datacore/env/.env")

import google.generativeai as genai
from PIL import Image
from io import BytesIO
import json
import time


GEMINI_3_PRO_IMAGE = "gemini-3-pro-image-preview"
MAX_RETRIES = 2


# Slide definitions - MINIMAL TEXT, STORY-DRIVEN
SLIDES = [
    {
        "id": "title",
        "background": "title-org.png",
        "title": "We're Ready. Are You?",
        "subtitle": "Conference 2026\nSpeaker Name, Organization",
        "text_layout": "center"
    },
    {
        "id": "ai-data-war",
        "background": "act1-title-org.png",
        "title": "The AI Data War",
        "body": "Who controls data\ncontrols AI's future",
        "text_layout": "center"
    },
    {
        "id": "data-asymmetry",
        "background": "cambridge-analytica-org.png",
        "title": "The Asymmetry",
        "body": "Hospital cancer detection data:\nBalance sheet value = $0\n\nBig Tech user data ($1.3T):\nBalance sheet value = $0\n\nNo recognition = Black market",
        "text_layout": "left"
    },
    {
        "id": "digital-freedom",
        "background": "shoe-size-org.png",
        "title": "Digital Age Freedom",
        "body": "Freedom starts with\nowning your data\n\nSelf-sovereignty:\nPeople • Organizations • States",
        "text_layout": "left"
    },
    {
        "id": "cambridge-2013",
        "background": "cambridge-analytica-org.png",
        "title": "Cambridge Analytica: 2013",
        "body": "\"Psychologically targeted ads\nchange beliefs without awareness\"\n\n2018: Weaponized\n2026: Building the alternative",
        "text_layout": "left"
    },
    {
        "id": "cant-be-evil",
        "background": "act2-title-org.png",
        "title": "Don't Be Evil → Can't Be Evil",
        "body": "Change who controls it",
        "text_layout": "center"
    },
    {
        "id": "why-hard-barrier1",
        "background": "timeline-org.png",
        "title": "Why Tokenizing Data Is Hard",
        "body": "Barrier #1:\nProvenance Without Self-Sovereignty\n= Impossible\n\nControl infrastructure = Prove ownership",
        "text_layout": "center"
    },
    {
        "id": "why-hard-barrier2",
        "background": "timeline-org.png",
        "title": "Why Tokenizing Data Is Hard",
        "body": "Barrier #2:\nOwnership Undefined\n\nStocks = Clear legal framework\nData = ???\n\nWe had to build it",
        "text_layout": "center"
    },
    {
        "id": "layer1-swarm",
        "background": "fair-data-stack-org.png",
        "title": "Layer 1: Self-Sovereign Storage",
        "body": "Infrastructure Foundation\nDecentralized • Immutable • Provably yours\n\nFoundation:\nOwnership requires proof of custody",
        "text_layout": "left"
    },
    {
        "id": "layer2-fds",
        "background": "escrow-demo-org.png",
        "title": "Layer 2: Sovereignty Protocols",
        "body": "PartnerOrg\n\nPartnerDrive: Your data vault\nData Escrow: Cryptographic escrow\n\nPrimitive of exchange",
        "text_layout": "left"
    },
    {
        "id": "layer3-tokenization",
        "background": "three-sided-market-org.png",
        "title": "Layer 3: Tokenization & Markets",
        "body": "Organization • Project Alpha\n\nBreakthrough:\nOwnership ≠ Access\n\nUnlocks three-sided markets",
        "text_layout": "center"
    },
    {
        "id": "layer4-agents",
        "background": "agent-demo-split-org.png",
        "title": "Layer 4: AI Agents",
        "body": "Agents don't negotiate PDFs\nThey read smart contracts\n\nMachine-readable ownership =\nOperational necessity",
        "text_layout": "left"
    },
    {
        "id": "demo-intro",
        "background": "act3-title-org.png",
        "title": "Live Proof",
        "body": "What \"ready\" means",
        "text_layout": "center"
    },
    {
        "id": "undavos-trade",
        "background": "undavos-reveal-org.png",
        "title": "The unDavos Trade",
        "body": "Seller: Bored at Davos panel\nBuyer: Flying to Davos tomorrow\n\nData: \"Where to network tonight\"\nPrice: $3",
        "text_layout": "center"
    },
    {
        "id": "the-reveal",
        "background": "undavos-reveal-org.png",
        "title": "The Reveal",
        "body": "Recommended Event:\nunDavos Counter-Summit\n\nLocation: Right here\nCost: FREE (pizza included)\n\n\"Periphery > Center\"",
        "text_layout": "center"
    },
    {
        "id": "the-twist",
        "background": "reputation-system-org.png",
        "title": "The Twist",
        "body": "Same data\nDifferent buyers\nDifferent ratings\n\nReputation: Contextual\nNot censorship: Filtering",
        "text_layout": "center"
    },
    {
        "id": "ethereum-proof",
        "background": "etherscan-qr-org.png",
        "title": "Verify on Ethereum",
        "body": "Transaction happened\n2 minutes ago\nMainnet\n\nScan QR • Verify yourself\nReal money • Real proof",
        "text_layout": "center"
    },
    {
        "id": "the-stack-live",
        "background": "fair-data-stack-org.png",
        "title": "The Stack: Live",
        "body": "Data Escrow • PartnerDrive • Project Alpha\n\nNot roadmap\nShipping now",
        "text_layout": "center"
    },
    {
        "id": "innovation-universal",
        "background": "who-participates-org.png",
        "title": "Innovation = Universal",
        "body": "Works for all:\n\nPeople • Corporations • States\nAgents • Investors\n\nAligned incentives = Infrastructure",
        "text_layout": "left"
    },
    {
        "id": "innovation-frictionless",
        "background": "cme-example-org.png",
        "title": "Innovation = Frictionless",
        "body": "Data business = Just business\nBut autonomous\n\nRegulation clarity:\nSecurities • Commerce • Custody",
        "text_layout": "center"
    },
    {
        "id": "fire-middlemen",
        "background": "three-sided-market-org.png",
        "title": "Fire The Middlemen",
        "body": "Data Marketplaces: $3B\nData Brokers: $700B\n\nWhy? Opacity\n\nTokenization = Transparency",
        "text_layout": "center"
    },
    {
        "id": "cme-model",
        "background": "cme-example-org.png",
        "title": "The Model",
        "body": "CME: $800M/year from data\nMargins: >90%\n\nThey don't produce data\nTraders do\n\nThey built infrastructure",
        "text_layout": "center"
    },
    {
        "id": "liability-to-asset",
        "background": "three-sided-market-org.png",
        "title": "Liability → Asset",
        "body": "Before: GDPR fines, breaches, cost\nAfter: Balance sheet, revenue, compliance\n\nBlockchain enforces\nLegal recognition unlocks",
        "text_layout": "center"
    },
    {
        "id": "ownership-not-access",
        "background": "three-sided-market-org.png",
        "title": "Ownership ≠ Access",
        "body": "Apple stock ≠ iPhone\nData token ≠ Data access\n\nInvestors: Economic rights\nConsumers: Usage rights\nOwners: Control + Royalties",
        "text_layout": "center"
    },
    {
        "id": "three-sided-market",
        "background": "three-sided-market-org.png",
        "title": "Three-Sided Market",
        "body": "Investors ← Own tokens\nData Owners ← Earn revenue\nConsumers ← Access data\n\nImpossible in two-sided markets",
        "text_layout": "center"
    },
    {
        "id": "agent-economy",
        "background": "agent-demo-split-org.png",
        "title": "The Agent Economy",
        "body": "Agents = Supply + Demand\n\nMillions of transactions daily\nMachine speed\n\nNo middlemen",
        "text_layout": "center"
    },
    {
        "id": "18-month-window",
        "background": "act5-title-org.png",
        "title": "18-Month Window",
        "body": "Before institutional consolidation\n\nInfrastructure builders\nset standards",
        "text_layout": "center"
    },
    {
        "id": "builders-not-committees",
        "background": "act6-title-org.png",
        "title": "Builders vs Committees",
        "body": "Around us: Debating frameworks\n\nHere: Building infrastructure\n\nFuture decided by who ships",
        "text_layout": "center"
    },
    {
        "id": "call-to-action",
        "background": "closing-org.png",
        "title": "The Question",
        "body": "Building infrastructure?\n\nOr renting access?",
        "text_layout": "center"
    },
    {
        "id": "thank-you",
        "background": "title-org.png",
        "title": "Freedom Starts With Ownership",
        "body": "Everything changes\n\nSpeaker Name\nOrganization • Project Alpha",
        "text_layout": "center"
    }
]


def crop_to_best_quadrant_v2(img: Image.Image, model, slide_def: dict) -> Image.Image:
    """Crop 2x2 grid to quadrant with most negative space."""
    width, height = img.size
    half_w = width // 2
    half_h = height // 2

    quadrants = {
        "top-left": img.crop((0, 0, half_w, half_h)),
        "top-right": img.crop((half_w, 0, width, half_h)),
        "bottom-left": img.crop((0, half_h, half_w, height)),
        "bottom-right": img.crop((half_w, half_h, width, height))
    }

    title = slide_def.get('title', '')
    body = slide_def.get('body', '')
    text_layout = slide_def.get('text_layout', 'center')

    analysis_prompt = f"""Analyze these 4 background quadrants from a 2x2 grid.

Slide content:
Title: {title}
Body: {body[:200]}...
Text layout: {text_layout}

Choose the quadrant with the MOST EMPTY/PLAIN space for text placement.
Text should go where there's LEAST design elements.

Respond with ONLY: top-left, top-right, bottom-left, or bottom-right"""

    try:
        contents = []
        for position, quad_img in quadrants.items():
            contents.append(quad_img)
            contents.append(f"Quadrant: {position}")
        contents.append(analysis_prompt)

        response = model.generate_content(contents)
        choice = response.text.strip().lower()

        for position in quadrants.keys():
            if position in choice:
                print(f"    Selected quadrant: {position} (most negative space)")
                return quadrants[position]

        print(f"    Unclear choice, using top-left")
        return quadrants["top-left"]

    except Exception as e:
        print(f"    Error selecting quadrant: {e}, using top-left")
        return quadrants["top-left"]


def validate_slide_text(model, slide_img: Image.Image, expected_slide: dict) -> tuple[bool, str]:
    """Validate generated slide text quality."""
    title = expected_slide.get('title', '')
    body = expected_slide.get('body', '')

    validation_prompt = f"""Analyze this presentation slide image and verify text quality.

Expected content:
Title: {title}
Body: {body}

Check:
1. Title spelled correctly?
2. Body text spelled correctly?
3. Text readable and well-formatted?
4. No obvious errors or garbled text?

Respond:
VALID: YES or NO
REASON: [brief explanation]"""

    try:
        contents = [slide_img, validation_prompt]
        response = model.generate_content(contents)
        result = response.text.strip()

        is_valid = "VALID: YES" in result.upper()
        reason_line = [line for line in result.split('\n') if 'REASON:' in line.upper()]
        reason = reason_line[0].split(':', 1)[1].strip() if reason_line else "Unknown"

        return is_valid, reason

    except Exception as e:
        print(f"    Validation error: {e}")
        return True, "Validation failed, assuming OK"


def generate_slide_image_with_retry(model, slide_def: dict, background_img, output_path: Path) -> bool:
    """Generate slide with retry logic for quality validation."""

    for attempt in range(1, MAX_RETRIES + 2):
        if attempt > 1:
            print(f"    Retry attempt {attempt - 1}/{MAX_RETRIES}...")
            time.sleep(2)

        generated_img = generate_slide_image(model, slide_def, background_img, output_path)

        if not generated_img:
            if attempt > MAX_RETRIES + 1:
                return False
            continue

        print(f"    Validating text quality...")
        is_valid, reason = validate_slide_text(model, generated_img, slide_def)

        if is_valid:
            print(f"    ✓ Validation passed: {reason}")
            return True
        else:
            print(f"    ✗ Validation failed: {reason}")
            if attempt > MAX_RETRIES + 1:
                print(f"    Maximum retries reached, keeping last version")
                return True

    return False


def generate_slide_image(model, slide_def: dict, background_img, output_path: Path) -> Image.Image:
    """Generate complete slide with Akzidenz Grotesk typography."""

    title = slide_def.get('title', '')
    subtitle = slide_def.get('subtitle', '')
    body = slide_def.get('body', '')
    text_layout = slide_def.get('text_layout', 'center')

    # Construct prompt with typography specs
    prompt_parts = []
    prompt_parts.append("Create a professional presentation slide (16:9 aspect ratio) with the following text:")

    if title:
        prompt_parts.append(f"\n\nTITLE (large, bold, prominent): {title}")
    if subtitle:
        prompt_parts.append(f"\n\nSUBTITLE (smaller, under title): {subtitle}")
    if body:
        prompt_parts.append(f"\n\nBODY TEXT:\n{body}")

    prompt_parts.append(f"\n\nText layout: {text_layout} aligned")
    prompt_parts.append("\n\nDESIGN REQUIREMENTS:")
    prompt_parts.append("- Typography: Akzidenz Grotesk or similar high-end sans-serif (clean, technical, modern)")
    prompt_parts.append("- Use the provided image as background")
    prompt_parts.append("- Place text on the EMPTY/PLAIN areas of background, NOT on busy design elements")
    prompt_parts.append("- Text must have excellent contrast and readability")
    prompt_parts.append("- Generous white space around text")
    prompt_parts.append("- Strong visual hierarchy (title > subtitle > body)")
    prompt_parts.append("- Clean, minimal, high-end aesthetic")
    prompt_parts.append("- CRITICAL: Render ALL text with PERFECT spelling and formatting")
    prompt_parts.append("- Double-check every word for accuracy before rendering")

    full_prompt = "".join(prompt_parts)

    try:
        contents = []
        if background_img:
            contents.append(background_img)
            contents.append("Use this image as background. Place text on plain/empty areas only.")
        contents.append(full_prompt)

        print(f"    Generating with Gemini 3 Pro Image...")
        response = model.generate_content(
            contents=contents,
            generation_config={
                "response_modalities": ["IMAGE"],
            }
        )

        for part in response.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                image = Image.open(BytesIO(part.inline_data.data))
                output_path.parent.mkdir(parents=True, exist_ok=True)
                image.save(output_path, 'PNG', optimize=False)

                size = image.size
                print(f"    ✓ Generated: {output_path.name} ({size[0]}x{size[1]})")
                return image

        print(f"    ✗ No image in response")
        return None

    except Exception as e:
        print(f"    ✗ Error: {e}")
        return None


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Generate v6 presentation slides with minimal text and Akzidenz Grotesk'
    )

    parser.add_argument('--backgrounds-dir',
                        default=os.path.join(os.environ.get("DATACORE_ROOT", os.path.expanduser("~/Data")), '1-teamspace/1-tracks/comms/presentations/keynote-visuals/midjourney'),
                        help='Directory containing Midjourney organization backgrounds')
    parser.add_argument('--output-dir', '-o',
                        default=os.path.join(os.environ.get("DATACORE_ROOT", os.path.expanduser("~/Data")), '1-teamspace/1-tracks/comms/presentations/keynote-visuals/v6-final-slides'),
                        help='Output directory for complete slides')

    args = parser.parse_args()

    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment", file=sys.stderr)
        sys.exit(1)

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(GEMINI_3_PRO_IMAGE)

    backgrounds_dir = Path(args.backgrounds_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Using Gemini 3 Pro Image: {GEMINI_3_PRO_IMAGE}")
    print(f"Typography: Akzidenz Grotesk (high-end sans-serif)")
    print(f"Design: Minimal text, negative space placement")
    print(f"Backgrounds: {backgrounds_dir}")
    print(f"Output: {output_dir}")
    print(f"Max retries per slide: {MAX_RETRIES}")
    print()

    successful = 0
    failed = 0

    for idx, slide in enumerate(SLIDES, 1):
        slide_id = slide['id']
        background_file = slide['background']
        title = slide.get('title', 'Untitled')

        print(f"[{idx}/{len(SLIDES)}] {slide_id}")
        print(f"  Title: {title}")
        print(f"  Background: {background_file}")

        background_path = backgrounds_dir / background_file
        if not background_path.exists():
            print(f"  ✗ Background not found: {background_path}")
            failed += 1
            print()
            continue

        try:
            full_background = Image.open(background_path)
            print(f"  Loaded 2x2 grid: {full_background.size}")

            cropped_bg = crop_to_best_quadrant_v2(full_background, model, slide)

        except Exception as e:
            print(f"  ✗ Could not load/crop background: {e}")
            failed += 1
            print()
            continue

        # Sequential naming: 01_xxx.png
        output_filename = f"{idx:02d}_{slide_id}.png"
        output_path = output_dir / output_filename

        if generate_slide_image_with_retry(model, slide, cropped_bg, output_path):
            successful += 1

            metadata_path = output_path.with_suffix('.json')
            metadata = {
                "sequence": idx,
                "slide_id": slide_id,
                "title": title,
                "background_reference": background_file,
                "model": GEMINI_3_PRO_IMAGE,
                "typography": "Akzidenz Grotesk",
                "generated_at": datetime.now().isoformat()
            }
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
        else:
            failed += 1

        print()

    print("=" * 60)
    print("Generation Complete")
    print("=" * 60)
    print(f"Total slides: {len(SLIDES)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    if successful + failed > 0:
        print(f"Success rate: {(successful/(successful+failed)*100):.1f}%")
    print()
    print(f"Complete slides saved to: {output_dir}")
    print()
    print("Design: Minimal text + Akzidenz Grotesk + Negative space")
    print("Files: Sequential naming (01_xxx.png, 02_xxx.png, etc.)")


if __name__ == '__main__':
    main()
