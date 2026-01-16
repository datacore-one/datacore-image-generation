#!/usr/bin/env python3
"""
Image Library Management

Manage image archive and prompt library:
- Build searchable index of all images
- Search by prompt keywords, date, service
- Rebuild index from metadata files
- Export prompt library

Usage:
    # Rebuild index from all metadata files
    python image-library.py rebuild --path ~/Data/2-datacore/2-projects/images

    # Search prompts
    python image-library.py search "mountain landscape"

    # Update index with new image
    python image-library.py update --image ./path/to/image.png

    # Export library
    python image-library.py export --format json --output library.json

    # List recent images
    python image-library.py list --limit 10
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict


def find_metadata_files(base_path: Path, service: str = None) -> List[Path]:
    """Find all metadata JSON files in archive."""
    metadata_files = []

    if service:
        search_path = base_path / service
    else:
        search_path = base_path

    for json_file in search_path.rglob("*.json"):
        # Skip index files
        if json_file.name in ["index.json", "midjourney-index.json", "library.json"]:
            continue

        # Only metadata files (have matching image file)
        image_file = json_file.with_suffix('.png')
        if image_file.exists():
            metadata_files.append(json_file)

    return metadata_files


def load_metadata(json_path: Path) -> Dict:
    """Load metadata from JSON file."""
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load {json_path}: {e}", file=sys.stderr)
        return None


def build_index(base_path: Path, service: str = None) -> List[Dict]:
    """Build searchable index from all metadata files."""
    print(f"Scanning {base_path} for images...")

    metadata_files = find_metadata_files(base_path, service)
    print(f"Found {len(metadata_files)} images")

    index = []
    for json_path in metadata_files:
        metadata = load_metadata(json_path)
        if metadata:
            # Add file path to metadata
            metadata["metadata_path"] = str(json_path)
            metadata["image_path"] = str(json_path.with_suffix('.png'))
            index.append(metadata)

    # Sort by creation date (newest first)
    index.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    return index


def save_index(index: List[Dict], output_path: Path):
    """Save index to JSON file."""
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(index, f, indent=2)
        print(f"Index saved: {output_path}")
    except Exception as e:
        print(f"Error saving index: {e}", file=sys.stderr)


def load_index(index_path: Path) -> List[Dict]:
    """Load index from JSON file."""
    try:
        with open(index_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load index: {e}", file=sys.stderr)
        return []


def search_index(index: List[Dict], query: str) -> List[Dict]:
    """Search index by keyword in prompt."""
    query_lower = query.lower()
    results = []

    for item in index:
        prompt = item.get("prompt", "").lower()
        if query_lower in prompt:
            results.append(item)

    return results


def cmd_rebuild(args):
    """Rebuild index from all metadata files."""
    base_path = Path(args.path).expanduser()

    if not base_path.exists():
        print(f"Error: Path not found: {base_path}", file=sys.stderr)
        sys.exit(1)

    # Build separate indices for each service
    services = ["midjourney", "gemini"]
    total_images = 0

    for service in services:
        service_path = base_path / service
        if not service_path.exists():
            continue

        print(f"\nBuilding index for {service}...")
        index = build_index(base_path, service)

        if index:
            index_path = service_path / "index.json"
            save_index(index, index_path)
            total_images += len(index)

    # Build unified library
    print(f"\nBuilding unified library...")
    full_index = build_index(base_path)
    library_path = base_path / "library.json"
    save_index(full_index, library_path)

    print(f"\nDone! Indexed {total_images} images")
    print(f"Unified library: {library_path}")


def cmd_search(args):
    """Search prompts by keyword."""
    base_path = Path(args.path).expanduser()
    library_path = base_path / "library.json"

    if not library_path.exists():
        print(f"Error: Library not found. Run 'rebuild' first.", file=sys.stderr)
        sys.exit(1)

    print(f"Loading library from {library_path}...")
    index = load_index(library_path)

    if not index:
        print("Library is empty or could not be loaded.", file=sys.stderr)
        sys.exit(1)

    print(f"Searching {len(index)} images for: {args.query}\n")

    results = search_index(index, args.query)

    if not results:
        print("No results found.")
        return

    print(f"Found {len(results)} result(s):\n")

    for i, item in enumerate(results[:args.limit], 1):
        service = item.get("service", "unknown")
        prompt = item.get("prompt", "No prompt")
        created_at = item.get("created_at", "Unknown date")
        image_path = item.get("image_path", "")

        # Format date
        try:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            date_str = dt.strftime("%Y-%m-%d")
        except:
            date_str = created_at

        print(f"{i}. [{service}] {date_str}")
        print(f"   Prompt: {prompt}")
        print(f"   Path: {image_path}")

        # Show parameters if available
        params = item.get("parameters", {})
        if params:
            param_strs = [f"{k}={v}" for k, v in params.items() if k != "model"]
            if param_strs:
                print(f"   Params: {', '.join(param_strs)}")

        print()


def cmd_update(args):
    """Update index with new image."""
    image_path = Path(args.image).expanduser()

    if not image_path.exists():
        print(f"Error: Image not found: {image_path}", file=sys.stderr)
        sys.exit(1)

    metadata_path = image_path.with_suffix('.json')
    if not metadata_path.exists():
        print(f"Error: Metadata not found: {metadata_path}", file=sys.stderr)
        sys.exit(1)

    metadata = load_metadata(metadata_path)
    if not metadata:
        sys.exit(1)

    # Determine service and base path
    service = metadata.get("service", "unknown")
    base_path = Path(args.path or "~/Data/2-datacore/2-projects/images").expanduser()

    # Load existing index
    index_path = base_path / service / "index.json"
    if index_path.exists():
        index = load_index(index_path)
    else:
        index = []

    # Add new item
    metadata["metadata_path"] = str(metadata_path)
    metadata["image_path"] = str(image_path)
    index.insert(0, metadata)  # Add to front (newest)

    # Save updated index
    save_index(index, index_path)

    # Update unified library
    library_path = base_path / "library.json"
    if library_path.exists():
        library = load_index(library_path)
    else:
        library = []

    library.insert(0, metadata)
    save_index(library, library_path)

    print(f"Updated index with: {image_path.name}")


def cmd_list(args):
    """List recent images."""
    base_path = Path(args.path).expanduser()
    library_path = base_path / "library.json"

    if not library_path.exists():
        print(f"Error: Library not found. Run 'rebuild' first.", file=sys.stderr)
        sys.exit(1)

    index = load_index(library_path)

    if not index:
        print("Library is empty.")
        return

    print(f"Recent images (showing {min(args.limit, len(index))} of {len(index)}):\n")

    for i, item in enumerate(index[:args.limit], 1):
        service = item.get("service", "unknown")
        prompt = item.get("prompt", "No prompt")
        created_at = item.get("created_at", "Unknown date")

        # Format date
        try:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            date_str = dt.strftime("%Y-%m-%d %H:%M")
        except:
            date_str = created_at

        # Truncate long prompts
        if len(prompt) > 60:
            prompt = prompt[:57] + "..."

        print(f"{i}. [{service:10s}] {date_str} - {prompt}")


def cmd_export(args):
    """Export library to file."""
    base_path = Path(args.path).expanduser()
    library_path = base_path / "library.json"

    if not library_path.exists():
        print(f"Error: Library not found. Run 'rebuild' first.", file=sys.stderr)
        sys.exit(1)

    index = load_index(library_path)

    if not index:
        print("Library is empty.")
        return

    output_path = Path(args.output)

    if args.format == "json":
        # Full export
        save_index(index, output_path)
    elif args.format == "csv":
        # CSV export (simplified)
        import csv
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Service", "Date", "Prompt", "Image Path"])

            for item in index:
                writer.writerow([
                    item.get("service", ""),
                    item.get("created_at", ""),
                    item.get("prompt", ""),
                    item.get("image_path", "")
                ])

        print(f"Exported {len(index)} items to: {output_path}")
    elif args.format == "markdown":
        # Markdown export
        with open(output_path, 'w') as f:
            f.write("# Image Library\n\n")

            for item in index:
                service = item.get("service", "unknown")
                prompt = item.get("prompt", "No prompt")
                created_at = item.get("created_at", "")
                image_path = item.get("image_path", "")

                try:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    date_str = dt.strftime("%Y-%m-%d")
                except:
                    date_str = created_at

                f.write(f"## {date_str} - {service}\n\n")
                f.write(f"**Prompt:** {prompt}\n\n")
                f.write(f"**Image:** `{image_path}`\n\n")

                params = item.get("parameters", {})
                if params:
                    f.write(f"**Parameters:**\n")
                    for k, v in params.items():
                        f.write(f"- {k}: {v}\n")
                    f.write("\n")

                f.write("---\n\n")

        print(f"Exported {len(index)} items to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Image Library Management',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Rebuild command
    rebuild_parser = subparsers.add_parser('rebuild', help='Rebuild index from metadata files')
    rebuild_parser.add_argument('--path', default='~/Data/2-datacore/2-projects/images',
                                help='Base archive path')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search prompts by keyword')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--path', default='~/Data/2-datacore/2-projects/images',
                               help='Base archive path')
    search_parser.add_argument('--limit', type=int, default=20, help='Max results')

    # Update command
    update_parser = subparsers.add_parser('update', help='Update index with new image')
    update_parser.add_argument('--image', required=True, help='Image file path')
    update_parser.add_argument('--path', default='~/Data/2-datacore/2-projects/images',
                               help='Base archive path')

    # List command
    list_parser = subparsers.add_parser('list', help='List recent images')
    list_parser.add_argument('--path', default='~/Data/2-datacore/2-projects/images',
                             help='Base archive path')
    list_parser.add_argument('--limit', type=int, default=10, help='Number to show')

    # Export command
    export_parser = subparsers.add_parser('export', help='Export library')
    export_parser.add_argument('--format', choices=['json', 'csv', 'markdown'],
                               default='json', help='Export format')
    export_parser.add_argument('--output', required=True, help='Output file path')
    export_parser.add_argument('--path', default='~/Data/2-datacore/2-projects/images',
                               help='Base archive path')

    args = parser.parse_args()

    # Route to command
    if args.command == 'rebuild':
        cmd_rebuild(args)
    elif args.command == 'search':
        cmd_search(args)
    elif args.command == 'update':
        cmd_update(args)
    elif args.command == 'list':
        cmd_list(args)
    elif args.command == 'export':
        cmd_export(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
