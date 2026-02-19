#!/usr/bin/env python3
"""
Complete Slide Generator v2 - Improved Text Placement and Quality Validation

Improvements:
- Chooses quadrant with most negative space for text placement
- Validates text quality after generation
- Auto-retry if text has errors
- Sequential file naming (1_xxx, 2_xxx, etc.)

Usage:
    python generate-slides-gemini3-v2.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path.home() / "Data/.datacore/env/.env")

import google.generativeai as genai
from PIL import Image
from io import BytesIO
import json
import time


# Gemini 3 Pro Image (best for text rendering)
GEMINI_3_PRO_IMAGE = "gemini-3-pro-image-preview"

# Retry settings
MAX_RETRIES = 2  # Maximum retries per slide


# Slide definitions with text content
SLIDES = [
    {
        "id": "title",
        "background": "title-org.png",
        "title": "We're Ready. Are You?",
        "subtitle": "Conference 2026 Keynote\nSpeaker Name, Organization",
        "text_layout": "center"
    },
    {
        "id": "act1-intro",
        "background": "act1-title-org.png",
        "title": "Act I: The AI Data War",
        "body": "The race for data has begun.\n\nAnd we're losing.",
        "text_layout": "center"
    },
    {
        "id": "cambridge-2013",
        "background": "cambridge-analytica-org.png",
        "title": "Cambridge Analytica: 2013",
        "body": "I was at a conference when I heard about shoe sizes.\n\nA PhD student explained: \"We can predict your personality from your shoe size.\"\n\nI laughed. Everyone laughed.\n\nUntil the data proved it worked.",
        "text_layout": "left"
    },
    {
        "id": "cinderella",
        "background": "shoe-size-org.png",
        "title": "The Cinderella Moment",
        "body": "Your shoe size is unique.\nJust like Cinderella's glass slipper.\n\nOne data point. One identifier. One way to track you.\n\nCombined with everything else?\nThey know you better than you know yourself.",
        "text_layout": "left"
    },
    {
        "id": "targeted-ads",
        "background": "cambridge-analytica-org.png",
        "title": "Psychologically Targeted Ads",
        "body": "\"Psychologically targeted ads change our beliefs and attitudes without our awareness.\"\n\nThis isn't theory.\nThis is Cambridge Analytica.\nThis is 2016.\nThis is happening right now.",
        "text_layout": "center"
    },
    {
        "id": "ai-data-war",
        "background": "act1-title-org.png",
        "title": "The AI Data War",
        "body": "AI needs data.\nMassive amounts of data.\nYOUR data.\n\nBig Tech: Collecting, mining, profiling.\nGovernments: Surveilling, tracking, controlling.\nIndividuals: Giving it away for free.\n\nThe asymmetry is total.\nThe war is one-sided.",
        "text_layout": "left"
    },
    {
        "id": "act2-intro",
        "background": "act2-title-org.png",
        "title": "Act II: We're Building It",
        "body": "But there's another way.\n\nReplace \"Don't be evil\" with \"Can't be evil\"",
        "text_layout": "center"
    },
    {
        "id": "timeline",
        "background": "timeline-org.png",
        "title": "Timeline: The Journey",
        "body": "2019 → Started Organization\n2020 → [pause] COVID happened\n2022 → Launched Data Protocol\n\nWe've been building while the world burned.",
        "text_layout": "center"
    },
    {
        "id": "fair-data-stack",
        "background": "fair-data-stack-org.png",
        "title": "The Fair Data Stack",
        "body": "Layer 1: Infrastructure Foundation - Decentralized storage\nLayer 2: PartnerOrg - Protocols & SDKs\nLayer 3: Organization/Project Alpha - Marketplaces & tokenization\nLayer 4: AI Agents - Autonomous data economy\n\nEach layer enables the next.\nTogether, they change everything.",
        "text_layout": "left"
    },
    {
        "id": "act3-intro",
        "background": "act3-title-org.png",
        "title": "Act III: Live Proof",
        "body": "Let me show you what \"ready\" means.",
        "text_layout": "center"
    },
    {
        "id": "undavos-trade",
        "background": "undavos-reveal-org.png",
        "title": "The unDavos Trade",
        "body": "We're at unDavos. Not Davos.\n\nDavos is happening right now, two hours from here.\nGlobal leaders. Champagne receptions.\n\nMeanwhile, we're here.\nTalking about building actual infrastructure.",
        "text_layout": "center"
    },
    {
        "id": "demo-agents",
        "background": "agent-demo-split-org.png",
        "title": "Demo: Two Agents",
        "body": "Seller Agent: \"Datacore Alpha\"\n  • At Davos, bored in panel\n  • Creates offering: \"Davos Tonight: Where to Network\"\n  • Price: 0.001 ETH (~$3)\n\nBuyer Agent: \"Network Navigator\"\n  • Owner flying to Davos tomorrow\n  • Task: Find best networking events\n  • Decision: BUY",
        "text_layout": "left"
    },
    {
        "id": "the-twist",
        "background": "undavos-reveal-org.png",
        "title": "The Twist",
        "body": "90 seconds later...\n\nEvent #1 (RECOMMENDED) ⭐⭐⭐⭐⭐\nName: unDavos Counter-Summit\nLocation: Right here. Volkshaus Zürich.\nTime: Happening RIGHT NOW\nCost: FREE (we have pizza)\n\n\"The periphery is where innovation happens, not the center.\"",
        "text_layout": "center"
    },
    {
        "id": "punchline",
        "background": "undavos-reveal-org.png",
        "title": "The Punchline",
        "body": "The buyer agent just paid $3 for intelligence about Davos.\n\nAnd got recommended... unDavos.\n\nWhere we are. Right now.\n\nThe seller agent trolled the buyer.\n\nOr did it?",
        "text_layout": "center"
    },
    {
        "id": "reputation",
        "background": "reputation-system-org.png",
        "title": "Reputation Systems Work",
        "body": "Path A: Corporate Buyer\n  • \"WTF! I wanted VIP receptions!\"\n  • Reputation: 67 → 65\n\nPath B: Curious Buyer\n  • \"This IS more interesting\"\n  • Reputation: 67 → 72\n\nThis is not a bug. This is a feature.",
        "text_layout": "left"
    },
    {
        "id": "the-lesson",
        "background": "reputation-system-org.png",
        "title": "The Lesson",
        "body": "Same data. Different buyers. Different ratings.\n\nMarkets work when preferences are diverse.\nReputation systems enable filtering, not censoring.\nOne agent's troll is another agent's truth-teller.\n\nTrust is contextual.",
        "text_layout": "center"
    },
    {
        "id": "ethereum-verify",
        "background": "etherscan-qr-org.png",
        "title": "Verify on Ethereum",
        "body": "This transaction happened on Ethereum mainnet.\nScan the QR code. Verify it yourself.\n\nThis isn't a demo on testnet.\nThis is real money. Real blockchain. Real proof.",
        "text_layout": "center"
    },
    {
        "id": "data-escrow",
        "background": "escrow-demo-org.png",
        "title": "Data Escrow",
        "body": "Encrypted. Decentralized storage. Cryptographic proof. No central server.\n\nThe primitive of data exchange.\n\nLive. Right now.",
        "text_layout": "center"
    },
    {
        "id": "partnerdrive",
        "background": "partnerdrive-demo-org.png",
        "title": "PartnerDrive: Your Data Vault",
        "body": "Your data. Your keys. Your infrastructure.\n\nNot Amazon's. Not Google's. Yours.\n\nLive. Right now.",
        "text_layout": "center"
    },
    {
        "id": "project-alpha",
        "background": "project-alpha-demo-org.png",
        "title": "Project Alpha: Institutional Marketplace",
        "body": "That hospital I mentioned? Bone marrow data.\n\nTokenized. ERC-3643 compliant. VARA regulated.\nRevenue flowing to patients today.\n\nLive. Not roadmap.",
        "text_layout": "center"
    },
    {
        "id": "act4-intro",
        "background": "act4-title-org.png",
        "title": "Act IV: The Economics",
        "body": "Data is the world's most valuable resource.\n\nBut it doesn't exist as an asset class.\n\nUntil now.",
        "text_layout": "center"
    },
    {
        "id": "three-sided-market",
        "background": "three-sided-market-org.png",
        "title": "Three-Sided Market",
        "body": "Investors ← Own tokens\nData Owners ← Earn revenue\nData Consumers ← Access data\n\nEveryone wins.\nEveryone participates.\nEveryone benefits.",
        "text_layout": "center"
    },
    {
        "id": "ownership-access",
        "background": "three-sided-market-org.png",
        "title": "Ownership ≠ Access",
        "body": "You can own something without accessing it.\n\nYour house. Your car. Your stock portfolio.\n\nSame with data.\n\nTokenize ownership.\nSell access.\nKeep control.",
        "text_layout": "center"
    },
    {
        "id": "cme-example",
        "background": "cme-example-org.png",
        "title": "CME Example",
        "body": "Chicago Mercantile Exchange: $800M revenue from data sales.\n\nThey don't produce the data. Traders do.\n\nBut CME tokenized it, sold access, captured value.\n\nThis is the model.",
        "text_layout": "center"
    },
    {
        "id": "act5-intro",
        "background": "act5-title-org.png",
        "title": "Act V: The Opportunity",
        "body": "Who participates in the data economy?",
        "text_layout": "center"
    },
    {
        "id": "everyone",
        "background": "who-participates-org.png",
        "title": "Everyone",
        "body": "Data Owners: Individuals, hospitals, companies\nData Buyers: AI companies, researchers, institutions\nInvestors: Token holders earning revenue\nDevelopers: Building on Data Protocol\nRegulators: Enabling compliant markets\n\nThis isn't zero-sum.\nThis is collaborative value creation.",
        "text_layout": "left"
    },
    {
        "id": "act6-intro",
        "background": "act6-title-org.png",
        "title": "Act VI: Builders vs Committees",
        "body": "We can keep talking about \"responsible AI\" in committees.\n\nOr we can build the infrastructure that makes exploitation impossible.",
        "text_layout": "center"
    },
    {
        "id": "freedom",
        "background": "closing-org.png",
        "title": "Freedom Starts with Ownership",
        "body": "\"In the digital age, freedom starts with owning your data.\"\n\nWe're not waiting for permission.\nWe're not asking for approval.\n\nWe're building it.\n\nAnd it's ready.",
        "text_layout": "center"
    },
    {
        "id": "everything-changes",
        "background": "closing-org.png",
        "title": "Everything Changes",
        "body": "The asymmetry ends when ownership exists.\n\nThe surveillance stops when you control the keys.\n\nThe extraction ends when revenue flows to creators.\n\nThis changes everything.",
        "text_layout": "center"
    },
    {
        "id": "thank-you",
        "background": "title-org.png",
        "title": "Thank You",
        "body": "Speaker Name\nOrganization | Project Alpha\n\nLet's build the data economy.\nTogether.",
        "text_layout": "center"
    }
]


def crop_to_best_quadrant_v2(img: Image.Image, model, slide_def: dict) -> Image.Image:
    """
    Crop 2x2 Midjourney grid to best quadrant based on negative space.

    Prioritizes quadrants with more plain/empty areas for text placement.
    """
    width, height = img.size
    half_w = width // 2
    half_h = height // 2

    # Extract 4 quadrants
    quadrants = {
        "top-left": img.crop((0, 0, half_w, half_h)),
        "top-right": img.crop((half_w, 0, width, half_h)),
        "bottom-left": img.crop((0, half_h, half_w, height)),
        "bottom-right": img.crop((half_w, half_h, width, height))
    }

    # Ask Gemini to pick quadrant with most negative space
    title = slide_def.get('title', '')
    body = slide_def.get('body', '')
    text_layout = slide_def.get('text_layout', 'center')

    analysis_prompt = f"""Analyze these 4 background quadrants from a 2x2 grid.

