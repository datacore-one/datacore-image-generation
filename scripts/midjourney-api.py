#!/usr/bin/env python3
"""
Midjourney API Integration via Apiframe.ai

Generate images using Midjourney through the Apiframe REST API.
No Discord required - clean, reliable, production-ready.

Usage:
    # Generate an image
    python midjourney-api.py imagine "a red bike on a beach, cinematic"

    # With parameters
    python midjourney-api.py imagine "mountain landscape" --ar 16:9 --style raw --v 6.1

    # Check status of a generation
    python midjourney-api.py status <task_id>

    # Download completed image
    python midjourney-api.py download <task_id> --output ./images/

    # List recent generations
    python midjourney-api.py list --limit 10
"""

import os

# DIP-0047: image generation costs money on a third-party service.
from datacore.ledger import attests
import sys
import json
import time
import argparse
import requests
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
load_dotenv(Path.home() / "Data/.datacore/env/.env")


# Apiframe API configuration
APIFRAME_BASE_URL = "https://api.apiframe.ai"
APIFRAME_FETCH_URL = "https://api.apiframe.pro/fetch"

# Default output directory
DEFAULT_OUTPUT_DIR = Path(os.environ.get("DATACORE_ROOT", str(Path.home() / "Data"))) / "content/images/midjourney"


def get_api_key() -> str:
    """Get Apiframe API key from environment."""
    api_key = os.environ.get('APIFRAME_API_KEY')
    if not api_key:
        print("Error: APIFRAME_API_KEY not found", file=sys.stderr)
        print("\nSolution:", file=sys.stderr)
        print("  1. Get your API key from https://apiframe.ai", file=sys.stderr)
        print("  2. Add to .datacore/env/.env:", file=sys.stderr)
        print("     APIFRAME_API_KEY=your_key_here", file=sys.stderr)
        sys.exit(1)
    return api_key


def get_headers(api_key: str) -> dict:
    """Get API headers with authorization."""
    return {
        "Content-Type": "application/json",
        "Authorization": api_key
    }



@attests("spend.image", ref=lambda r: str(getattr(r, "id", None) or (r.get("id", "") if isinstance(r, dict) else "") or ""))

