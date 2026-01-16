#!/usr/bin/env python3
"""
Batch Presentation Image Generator

Reads presentation-prompts.yaml and generates all slide backgrounds
using Gemini image generation.

Usage:
    python generate-presentation.py [--fast] [--preview] [--slide-id ID]
"""

import os
import sys
import yaml
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path.home() / "Data/.datacore/env/.env")

import google.generativeai as genai
from PIL import Image
from io import BytesIO


def load_prompts(yaml_path: str) -> dict:
    """Load presentation prompts from YAML file."""
    with open(yaml_path, 'r') as f:
        return yaml.safe_load(f)


def generate_image(model, prompt: str, style: str = None) -> bytes:
    """Generate single image from prompt."""
    try:
        # Build full prompt with style
        full_prompt = prompt
        if style:
            full_prompt = f"{prompt}\n\nStyle: {style}"

        response = model.generate_content(
            contents=[full_prompt],
            generation_config={
                "response_modalities": ["IMAGE"],
            }
        )

        for part in response.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                return part.inline_data.data

        print("Warning: No image in response", file=sys.stderr)
        return None

    except Exception as e:
        print(f"Error generating image: {e}", file=sys.stderr)
        return None


def save_image(image_data: bytes, output_path: Path) -> bool:
    """Save image to disk."""
    try:
        image = Image.open(BytesIO(image_data))

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        image.save(output_path, 'PNG', optimize=False)
        return True

    except Exception as e:
        print(f"Error saving image: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Generate presentation images from YAML prompts',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--prompts', '-p',
                        default='presentation-prompts.yaml',
                        help='Path to prompts YAML file')
    parser.add_argument('--fast', action='store_true',
                        help='Use Nano Banana (fast) model instead of Pro')
    parser.add_argument('--preview', action='store_true',
                        help='Generate only first slide as preview')
    parser.add_argument('--slide-id', '-s',
                        help='Generate only specific slide by ID')
    parser.add_argument('--variations', '-v', type=int, default=3,
                        help='Number of variations per slide (default: 3)')
    parser.add_argument('--output-dir', '-o',
                        help='Override output directory')

    args = parser.parse_args()

    # Check API key
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment", file=sys.stderr)
        print("\nSolution:", file=sys.stderr)
        print("  1. Get API key from: https://aistudio.google.com/apikey", file=sys.stderr)
        print("  2. Add to .datacore/env/.env:", file=sys.stderr)
        print("     GEMINI_API_KEY=AIza...", file=sys.stderr)
        sys.exit(1)

    # Load prompts
    print(f"Loading prompts from {args.prompts}...")
    config = load_prompts(args.prompts)

    slides = config.get('slides', [])
    generation = config.get('generation', {})

    # Determine model
    if args.fast:
        model_name = generation.get('model_fast', 'gemini-2.5-flash-image')
        print(f"Using FAST model: {model_name} (Nano Banana)")
    else:
        model_name = generation.get('model', 'gemini-3-pro-image-preview')
        print(f"Using PRO model: {model_name}")

    # Configure Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)

    # Determine output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = Path(generation.get('output_dir', './output'))

    print(f"Output directory: {output_dir}")
    print(f"Variations per slide: {args.variations}")
    print()

    # Filter slides if needed
    if args.preview:
        slides = slides[:1]
        print("PREVIEW MODE: Generating first slide only\n")
    elif args.slide_id:
        slides = [s for s in slides if s.get('id') == args.slide_id]
        if not slides:
            print(f"Error: Slide ID '{args.slide_id}' not found", file=sys.stderr)
            sys.exit(1)
        print(f"Generating only slide: {args.slide_id}\n")

    # Generate images
    total_slides = len(slides)
    successful = 0
    failed = 0

    for idx, slide in enumerate(slides, 1):
        slide_id = slide.get('id', f'slide-{idx}')
        act = slide.get('act', 'Unknown')
        title = slide.get('title', 'Untitled')
        prompt = slide.get('prompt', '')
        style = slide.get('style', '')

        print(f"[{idx}/{total_slides}] {slide_id}")
        print(f"  Act: {act}")
        print(f"  Title: {title}")
        print()

        # Generate variations
        for var in range(1, args.variations + 1):
            print(f"  Generating variation {var}/{args.variations}...", end=' ')

            image_data = generate_image(model, prompt, style)

            if image_data:
                # Construct output path
                if args.variations > 1:
                    filename = f"{slide_id}-v{var}.png"
                else:
                    filename = f"{slide_id}.png"

                output_path = output_dir / filename

                if save_image(image_data, output_path):
                    successful += 1
                    print(f"✓ Saved: {filename}")
                else:
                    failed += 1
                    print(f"✗ Failed to save")
            else:
                failed += 1
                print(f"✗ Failed to generate")

        print()

    # Summary
    total_attempts = successful + failed
    print("=" * 60)
    print(f"Generation Complete")
    print("=" * 60)
    print(f"Total attempts: {total_attempts}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(successful/total_attempts*100):.1f}%")
    print()
    print(f"Images saved to: {output_dir}")
    print()

    # Next steps
    print("Next steps:")
    print("1. Review generated images in output directory")
    print("2. Select best variation for each slide")
    print("3. Import into presentation software (Google Slides, Keynote, etc.)")
    print("4. Add text overlays and content")
    print("5. Test on projector for readability")


if __name__ == '__main__':
    main()
