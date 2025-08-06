from __future__ import annotations

import argparse
import json
import sys
import time
from collections.abc import Sequence
from pathlib import Path

import jsonschema
import requests
import yaml


def download_schema(schema_url: str = "https://docs.mergify.com/mergify-configuration-schema.json") -> dict:
    """Download the Mergify JSON schema."""
    try:
        response = requests.get(schema_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Failed to fetch Mergify schema: {e}", file=sys.stderr)
        sys.exit(1)


def get_mergify_schema(use_cache: bool = True, schema_url: str = "https://docs.mergify.com/mergify-configuration-schema.json") -> dict:
    """Get schema with caching support."""
    cache_file = Path.home() / '.cache' / 'mergify-schema.json'
    
    if use_cache and cache_file.exists():
        # Check if cache is less than 24 hours old
        if (time.time() - cache_file.stat().st_mtime) < 86400:
            with open(cache_file) as f:
                return json.load(f)
    
    # Download fresh schema
    schema = download_schema(schema_url)
    
    # Cache it
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_file, 'w') as f:
        json.dump(schema, f)
    
    return schema


def validate_mergify_file(filename: str, schema: dict) -> bool:
    """Validate a single Mergify configuration file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            if filename.endswith('.yaml') or filename.endswith('.yml'):
                config = yaml.safe_load(f)
            else:
                config = json.load(f)
        
        jsonschema.validate(config, schema)
        return True
        
    except yaml.YAMLError as e:
        print(f"{filename}: YAML parsing error - {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"{filename}: JSON parsing error - {e}")
        return False
    except jsonschema.ValidationError as e:
        print(f"{filename}: Schema validation error - {e.message}")
        if e.absolute_path:
            print(f"  at path: {' -> '.join(str(p) for p in e.absolute_path)}")
        return False
    except Exception as e:
        print(f"{filename}: Unexpected error - {e}")
        return False


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Mergify configuration files against the official schema"
    )
    parser.add_argument(
        'filenames', 
        nargs='*', 
        help='Mergify configuration filenames to validate'
    )
    parser.add_argument(
        '--schema-url',
        default='https://docs.mergify.com/mergify-configuration-schema.json',
        help='URL to the Mergify schema (default: official URL)'
    )
    
    args = parser.parse_args(argv)
    
    if not args.filenames:
        return 0
    
    # Download schema
    schema = get_mergify_schema(schema_url=args.schema_url)
    
    # Validate each file
    retval = 0
    for filename in args.filenames:
        if not validate_mergify_file(filename, schema):
            retval = 1
    
    return retval


if __name__ == '__main__':
    sys.exit(main())