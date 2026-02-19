#!/usr/bin/env python3
"""
Complete Slide Generator v10 - FINAL
- Tokenization & three-sided markets added
- Machine-readable ownership strengthened
- PartnerDrive free reframed with economics
- Akzidenz Grotesk typography
- Quality validation with retry
- Sequential naming

Usage:
    python generate-slides-v10-final.py
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


# V10 Slide definitions - FINAL with tokenization, machine-readable ownership, economic framing
SLIDES = [
    {
        "id": "title",
        "background": "title-org.png",
        "title": "We're Ready. Are You?",
        "subtitle": "The Ownership Paradigm\nConference 2026 • Speaker Name, Organization",
        "text_layout": "center"
    },
    {
        "id": "extraction-paradigm",
        "background": "cambridge-analytica-org.png",
        "title": "The Extraction Paradigm",
        "body": "Data economy: Shady backroom deals\nMarketplaces broken • Data locked\n\nYou create • Someone else owns\nSomeone else monetizes\n\nThis is breaking",
        "text_layout": "center"
    },
    {
        "id": "the-asymmetry",
        "background": "cambridge-analytica-org.png",
        "title": "AI Requires Machine-Readable Ownership",
        "body": "Hospital data: $0 balance sheet value\nBig Tech ($1.3T): $0 balance sheet value\n\nAgents need cryptographic proof\nMarkets need verification\nCFOs need recognized assets\n\nAI runs on verifiable ownership",
        "text_layout": "left"
    },
    {
        "id": "digital-freedom",
        "background": "shoe-size-org.png",
        "title": "Digital Age Freedom",
        "body": "ChatGPT knows more about you\nthan you know about yourself\n\nKnowledge locked in their vault\n\nFreedom starts with\nowning your data",
        "text_layout": "center"
    },
    {
        "id": "cambridge-2013",
        "background": "cambridge-analytica-org.png",
        "title": "Cambridge Analytica: 2013",
        "body": "\"Targeted ads change beliefs\nwithout awareness\"\n\n2018: Weaponized\n\nThe lesson:\nData powerful enough to influence\nbeyond our awareness\n\nOnly defense: Ownership",
        "text_layout": "left"
    },
    {
        "id": "cant-be-evil",
        "background": "act2-title-org.png",
        "title": "Don't Be Evil → Can't Be Evil",
        "body": "Change who controls it\nMake exploitation\narchitecturally impossible",
        "text_layout": "center"
    },
    # THREE CORE CONCEPTS
    {
        "id": "three-concepts-intro",
        "background": "act2-title-org.png",
        "title": "Three Core Concepts",
        "body": "Data Asset\nData Product\nData Business",
        "text_layout": "center"
    },
    {
        "id": "data-asset",
        "background": "fair-data-stack-org.png",
        "title": "Data Asset: What You OWN",
        "body": "Raw data • Stays private\nEncrypted vault • Never leaves\n\nAbsolute privacy",
        "text_layout": "center"
    },
    {
        "id": "data-product",
        "background": "three-sided-market-org.png",
        "title": "Data Product: What You MONETIZE",
        "body": "Created by agents • From assets\nSold or licensed\n\nGold mine → Gold bars",
        "text_layout": "center"
    },
    {
        "id": "data-business",
        "background": "agent-demo-split-org.png",
        "title": "Data Business: Autonomous Operation",
        "body": "Agent working 24/7\nCreating products • Finding buyers\nGenerating revenue\n\nPrivacy preserved • Value unlocked",
        "text_layout": "center"
    },
    # NEW: Three-sided markets & tokenization
    {
        "id": "three-sided-markets",
        "background": "three-sided-market-org.png",
        "title": "Three-Sided Markets",
        "body": "Agents: Create & consume products\nHumans: Invest in data businesses\nCapital: Flows to value creation\n\nMarketplaces transform",
        "text_layout": "center"
    },
    {
        "id": "tokenization",
        "background": "fair-data-stack-org.png",
        "title": "Data Business Tokenization",
        "body": "Like going public—for data\n\nFundraising • Growth • M&A\nSmart contracts distribute revenue\n\nTransparent • Auditable • Compliant\n\nData becomes Real World Assets",
        "text_layout": "center"
    },
    {
        "id": "self-sovereign-why",
        "background": "fair-data-stack-org.png",
        "title": "Why Self-Sovereign Infrastructure",
        "body": "Data on AWS = NFT on AWS\nYou have token\nAsset controlled by someone else\n\nSelf-sovereign:\nYour data • Your keys • Your proof\n\nUniversal: Works for everyone",
        "text_layout": "center"
    },
    {
        "id": "self-sovereign-ready",
        "background": "partnerdrive-demo-org.png",
        "title": "Ready to Be Battle Tested",
        "body": "✓ Decentralized storage • Live now\n✓ PartnerDrive: Your vault • Free forever\n✓ Data Escrow • Operating now\n\nInfrastructure exists\nFirst pilot projects starting",
        "text_layout": "left"
    },
    {
        "id": "agent-first",
        "background": "agent-demo-split-org.png",
        "title": "Agent-First Infrastructure",
        "body": "Built for AI agents\nModel Context Protocol (MCP)\n\nNot retrofitted APIs\nNative agent interfaces\n\nAgent-native • Ready now",
        "text_layout": "center"
    },
    {
        "id": "agents-drive-everything",
        "background": "agent-demo-split-org.png",
        "title": "Agents: Enablers & Fast-Trackers",
        "body": "Create products from assets\nGenerate supply AND demand\n\nHuman: Months\nAgent: 90 seconds",
        "text_layout": "center"
    },
    {
        "id": "fds-principles",
        "background": "fair-data-stack-org.png",
        "title": "PartnerOrg Principles",
        "body": "10 ethical constraints\n\nOwnership • Privacy • Control\nConsent • Transparency\n\nEthics by design\nBuilders: Just use the tools",
        "text_layout": "center"
    },
    {
        "id": "partnerdrive-free",
        "background": "partnerdrive-demo-org.png",
        "title": "Why PartnerDrive Is Free",
        "body": "Value isn't in the vault\nIt's in what happens on top\n\nRoads analogy: Free access\nCommerce generates value\n\nInfrastructure free\nTransactions generate revenue",
        "text_layout": "center"
    },
    # LIVE PROOF
    {
        "id": "demo-intro",
        "background": "act3-title-org.png",
        "title": "Three Concepts in Action",
        "body": "Live proof\nOperating now",
        "text_layout": "center"
    },
    {
        "id": "demo-asset-layer",
        "background": "partnerdrive-demo-org.png",
        "title": "Layer 1: Data Asset (Private)",
        "body": "Davos event intelligence\nDecentralized storage (encrypted)\nAgent access: Native MCP\nStatus: Never leaves vault\n\nPrivacy: Absolute",
        "text_layout": "left"
    },
    {
        "id": "demo-product-layer",
        "background": "three-sided-market-org.png",
        "title": "Layer 2: Data Product (Monetized)",
        "body": "Product: Networking Intelligence API\nAgent creates from asset\nWhat's sold: Insights (NOT raw data)\n\nPrice: $3 per query",
        "text_layout": "left"
    },
    {
        "id": "demo-business-layer",
        "background": "agent-demo-split-org.png",
        "title": "Layer 3: Data Business (24/7)",
        "body": "Operating autonomously\nThis week: 47 transactions\nRevenue: $141\n\nWhile you listen\nyour agent could be working",
        "text_layout": "center"
    },
    {
        "id": "ethereum-proof",
        "background": "etherscan-qr-org.png",
        "title": "Verify on Ethereum",
        "body": "Mainnet transactions\nScan QR • Verify yourself\n\nNot theory • Infrastructure",
        "text_layout": "center"
    },
    # COLLABORATIVE OPPORTUNITY
    {
        "id": "infrastructure-for-all",
        "background": "who-participates-org.png",
        "title": "Infrastructure for All",
        "body": "Like Tim Berners-Lee:\nGave web away\n\nInfrastructure works when\neveryone builds on it",
        "text_layout": "center"
    },
    {
        "id": "everyone-participates",
        "background": "who-participates-org.png",
        "title": "Everyone Participates",
        "body": "Individuals • Researchers\nOrganizations • States • AI builders\n\nEveryone contributes\nEveryone benefits",
        "text_layout": "center"
    },
    {
        "id": "its-early",
        "background": "act5-title-org.png",
        "title": "It's Early - That's the Opportunity",
        "body": "Like internet 1995\nLike cloud 2008\nLike AI 2020\n\nThe race is on",
        "text_layout": "center"
    },
    {
        "id": "first-movers",
        "background": "timeline-org.png",
        "title": "First Movers Set Standards",
        "body": "ERC-3643 • PartnerOrg principles • Decentralized storage\n\nRails get laid once\n\nStandards being set NOW",
        "text_layout": "center"
    },
    {
        "id": "liability-to-asset",
        "background": "fair-data-stack-org.png",
        "title": "Liability → Asset",
        "body": "Today: GDPR fines • Breaches • Zero value\n\nOwnership paradigm:\nBalance sheet recognition\nRevenue streams • Liquidity\nLending against data value\nM&A reflects true worth",
        "text_layout": "left"
    },
    {
        "id": "agents-market-makers",
        "background": "agent-demo-split-org.png",
        "title": "Agents = Market Makers",
        "body": "Turn assets into products\nGenerate supply AND demand\n\nData businesses:\n24/7 autonomous revenue",
        "text_layout": "center"
    },
    {
        "id": "readiness-levels",
        "background": "timeline-org.png",
        "title": "Three Levels of Readiness",
        "body": "Level 0: Extraction paradigm\nLevel 1: Awareness\nLevel 2: Infrastructure (first movers)\nLevel 3: Operational (18-24 months)\n\nRace is wide open",
        "text_layout": "left"
    },
    {
        "id": "are-you-ready",
        "background": "act6-title-org.png",
        "title": "Are You Ready?",
        "body": "For the ownership paradigm\n\nYour AI strategy\nstarts with data ownership",
        "text_layout": "center"
    },
    {
        "id": "paradigm-shift",
        "background": "closing-org.png",
        "title": "The Paradigm Shift",
        "body": "Extraction → Ownership\nSurveillance → Fair data economy\n'Don't be evil' → 'Can't be evil'",
        "text_layout": "center"
    },
    {
        "id": "how-it-works",
        "background": "fair-data-stack-org.png",
        "title": "How It Works",
        "body": "Assets stay private\nProducts get monetized\nBusinesses run autonomously\n\nSelf-sovereign infrastructure\nAgents drive it all",
        "text_layout": "center"
    },
    {
        "id": "thank-you",
        "background": "title-org.png",
        "title": "We're Ready. Are You?",
        "body": "Freedom starts with ownership\n\nLet's build it. Together.\n\nSpeaker Name • Organization",
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
    prompt_parts.append("- Typography: Akzidenz Grotesk (stylish, high-end sans-serif - clean, technical, modern)")
    prompt_parts.append("- Use the provided image as background")
    prompt_parts.append("- Place text on the EMPTY/PLAIN areas of background, NOT on busy design elements")
    prompt_parts.append("- Text must have excellent contrast and readability")
    prompt_parts.append("- Generous white space around text")
    prompt_parts.append("- Strong visual hierarchy (title > subtitle > body)")
    prompt_parts.append("- Clean, minimal, high-end aesthetic with stylish typography")
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
        description='Generate v10 presentation slides - FINAL'
    )

    datacore_root = os.environ.get("DATACORE_ROOT", os.path.expanduser("~/Data"))
    parser.add_argument('--backgrounds-dir',
                        default=os.path.join(datacore_root, '1-teamspace/1-tracks/comms/presentations/keynote-visuals/midjourney'),
                        help='Directory containing Midjourney backgrounds')
    parser.add_argument('--output-dir', '-o',
                        default=os.path.join(datacore_root, '1-teamspace/1-tracks/comms/presentations/keynote-visuals/v10-final-slides'),
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
    print(f"Version: v10 - FINAL")
    print(f"Key concepts: Asset → Product → Business + Tokenization")
    print(f"Typography: Akzidenz Grotesk (stylish, high-end sans-serif)")
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
                "version": "v10-final",
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
    print("V10 - FINAL:")
    print("✓ Tokenization & three-sided markets")
    print("✓ Machine-readable ownership")
    print("✓ Economic framing for PartnerDrive free")
    print("✓ Akzidenz Grotesk typography (stylish)")
    print("✓ Sequential naming (01_xxx.png, 02_xxx.png, etc.)")


if __name__ == '__main__':
    main()
