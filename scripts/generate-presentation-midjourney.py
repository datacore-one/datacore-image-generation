#!/usr/bin/env python3
"""
Batch Presentation Image Generator - Midjourney Edition

Reads presentation-prompts.yaml and generates all slide backgrounds
using Midjourney via Apiframe API.

Generates TWO versions of each slide:
1. WITH Organization style (pure blue, clean minimal)
2. WITHOUT style (baseline for comparison)

Usage:
    python generate-presentation-midjourney.py
    python generate-presentation-midjourney.py --slide-id title
    python generate-presentation-midjourney.py --style-only  # Only Organization style
    python generate-presentation-midjourney.py --baseline-only  # Only no-style
"""

import os
import sys
import yaml
import time
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path.home() / "Data/.datacore/env/.env")

# Import midjourney API functions
import importlib.util
spec = importlib.util.spec_from_file_location(
    "midjourney_api",
    Path(__file__).parent / "midjourney-api.py"
)
midjourney_api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(midjourney_api)

imagine = midjourney_api.imagine
wait_for_completion = midjourney_api.wait_for_completion
download_image = midjourney_api.download_image
save_metadata = midjourney_api.save_metadata


# Organization brand style suffix (from brand-prompts/organization.md)
ORG_STYLE = """clean minimal design, pure blue (#0000FF) accent color,
black and white base, geometric shapes, professional tech aesthetic,
data sovereignty theme, modern sans-serif feel --ar 16:9"""


def load_prompts(yaml_path: str) -> dict:
    """Load presentation prompts from YAML file."""
    with open(yaml_path, 'r') as f:
        return yaml.safe_load(f)


def load_org_style() -> str:
    """Load Organization style from brand prompts."""
    brand_file = Path(__file__).parent.parent / "brand-prompts/organization.md"
    if brand_file.exists():
        # Could parse the markdown, but we'll use the constant for now
        return ORG_STYLE
    return ORG_STYLE


def generate_slide(
    slide_id: str,
    prompt: str,
    output_dir: Path,
    with_style: bool = True,
    api_key: str = None
) -> tuple:
    """
    Generate a single slide image.

    Args:
        slide_id: Slide identifier (e.g., "title", "act1-title")
        prompt: Base prompt text
        output_dir: Directory to save images
        with_style: If True, append Organization style; if False, use prompt as-is
        api_key: Apiframe API key

    Returns:
        (success: bool, output_path: Path or None)
    """
    # Build full prompt
    if with_style:
        full_prompt = f"{prompt} {ORG_STYLE}"
        suffix = "-org"
    else:
        full_prompt = f"{prompt} --ar 16:9"
        suffix = "-baseline"

    print(f"  Prompt: {full_prompt[:100]}..." if len(full_prompt) > 100 else f"  Prompt: {full_prompt}")

    # Submit to Midjourney
    print("  Submitting to Midjourney...")
    result = imagine(full_prompt, api_key=api_key)

    if "error" in result:
        print(f"  ✗ Error: {result['error']}")
        return False, None

    task_id = result.get("task_id")
    if not task_id:
        print(f"  ✗ No task_id in response")
        return False, None

    print(f"  Task ID: {task_id}")
    print(f"  Waiting for completion (max 5 min)...")

    # Wait for completion
    final_result = wait_for_completion(task_id, api_key=api_key, max_wait=300, poll_interval=15)

    if "error" in final_result:
        print(f"  ✗ Error during generation: {final_result['error']}")
        return False, None

    status = final_result.get("status", "").lower()
    if status not in ["completed", "complete", "finished"]:
        print(f"  ✗ Generation failed with status: {status}")
        return False, None

    # Get image URL (try multiple fields based on API response structure)
    image_url = (
        final_result.get("original_image_url") or
        final_result.get("task_result", {}).get("image_url") or
        (final_result.get("image_urls", [None])[0] if final_result.get("image_urls") else None)
    )
    if not image_url:
        print(f"  ✗ No image URL in result")
        print(f"  Debug: {final_result}")
        return False, None

    # Download image
    output_filename = f"{slide_id}{suffix}.png"
    output_path = output_dir / output_filename

    print(f"  Downloading image...")
    if download_image(image_url, output_path):
        print(f"  ✓ Saved: {output_filename}")

        # Save metadata
        save_metadata(
            output_path,
            full_prompt,
            task_id,
            params={"with_style": with_style, "style": "org" if with_style else "baseline"},
            result=final_result
        )

        return True, output_path
    else:
        print(f"  ✗ Failed to download image")
        return False, None