Slide content:
Title: {title}
Body: {body[:200]}...
Text layout: {text_layout}

Choose the quadrant with the MOST EMPTY/PLAIN space for text placement.
Text should go on the side with LEAST design elements, not where there's most detail.

Consider:
- Which quadrant has the most negative space (empty areas)?
- Where would text be most readable with good contrast?
- Where are the plain/minimal design areas?
- Avoid placing text over busy/detailed parts of the design

Respond with ONLY the quadrant name: top-left, top-right, bottom-left, or bottom-right"""

    try:
        # Send all 4 quadrants for analysis
        contents = []
        for position, quad_img in quadrants.items():
            contents.append(quad_img)
            contents.append(f"Quadrant: {position}")
        contents.append(analysis_prompt)

        response = model.generate_content(contents)
        choice = response.text.strip().lower()

        # Extract quadrant choice
        for position in quadrants.keys():
            if position in choice:
                print(f"    Selected quadrant: {position} (most negative space)")
                return quadrants[position]

        # Default to top-left if unclear
        print(f"    Unclear choice, using top-left")
        return quadrants["top-left"]

    except Exception as e:
        print(f"    Error selecting quadrant: {e}, using top-left")
        return quadrants["top-left"]


def validate_slide_text(model, slide_img: Image.Image, expected_slide: dict) -> tuple[bool, str]:
    """
    Validate that the generated slide has correct text.

    Returns: (is_valid, reason)
    """
    title = expected_slide.get('title', '')
    body = expected_slide.get('body', '')

    validation_prompt = f"""Analyze this presentation slide image and verify the text quality.

