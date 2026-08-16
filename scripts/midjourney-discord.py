#!/usr/bin/env python3
"""
Midjourney Discord API Integration

Interact with Midjourney bot via Discord API:
- Fetch historical prompts and images
- Send new /imagine commands
- Monitor generation status
- Download completed images

Usage:
    # Fetch all historical images
    python midjourney-discord.py fetch --all

    # Fetch images since date
    python midjourney-discord.py fetch --since "2025-01-01"

    # Send new prompt
    python midjourney-discord.py imagine "a serene mountain landscape" --ar 16:9

    # Check status
    python midjourney-discord.py status --prompt-id <message_id>

    # Download image
    python midjourney-discord.py download --prompt-id <message_id> --output ./output/
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
from urllib.parse import urlparse

from dotenv import load_dotenv
load_dotenv(Path.home() / "Data/.datacore/env/.env")


# Discord API configuration
DISCORD_API_BASE = "https://discord.com/api/v10"
MIDJOURNEY_BOT_ID = "936929561302675456"  # Official Midjourney bot ID


def get_headers(token: str) -> dict:
    """Get Discord API headers with authorization."""
    return {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "DiscordBot (Datacore, 1.0)"
    }


def fetch_channel_messages(channel_id: str, token: str, limit: int = 100, before: str = None) -> list:
    """Fetch messages from channel."""
    url = f"{DISCORD_API_BASE}/channels/{channel_id}/messages"
    params = {"limit": limit}
    if before:
        params["before"] = before

    try:
        response = requests.get(url, headers=get_headers(token), params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching messages: {e}", file=sys.stderr)
        return []


def extract_midjourney_data(message: dict) -> dict:
    """Extract Midjourney prompt and image URLs from message."""
    if not message.get("author") or message["author"].get("id") != MIDJOURNEY_BOT_ID:
        return None

    # Check for image attachments
    attachments = message.get("attachments", [])
    if not attachments:
        return None

    # Extract prompt from message content or embeds
    content = message.get("content", "")
    prompt = None

    # Try to extract prompt from content (usually formatted like "**prompt** - <username>")
    if "**" in content:
        parts = content.split("**")
        if len(parts) >= 2:
            prompt = parts[1].strip()

    # Extract images
    images = []
    for attachment in attachments:
        if attachment.get("content_type", "").startswith("image/"):
            images.append({
                "url": attachment["url"],
                "filename": attachment["filename"],
                "size": attachment.get("size", 0)
            })

    if not images:
        return None

    return {
        "message_id": message["id"],
        "timestamp": message["timestamp"],
        "prompt": prompt or "Unknown prompt",
        "images": images,
        "raw_content": content
    }


def download_image(url: str, output_path: Path) -> bool:
    """Download image from URL."""
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


def save_metadata(output_path: Path, data: dict):
    """Save metadata JSON sidecar."""
    metadata_path = output_path.with_suffix('.json')

    metadata = {
        "service": "midjourney",
        "prompt": data["prompt"],
        "parameters": data.get("parameters", {}),
        "created_at": data["timestamp"],
        "discord_message_id": data["message_id"],
        "file": output_path.name,
        "raw_content": data.get("raw_content", "")
    }

    try:
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save metadata: {e}", file=sys.stderr)



@attests("spend.image", ref=lambda r: str(getattr(r, "id", None) or (r.get("id", "") if isinstance(r, dict) else "") or ""))

def send_imagine_command(channel_id: str, token: str, prompt: str, params: str = "") -> dict:
    """Send /imagine command to Midjourney bot."""
    url = f"{DISCORD_API_BASE}/channels/{channel_id}/messages"

    full_prompt = f"/imagine prompt: {prompt}"
    if params:
        full_prompt += f" {params}"

    payload = {
        "content": full_prompt
    }

    try:
        response = requests.post(url, headers=get_headers(token), json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending command: {e}", file=sys.stderr)
        return None


def check_generation_status(channel_id: str, token: str, message_id: str) -> dict:
    """Check if generation is complete by fetching message."""
    url = f"{DISCORD_API_BASE}/channels/{channel_id}/messages/{message_id}"

    try:
        response = requests.get(url, headers=get_headers(token))
        response.raise_for_status()
        message = response.json()

        # Check for attachments (completed)
        if message.get("attachments"):
            return {"status": "completed", "message": message}
        else:
            return {"status": "processing", "message": message}
    except requests.exceptions.RequestException as e:
        print(f"Error checking status: {e}", file=sys.stderr)
        return {"status": "error", "message": None}


def cmd_fetch(args, token: str):
    """Fetch historical Midjourney images."""
    print(f"Fetching Midjourney images from channel {args.channel_id}...")

    all_data = []
    before = None
    total_messages = 0
    total_images = 0

    # Parse since date if provided
    since_timestamp = None
    if args.since:
        try:
            since_dt = datetime.fromisoformat(args.since)
            since_timestamp = since_dt.isoformat()
        except:
            print(f"Warning: Invalid date format for --since: {args.since}", file=sys.stderr)

    # Fetch messages in batches
    while True:
        messages = fetch_channel_messages(args.channel_id, token, limit=100, before=before)
        if not messages:
            break

        total_messages += len(messages)

        for message in messages:
            # Stop if we've reached the since date
            if since_timestamp and message["timestamp"] < since_timestamp:
                break

            data = extract_midjourney_data(message)
            if data:
                all_data.append(data)
                total_images += len(data["images"])

        # Break if we've hit the since date
        if since_timestamp and messages[-1]["timestamp"] < since_timestamp:
            break

        # Get next page
        before = messages[-1]["id"]

        print(f"Scanned {total_messages} messages, found {total_images} images...", end="\r")

        # Break if --all not specified (single batch only)
        if not args.all:
            break

    print(f"\nFound {total_images} images from {len(all_data)} prompts")

    # Download images
    if args.download:
        output_dir = Path(args.output or ".")
        downloaded = 0

        for data in all_data:
            # Organize by date
            timestamp = datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
            date_path = output_dir / timestamp.strftime("%Y/%m/%d")

            for i, image in enumerate(data["images"]):
                filename = f"mj-{data['message_id']}-{i+1}.png"
                output_path = date_path / filename

                if output_path.exists() and not args.force:
                    print(f"Skipping (exists): {output_path}")
                    continue

                print(f"Downloading: {filename}...")
                if download_image(image["url"], output_path):
                    save_metadata(output_path, data)
                    downloaded += 1

        print(f"\nDownloaded {downloaded} images to: {output_dir}")

    # Save index
    if args.save_index:
        index_path = Path(args.output or ".") / "midjourney-index.json"
        with open(index_path, 'w') as f:
            json.dump(all_data, f, indent=2)
        print(f"Index saved: {index_path}")


def cmd_imagine(args, token: str):
    """Send new /imagine command."""
    # Build parameters string
    params = []
    if args.ar:
        params.append(f"--ar {args.ar}")
    if args.style:
        params.append(f"--style {args.style}")
    if args.version:
        params.append(f"--v {args.version}")
    if args.params:
        params.append(args.params)

    params_str = " ".join(params)

    print(f"Sending to Midjourney:")
    print(f"  Prompt: {args.prompt}")
    if params_str:
        print(f"  Params: {params_str}")

    result = send_imagine_command(args.channel_id, token, args.prompt, params_str)

    if result:
        message_id = result["id"]
        print(f"\nSent! Message ID: {message_id}")
        print(f"Generation typically takes 1-2 minutes.")
        print(f"\nCheck status with:")
        print(f"  python {sys.argv[0]} status --prompt-id {message_id}")
    else:
        print("Failed to send command.", file=sys.stderr)
        sys.exit(1)


def cmd_status(args, token: str):
    """Check generation status."""
    print(f"Checking status for message {args.prompt_id}...")

    status = check_generation_status(args.channel_id, token, args.prompt_id)

    if status["status"] == "completed":
        print("✅ Generation complete!")
        message = status["message"]
        attachments = message.get("attachments", [])
        print(f"Found {len(attachments)} image(s)")

        if args.download:
            output_dir = Path(args.output or ".")
            for i, attachment in enumerate(attachments):
                filename = f"mj-{args.prompt_id}-{i+1}.png"
                output_path = output_dir / filename

                print(f"Downloading: {filename}...")
                download_image(attachment["url"], output_path)

            print(f"Downloaded to: {output_dir}")

    elif status["status"] == "processing":
        print("⏳ Still processing...")
    else:
        print("❌ Error checking status", file=sys.stderr)
        sys.exit(1)


def cmd_download(args, token: str):
    """Download completed images."""
    print(f"Downloading images for message {args.prompt_id}...")

    url = f"{DISCORD_API_BASE}/channels/{args.channel_id}/messages/{args.prompt_id}"

    try:
        response = requests.get(url, headers=get_headers(token))
        response.raise_for_status()
        message = response.json()

        attachments = message.get("attachments", [])
        if not attachments:
            print("No images found (generation may still be in progress)", file=sys.stderr)
            sys.exit(1)

        output_dir = Path(args.output or ".")
        data = extract_midjourney_data(message)

        for i, attachment in enumerate(attachments):
            filename = f"mj-{args.prompt_id}-{i+1}.png"
            output_path = output_dir / filename

            print(f"Downloading: {filename}...")
            if download_image(attachment["url"], output_path):
                if data:
                    save_metadata(output_path, data)

        print(f"Downloaded to: {output_dir}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Midjourney Discord API Integration',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Fetch command
    fetch_parser = subparsers.add_parser('fetch', help='Fetch historical images')
    fetch_parser.add_argument('--all', action='store_true',
                              help='Fetch all historical images (not just latest 100)')
    fetch_parser.add_argument('--since', help='Fetch images since date (YYYY-MM-DD)')
    fetch_parser.add_argument('--download', action='store_true', help='Download images')
    fetch_parser.add_argument('--force', action='store_true', help='Re-download existing files')
    fetch_parser.add_argument('--save-index', action='store_true', help='Save JSON index')
    fetch_parser.add_argument('--output', '-o', help='Output directory')

    # Imagine command
    imagine_parser = subparsers.add_parser('imagine', help='Send new /imagine command')
    imagine_parser.add_argument('prompt', help='Image prompt')
    imagine_parser.add_argument('--ar', help='Aspect ratio (e.g., 16:9)')
    imagine_parser.add_argument('--style', help='Style parameter (e.g., raw)')
    imagine_parser.add_argument('--version', '-v', help='Midjourney version (e.g., 6)')
    imagine_parser.add_argument('--params', help='Additional parameters')

    # Status command
    status_parser = subparsers.add_parser('status', help='Check generation status')
    status_parser.add_argument('--prompt-id', required=True, help='Discord message ID')
    status_parser.add_argument('--download', action='store_true', help='Download if complete')
    status_parser.add_argument('--output', '-o', help='Output directory')

    # Download command
    download_parser = subparsers.add_parser('download', help='Download completed images')
    download_parser.add_argument('--prompt-id', required=True, help='Discord message ID')
    download_parser.add_argument('--output', '-o', help='Output directory')

    # Global arguments
    parser.add_argument('--channel-id', help='Discord channel ID (or use MIDJOURNEY_CHANNEL_ID env)')
    parser.add_argument('--token', help='Discord token (or use MIDJOURNEY_DISCORD_TOKEN env)')

    args = parser.parse_args()

    # Get credentials
    token = args.token or os.environ.get('MIDJOURNEY_DISCORD_TOKEN')
    channel_id = args.channel_id or os.environ.get('MIDJOURNEY_CHANNEL_ID')

    if not token:
        print("Error: MIDJOURNEY_DISCORD_TOKEN not found", file=sys.stderr)
        print("\nSolution:", file=sys.stderr)
        print("  1. Get your Discord token:", file=sys.stderr)
        print("     - Open Discord in browser", file=sys.stderr)
        print("     - Open DevTools (F12) > Network tab", file=sys.stderr)
        print("     - Look for any XHR request", file=sys.stderr)
        print("     - Find 'authorization' header", file=sys.stderr)
        print("     - Copy the token", file=sys.stderr)
        print("  2. Add to .datacore/env/.env:", file=sys.stderr)
        print("     MIDJOURNEY_DISCORD_TOKEN=your_token_here", file=sys.stderr)
        print("\nWarning: NEVER share your Discord token!", file=sys.stderr)
        sys.exit(1)

    if not channel_id:
        print("Error: MIDJOURNEY_CHANNEL_ID not found", file=sys.stderr)
        print("\nSolution:", file=sys.stderr)
        print("  1. Enable Developer Mode in Discord Settings", file=sys.stderr)
        print("  2. Right-click Midjourney bot in DMs", file=sys.stderr)
        print("  3. Copy ID", file=sys.stderr)
        print("  4. Add to .datacore/env/.env:", file=sys.stderr)
        print("     MIDJOURNEY_CHANNEL_ID=your_channel_id_here", file=sys.stderr)
        sys.exit(1)

    # Route to command
    if args.command == 'fetch':
        args.channel_id = channel_id
        cmd_fetch(args, token)
    elif args.command == 'imagine':
        args.channel_id = channel_id
        cmd_imagine(args, token)
    elif args.command == 'status':
        args.channel_id = channel_id
        cmd_status(args, token)
    elif args.command == 'download':
        args.channel_id = channel_id
        cmd_download(args, token)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