def main():
    parser = argparse.ArgumentParser(
        description='Generate presentation images using Midjourney',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--prompts', '-p',
                        default='presentation-prompts.yaml',
                        help='Path to prompts YAML file')
    parser.add_argument('--slide-id', '-s',
                        help='Generate only specific slide by ID')
    parser.add_argument('--style-only', action='store_true',
                        help='Only generate Organization style versions')
    parser.add_argument('--baseline-only', action='store_true',
                        help='Only generate baseline (no style) versions')
    parser.add_argument('--output-dir', '-o',
                        help='Override output directory')
    parser.add_argument('--start-from',
                        help='Start from specific slide ID (skip earlier)')

    args = parser.parse_args()

    # Check API key
    api_key = os.environ.get('APIFRAME_API_KEY')
    if not api_key:
        print("Error: APIFRAME_API_KEY not found in environment", file=sys.stderr)
        print("\nSolution:", file=sys.stderr)
        print("  1. Get API key from: https://apiframe.ai", file=sys.stderr)
        print("  2. Add to .datacore/env/.env:", file=sys.stderr)
        print("     APIFRAME_API_KEY=af_...", file=sys.stderr)
        sys.exit(1)

    # Load prompts
    print(f"Loading prompts from {args.prompts}...")
    config = load_prompts(args.prompts)

    slides = config.get('slides', [])
    generation = config.get('generation', {})

    # Determine output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = Path(generation.get('output_dir', './output'))

    # Add midjourney subdirectory
    output_dir = output_dir / "midjourney"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Output directory: {output_dir}")
    print()

    # Filter slides if needed
    if args.slide_id:
        slides = [s for s in slides if s.get('id') == args.slide_id]
        if not slides:
            print(f"Error: Slide ID '{args.slide_id}' not found", file=sys.stderr)
            sys.exit(1)
        print(f"Generating only slide: {args.slide_id}\n")
    elif args.start_from:
        # Find index and skip earlier
        start_idx = next((i for i, s in enumerate(slides) if s.get('id') == args.start_from), 0)
        slides = slides[start_idx:]
        print(f"Starting from slide: {args.start_from}\n")

    # Determine which versions to generate
    generate_styled = not args.baseline_only
    generate_baseline = not args.style_only

    print(f"Generating:")
    if generate_styled:
        print("  ✓ Organization style versions")
    if generate_baseline:
        print("  ✓ Baseline (no style) versions")
    print()

    # Generate images
    total_slides = len(slides)
    total_versions = (1 if generate_styled else 0) + (1 if generate_baseline else 0)
    successful = 0
    failed = 0

    for idx, slide in enumerate(slides, 1):
        slide_id = slide.get('id', f'slide-{idx}')
        act = slide.get('act', 'Unknown')
        title = slide.get('title', 'Untitled')
        prompt = slide.get('prompt', '')

        print(f"[{idx}/{total_slides}] {slide_id}")
        print(f"  Act: {act}")
        print(f"  Title: {title}")
        print()

        # Generate styled version
        if generate_styled:
            print(f"  Generating WITH Organization style...")
            success, _ = generate_slide(
                slide_id,
                prompt,
                output_dir,
                with_style=True,
                api_key=api_key
            )
            if success:
                successful += 1
            else:
                failed += 1
            print()

        # Generate baseline version
        if generate_baseline:
            print(f"  Generating WITHOUT style (baseline)...")
            success, _ = generate_slide(
                slide_id,
                prompt,
                output_dir,
                with_style=False,
                api_key=api_key
            )
            if success:
                successful += 1
            else:
                failed += 1
            print()

        print()

    # Summary
    total_attempts = successful + failed
    print("=" * 60)
    print(f"Generation Complete")
    print("=" * 60)
    print(f"Total slides: {total_slides}")
    print(f"Versions per slide: {total_versions}")
    print(f"Total attempts: {total_attempts}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(successful/total_attempts*100):.1f}%")
    print()
    print(f"Images saved to: {output_dir}")
    print()

    # Next steps
    print("Next steps:")
    print("1. Review both versions (org style vs baseline)")
    print("2. Select which style works best")
    print("3. Generate any missing slides or variations")
    print("4. Import final selections into presentation")


if __name__ == '__main__':
    main()
