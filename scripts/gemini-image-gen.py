#!/usr/bin/env python3
"""
Gemini Image Generation Script

Reusable script for generating images via Google Gemini AI.
Extracted from slides module for standalone use.

Usage:
    python gemini-image-gen.py --prompt "description" --output image.png
    python gemini-image-gen.py --prompt "description" --model gemini-3-pro-image-preview
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from io import BytesIO

from dotenv import load_dotenv
load_dotenv(Path.home() / "Data/.datacore/env/.env")

import google.generativeai as genai
from PIL import Image


def generate_image(model, prompt: str, reference_images=None, **kwargs) -> bytes:
    """Generate a single image from text prompt, optionally with reference images."""

    try:
        # Build contents list
        contents = []

        # Add reference images if provided
        if reference_images:
            for ref_img in reference_images:
                contents.append(ref_img)
            # Add instruction to use references
            if len(reference_images) > 0:
                contents.append("Use the provided reference image(s) as style and composition guidance for the following prompt:")

        # Add text prompt
        contents.append(prompt)

        response = model.generate_content(
            contents=contents,
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


def save_image(image_data: bytes, output_path: str) -> tuple:
    """Save image, return (success, size)."""
    try:
        image = Image.open(BytesIO(image_data))
        orig_size = image.size
        aspect = orig_size[0] / orig_size[1]

        print(f"Generated: {orig_size[0]}x{orig_size[1]} (aspect {aspect:.2f})")

        # Ensure output directory exists
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        image.save(output_path, 'PNG', optimize=False)
        return True, orig_size

    except Exception as e:
        print(f"Error saving image: {e}", file=sys.stderr)
        return False, (0, 0)


def save_metadata(output_path: str, prompt: str, model_name: str, size: tuple, **kwargs):
    """Save metadata JSON sidecar."""
    metadata_path = Path(output_path).with_suffix('.json')

    metadata = {
        "service": "gemini",
        "prompt": prompt,
        "parameters": {
            "model": model_name,
            "size": f"{size[0]}x{size[1]}",
            **kwargs
        },
        "created_at": datetime.now().isoformat(),
        "file": Path(output_path).name
    }

    try:
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"Metadata saved: {metadata_path}")
    except Exception as e:
        print(f"Warning: Could not save metadata: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description='Generate images using Google Gemini AI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python gemini-image-gen.py --prompt "a serene mountain landscape" --output image.png

  # Custom model
  python gemini-image-gen.py --prompt "abstract art" --model gemini-3-pro-image-preview

  # With metadata
  python gemini-image-gen.py --prompt "futuristic city" --output city.png --save-metadata

  # Multiple images
  python gemini-image-gen.py --prompt "variations of sunset" --output sunset.png --count 3
        """
    )

    parser.add_argument('--prompt', '-p', required=True,
                        help='Text prompt for image generation')
    parser.add_argument('--output', '-o', required=True,
                        help='Output file path (PNG)')
    parser.add_argument('--model', '-m',
                        default='gemini-3-pro-image-preview',
                        help='Gemini model (default: gemini-3-pro-image-preview)')
    parser.add_argument('--save-metadata', action='store_true',
                        help='Save metadata JSON sidecar')
    parser.add_argument('--count', '-n', type=int, default=1,
                        help='Number of images to generate (default: 1)')
    parser.add_argument('--style', '-s',
                        help='Style instructions (optional)')
    parser.add_argument('--reference', '-r', action='append',
                        help='Reference image path(s) for style/composition guidance (can use multiple times)')

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

    # Configure Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(args.model)

    # Load reference images if provided
    reference_images = None
    if args.reference:
        reference_images = []
        for ref_path in args.reference:
            try:
                ref_img = Image.open(ref_path)
                reference_images.append(ref_img)
                print(f"Loaded reference image: {ref_path}")
            except Exception as e:
                print(f"Warning: Could not load reference image {ref_path}: {e}", file=sys.stderr)

    # Build full prompt with style if provided
    full_prompt = args.prompt
    if args.style:
        full_prompt = f"{args.prompt}\n\nStyle: {args.style}"

    print(f"Generating {args.count} image(s) with {args.model}...")
    if reference_images:
        print(f"Using {len(reference_images)} reference image(s) for style guidance")
    print(f"Prompt: {args.prompt}\n")

    # Generate image(s)
    successful = 0
    for i in range(args.count):
        if args.count > 1:
            # Add variation number to filename
            output_path = Path(args.output)
            output_with_num = output_path.parent / f"{output_path.stem}-{i+1:02d}{output_path.suffix}"
        else:
            output_with_num = args.output

        print(f"Generating image {i+1}/{args.count}...")

        image_data = generate_image(model, full_prompt)

        if image_data:
            success, size = save_image(image_data, str(output_with_num))
            if success:
                successful += 1
                print(f"Saved: {output_with_num}\n")

                if args.save_metadata:
                    save_metadata(
                        str(output_with_num),
                        args.prompt,
                        args.model,
                        size,
                        style=args.style
                    )
        else:
            print(f"Failed to generate image {i+1}\n", file=sys.stderr)

    # Summary
    print(f"\nDone! {successful}/{args.count} image(s) generated")
    if successful > 0:
        if args.count == 1:
            print(f"Output: {args.output}")
        else:
            print(f"Output: {Path(args.output).parent}")


if __name__ == '__main__':
    main()