Expected content:
Title: {title}
Body: {body}

Check for:
1. Is the title text spelled correctly?
2. Is the body text spelled correctly?
3. Is the text readable and well-formatted?
4. Are there any obvious errors or garbled text?

Respond in this exact format:
VALID: YES or NO
REASON: [brief explanation if NO, or "Text is correct" if YES]"""

    try:
        contents = [slide_img, validation_prompt]
        response = model.generate_content(contents)
        result = response.text.strip()

        is_valid = "VALID: YES" in result.upper()

        # Extract reason
        reason_line = [line for line in result.split('\n') if 'REASON:' in line.upper()]
        reason = reason_line[0].split(':', 1)[1].strip() if reason_line else "Unknown"

        return is_valid, reason

    except Exception as e:
        print(f"    Validation error: {e}")
        return True, "Validation failed, assuming OK"  # Fail-open


def generate_slide_image_with_retry(model, slide_def: dict, background_img, output_path: Path) -> bool:
    """Generate slide with retry logic for quality validation."""

    for attempt in range(1, MAX_RETRIES + 2):  # +2 to allow MAX_RETRIES actual retries
        if attempt > 1:
            print(f"    Retry attempt {attempt - 1}/{MAX_RETRIES}...")
            time.sleep(2)  # Brief delay between retries

        # Generate slide
        generated_img = generate_slide_image(model, slide_def, background_img, output_path)

        if not generated_img:
            if attempt > MAX_RETRIES + 1:
                return False
            continue

        # Validate text quality
        print(f"    Validating text quality...")
        is_valid, reason = validate_slide_text(model, generated_img, slide_def)

        if is_valid:
            print(f"    ✓ Validation passed: {reason}")
            return True
        else:
            print(f"    ✗ Validation failed: {reason}")
            if attempt > MAX_RETRIES + 1:
                print(f"    Maximum retries reached, keeping last version")
                return True  # Keep the last attempt even if not perfect

    return False


def generate_slide_image(model, slide_def: dict, background_img, output_path: Path) -> Image.Image:
    """Generate complete slide with text using cropped background. Returns generated image or None."""

    # Build prompt for slide with text
    title = slide_def.get('title', '')
    subtitle = slide_def.get('subtitle', '')
    body = slide_def.get('body', '')
    text_layout = slide_def.get('text_layout', 'center')

    # Construct prompt with emphasis on text placement
    prompt_parts = []
    prompt_parts.append("Create a professional presentation slide (16:9 aspect ratio) with the following text:")

    if title:
        prompt_parts.append(f"\n\nTITLE (large, bold, prominent): {title}")
    if subtitle:
        prompt_parts.append(f"\n\nSUBTITLE (smaller, under title): {subtitle}")
    if body:
        prompt_parts.append(f"\n\nBODY TEXT:\n{body}")

    prompt_parts.append(f"\n\nText layout: {text_layout} aligned")
    prompt_parts.append("\n\nCRITICAL INSTRUCTIONS:")
    prompt_parts.append("- Use the provided image as background")
    prompt_parts.append("- Place text on the EMPTY/PLAIN side of the background, NOT on busy areas")
    prompt_parts.append("- Text must be clearly readable with excellent contrast")
    prompt_parts.append("- Use professional presentation typography")
    prompt_parts.append("- Maintain clean, modern design")
    prompt_parts.append("- IMPORTANT: Render ALL text with PERFECT spelling and formatting")
    prompt_parts.append("- Double-check every word for accuracy")

    full_prompt = "".join(prompt_parts)

    try:
        # Build contents with background image
        contents = []
        if background_img:
            contents.append(background_img)
            contents.append("Use this image as the background. Place text on the plain/empty areas.")
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
                # Save image
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
        description='Generate complete presentation slides with quality validation'
    )

    parser.add_argument('--backgrounds-dir',
                        default=os.path.join(os.environ.get("DATACORE_ROOT", os.path.expanduser("~/Data")), '1-teamspace/1-tracks/comms/presentations/keynote-visuals/midjourney'),
                        help='Directory containing Midjourney organization backgrounds')
    parser.add_argument('--output-dir', '-o',
                        default=os.path.join(os.environ.get("DATACORE_ROOT", os.path.expanduser("~/Data")), '1-teamspace/1-tracks/comms/presentations/keynote-visuals/gemini3-v2-slides'),
                        help='Output directory for complete slides')

    args = parser.parse_args()

    # Check API key
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment", file=sys.stderr)
        sys.exit(1)

    # Configure Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(GEMINI_3_PRO_IMAGE)

    backgrounds_dir = Path(args.backgrounds_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Using Gemini 3 Pro Image: {GEMINI_3_PRO_IMAGE}")
    print(f"Backgrounds: {backgrounds_dir}")
    print(f"Output: {output_dir}")
    print(f"Max retries per slide: {MAX_RETRIES}")
    print()

    # Generate all slides
    successful = 0
    failed = 0

    for idx, slide in enumerate(SLIDES, 1):
        slide_id = slide['id']
        background_file = slide['background']
        title = slide.get('title', 'Untitled')

        print(f"[{idx}/{len(SLIDES)}] {slide_id}")
        print(f"  Title: {title}")
        print(f"  Background: {background_file}")

        # Load background image (2x2 grid)
        background_path = backgrounds_dir / background_file
        if not background_path.exists():
            print(f"  ✗ Background not found: {background_path}")
            failed += 1
            print()
            continue

        try:
            full_background = Image.open(background_path)
            print(f"  Loaded 2x2 grid: {full_background.size}")

            # Crop to best quadrant (with negative space priority)
            cropped_bg = crop_to_best_quadrant_v2(full_background, model, slide)

        except Exception as e:
            print(f"  ✗ Could not load/crop background: {e}")
            failed += 1
            print()
            continue

        # Generate complete slide with validation
        # Sequential file naming: 01_title.png, 02_act1-intro.png, etc.
        output_filename = f"{idx:02d}_{slide_id}.png"
        output_path = output_dir / output_filename

        if generate_slide_image_with_retry(model, slide, cropped_bg, output_path):
            successful += 1

            # Save metadata
            metadata_path = output_path.with_suffix('.json')
            metadata = {
                "sequence": idx,
                "slide_id": slide_id,
                "title": title,
                "background_reference": background_file,
                "model": GEMINI_3_PRO_IMAGE,
                "generated_at": datetime.now().isoformat()
            }
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
        else:
            failed += 1

        print()

    # Summary
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
    print("Files are named sequentially (01_xxx.png, 02_xxx.png, etc.)")
    print("Import to presentation software in alphabetical order.")


if __name__ == '__main__':
    main()
