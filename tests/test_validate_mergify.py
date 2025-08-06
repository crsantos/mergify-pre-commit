import pytest
import tempfile
import json
from pathlib import Path
from mergify_hook.validate_mergify import validate_mergify_file, main

def test_valid_mergify_config():
    valid_config = {
        "pull_request_rules": [
            {
                "name": "Auto merge",
                "conditions": ["check-success=ci"],
                "actions": {"merge": {"method": "merge"}}
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
        import yaml
        yaml.dump(valid_config, f)
        
    # Mock schema for testing
    schema = {"type": "object", "properties": {"pull_request_rules": {"type": "array"}}}
    
    assert validate_mergify_file(f.name, schema) == True
    Path(f.name).unlink()

def test_main_with_valid_files():
    # Test the main function
    assert main([]) == 0  # No files should return 0