def imagine(prompt: str, params: dict = None, api_key: str = None) -> dict:
    """
    Send imagine request to Midjourney via Apiframe.

    Args:
        prompt: The image prompt
        params: Optional parameters (ar, style, v, mode, etc.)
        api_key: API key (defaults to env var)

    Returns:
        dict with task_id and status
    """
    api_key = api_key or get_api_key()

    payload = {"prompt": prompt}

    # Add optional parameters
    if params:
        # Aspect ratio
        if params.get('ar'):
            payload["aspect_ratio"] = params['ar']
        # Style
        if params.get('style'):
            payload["style"] = params['style']
        # Version
        if params.get('v'):
            payload["version"] = params['v']
        # Mode (fast/turbo)
        if params.get('mode'):
            payload["mode"] = params['mode']
        # Webhook for async notifications
        if params.get('webhook_url'):
            payload["webhook_url"] = params['webhook_url']
            if params.get('webhook_secret'):
                payload["webhook_secret"] = params['webhook_secret']

    try:
        response = requests.post(
            f"{APIFRAME_BASE_URL}/pro/imagine",
            headers=get_headers(api_key),
            json=payload
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                error_msg = error_detail.get('message', str(e))
            except:
                error_msg = e.response.text or str(e)
        return {"error": error_msg}


def fetch_status(task_id: str, api_key: str = None) -> dict:
    """
    Check status of a generation task.

    Args:
        task_id: The task ID from imagine request
        api_key: API key (defaults to env var)

    Returns:
        dict with status, progress, and result URLs when complete
    """
    api_key = api_key or get_api_key()

    try:
        response = requests.post(
            APIFRAME_FETCH_URL,
            headers=get_headers(api_key),
            json={"task_id": task_id}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                error_msg = error_detail.get('message', str(e))
            except:
                error_msg = e.response.text or str(e)
        return {"error": error_msg}


def download_image(url: str, output_path: Path) -> bool:
    """Download image from URL to local path."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return True
    except Exception as e:
        print(f"Error downloading image: {e}", file=sys.stderr)
        return False


def save_metadata(output_path: Path, prompt: str, task_id: str, params: dict = None, result: dict = None):
    """Save metadata JSON sidecar."""
    metadata_path = output_path.with_suffix('.json')

    metadata = {
        "service": "midjourney",
        "provider": "apiframe",
        "prompt": prompt,
        "task_id": task_id,
        "parameters": params or {},
        "created_at": datetime.now().isoformat(),
        "file": output_path.name
    }

    if result:
        metadata["api_result"] = result

    try:
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save metadata: {e}", file=sys.stderr)


def wait_for_completion(task_id: str, api_key: str = None, max_wait: int = 300, poll_interval: int = 10) -> dict:
    """
    Poll for task completion.

    Args:
        task_id: The task ID
        api_key: API key
        max_wait: Maximum wait time in seconds (default 5 minutes)
        poll_interval: Polling interval in seconds (default 10)

    Returns:
        Final status dict
    """
    api_key = api_key or get_api_key()
    elapsed = 0

    while elapsed < max_wait:
        result = fetch_status(task_id, api_key)

        if result.get('error'):
            return result

        status = result.get('status', '').lower()

        if status in ['completed', 'complete', 'finished']:
            return result
        elif status in ['failed', 'error']:
            return {"error": result.get('message', 'Generation failed'), "result": result}

        # Show progress
        progress = result.get('progress', 0)
        print(f"  Status: {status} ({progress}%) - waiting...", end='\r')

        time.sleep(poll_interval)
        elapsed += poll_interval

    return {"error": f"Timeout after {max_wait} seconds", "last_status": result}


def generate_and_download(prompt: str, params: dict = None, output_dir: Path = None, wait: bool = True) -> dict:
    """
    Complete workflow: generate image and download result.

    Args:
        prompt: Image prompt
        params: Generation parameters
        output_dir: Output directory (defaults to archive location)
        wait: Wait for completion (default True)

    Returns:
        dict with task_id, status, and local file paths
    """
    api_key = get_api_key()
    output_dir = output_dir or DEFAULT_OUTPUT_DIR

    # Step 1: Submit generation request
    print(f"Submitting prompt: {prompt[:50]}...")
    result = imagine(prompt, params, api_key)

    if result.get('error'):
        return result

    task_id = result.get('task_id')
    if not task_id:
        return {"error": "No task_id in response", "result": result}

    print(f"Task ID: {task_id}")

    if not wait:
        return {"task_id": task_id, "status": "submitted"}

    # Step 2: Wait for completion
    print("Waiting for generation...")
    final_result = wait_for_completion(task_id, api_key)

    if final_result.get('error'):
        return final_result

    print("\nGeneration complete!")

    # Step 3: Download images
    # Handle different response formats from Apiframe
    image_url = final_result.get('image_url') or final_result.get('url') or final_result.get('original_image_url')
    image_urls = final_result.get('image_urls', [])

    # If we have image_urls array, use those (Midjourney variations)
    # Otherwise fall back to single image_url
    if not image_urls and image_url:
        image_urls = [image_url]

    if not image_urls:
        return {"error": "No image URLs in result", "result": final_result}

    # Organize by date
    today = datetime.now()
    date_path = output_dir / today.strftime("%Y/%m/%d")

    downloaded_files = []
    for i, url in enumerate(image_urls):
        filename = f"mj-{task_id[:8]}-{i+1}.png"
        output_path = date_path / filename

        print(f"Downloading: {filename}...")
        if download_image(url, output_path):
            save_metadata(output_path, prompt, task_id, params, final_result)
            downloaded_files.append(str(output_path))

    return {
        "task_id": task_id,
        "status": "completed",
        "files": downloaded_files,
        "result": final_result
    }


# CLI Commands

def cmd_imagine(args):
    """Handle imagine command."""
    params = {}
    if args.ar:
        params['ar'] = args.ar
    if args.style:
        params['style'] = args.style
    if args.version:
        params['v'] = args.version
    if args.mode:
        params['mode'] = args.mode

    output_dir = Path(args.output) if args.output else DEFAULT_OUTPUT_DIR

    print(f"Generating image with Midjourney via Apiframe")
    print(f"  Prompt: {args.prompt}")
    if params:
        print(f"  Params: {params}")
    print()

    if args.no_wait:
        result = imagine(args.prompt, params)
        if result.get('error'):
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
        print(f"Task submitted: {result.get('task_id')}")
        print(f"\nCheck status with:")
        print(f"  python {sys.argv[0]} status {result.get('task_id')}")
    else:
        result = generate_and_download(args.prompt, params, output_dir)
        if result.get('error'):
            print(f"\nError: {result['error']}", file=sys.stderr)
            sys.exit(1)

        print(f"\nSaved to:")
        for f in result.get('files', []):
            print(f"  {f}")


def cmd_status(args):
    """Handle status command."""
    result = fetch_status(args.task_id)

    if result.get('error'):
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    status = result.get('status', 'unknown')
    progress = result.get('progress', 0)

    print(f"Task: {args.task_id}")
    print(f"Status: {status}")
    print(f"Progress: {progress}%")

    if status.lower() in ['completed', 'complete', 'finished']:
        # Handle both single image_url and image_urls array
        image_url = result.get('image_url') or result.get('url') or result.get('original_image_url')
        image_urls = result.get('image_urls', [])

        if image_urls:
            print(f"Image URLs ({len(image_urls)} variations):")
            for i, url in enumerate(image_urls):
                print(f"  [{i+1}] {url}")
        elif image_url:
            print(f"Image URL: {image_url}")

        if args.download:
            output_dir = Path(args.output) if args.output else DEFAULT_OUTPUT_DIR
            today = datetime.now()
            date_path = output_dir / today.strftime("%Y/%m/%d")

            # Download all variations if available
            urls_to_download = image_urls if image_urls else [image_url] if image_url else []

            for i, url in enumerate(urls_to_download):
                suffix = f"-{i+1}" if len(urls_to_download) > 1 else ""
                filename = f"mj-{args.task_id[:8]}{suffix}.png"
                output_path = date_path / filename

                print(f"\nDownloading to: {output_path}")
                if download_image(url, output_path):
                    prompt = result.get('prompt', 'Unknown prompt')
                    save_metadata(output_path, prompt, args.task_id, None, result)

            print("\nDone!")

    if args.json:
        print("\nFull response:")
        print(json.dumps(result, indent=2))


def cmd_download(args):
    """Handle download command."""
    result = fetch_status(args.task_id)

    if result.get('error'):
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    status = result.get('status', 'unknown')
    if status.lower() not in ['completed', 'complete', 'finished']:
        print(f"Task not complete (status: {status})", file=sys.stderr)
        sys.exit(1)

    image_url = result.get('image_url') or result.get('url')
    if not image_url:
        print("No image URL in result", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output) if args.output else DEFAULT_OUTPUT_DIR
    today = datetime.now()
    date_path = output_dir / today.strftime("%Y/%m/%d")

    filename = f"mj-{args.task_id[:8]}.png"
    output_path = date_path / filename

    print(f"Downloading to: {output_path}")
    if download_image(image_url, output_path):
        prompt = result.get('prompt', 'Unknown prompt')
        save_metadata(output_path, prompt, args.task_id, None, result)
        print("Done!")
    else:
        sys.exit(1)


def cmd_list(args):
    """Handle list command (placeholder - Apiframe may not support this)."""
    print("Note: Listing generations requires checking local metadata files.")
    print("Use the image-library.py script for searchable history:")
    print(f"  python image-library.py list --limit {args.limit}")


def main():
    parser = argparse.ArgumentParser(
        description='Midjourney API Integration via Apiframe.ai',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s imagine "a serene mountain landscape at sunset"
  %(prog)s imagine "cyberpunk city" --ar 16:9 --style raw
  %(prog)s status abc123def
  %(prog)s download abc123def --output ./my-images/
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Imagine command
    imagine_parser = subparsers.add_parser('imagine', help='Generate a new image')
    imagine_parser.add_argument('prompt', help='Image prompt')
    imagine_parser.add_argument('--ar', help='Aspect ratio (e.g., 16:9, 1:1, 9:16)')
    imagine_parser.add_argument('--style', help='Style (e.g., raw)')
    imagine_parser.add_argument('--version', '-v', help='Midjourney version (e.g., 6.1)')
    imagine_parser.add_argument('--mode', choices=['fast', 'turbo'], help='Generation mode')
    imagine_parser.add_argument('--output', '-o', help='Output directory')
    imagine_parser.add_argument('--no-wait', action='store_true', help='Submit and return immediately')

    # Status command
    status_parser = subparsers.add_parser('status', help='Check generation status')
    status_parser.add_argument('task_id', help='Task ID from imagine request')
    status_parser.add_argument('--download', '-d', action='store_true', help='Download if complete')
    status_parser.add_argument('--output', '-o', help='Output directory for download')
    status_parser.add_argument('--json', action='store_true', help='Show full JSON response')

    # Download command
    download_parser = subparsers.add_parser('download', help='Download completed image')
    download_parser.add_argument('task_id', help='Task ID')
    download_parser.add_argument('--output', '-o', help='Output directory')

    # List command
    list_parser = subparsers.add_parser('list', help='List recent generations')
    list_parser.add_argument('--limit', type=int, default=10, help='Number of items')

    args = parser.parse_args()

    if args.command == 'imagine':
        cmd_imagine(args)
    elif args.command == 'status':
        cmd_status(args)
    elif args.command == 'download':
        cmd_download(args)
    elif args.command == 'list':
        cmd_list(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
