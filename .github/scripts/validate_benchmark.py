#!/usr/bin/env python3
"""
Validate benchmark submission structure and metadata.
"""

import os
import sys
from pathlib import Path
import yaml

def validate_benchmark_structure(benchmark_path):
    """Check that required files exist."""
    errors = []
    warnings = []
    
    required_files = [
        'index.qmd',
        'metadata.yml',
        'data/train.csv',
        'data/test.csv',
        'data/data-dictionary.csv'
    ]
    
    for file in required_files:
        file_path = benchmark_path / file
        if not file_path.exists():
            errors.append(f"Missing required file: {file}")
    
    return errors, warnings

def validate_metadata(metadata_path):
    """Validate metadata.yml structure."""
    errors = []
    warnings = []
    
    required_fields = [
        'name', 'title', 'version', 'date', 'authors',
        'description', 'keywords', 'data_type', 'tasks', 'license'
    ]
    
    try:
        with open(metadata_path, 'r') as f:
            metadata = yaml.safe_load(f)
        
        for field in required_fields:
            if field not in metadata:
                errors.append(f"Missing required metadata field: {field}")
        
        # Validate authors structure
        if 'authors' in metadata:
            if not isinstance(metadata['authors'], list) or len(metadata['authors']) == 0:
                errors.append("Authors must be a non-empty list")
            else:
                for i, author in enumerate(metadata['authors']):
                    if 'name' not in author:
                        errors.append(f"Author {i+1} missing 'name' field")
        
        # Validate tasks structure
        if 'tasks' in metadata:
            if not isinstance(metadata['tasks'], list) or len(metadata['tasks']) == 0:
                errors.append("Tasks must be a non-empty list")
            else:
                for i, task in enumerate(metadata['tasks']):
                    if 'name' not in task:
                        errors.append(f"Task {i+1} missing 'name' field")
                    if 'description' not in task:
                        warnings.append(f"Task {i+1} missing 'description' field")
                    if 'metric' not in task:
                        warnings.append(f"Task {i+1} missing 'metric' field")
        
    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML syntax: {e}")
    except FileNotFoundError:
        errors.append("metadata.yml file not found")
    
    return errors, warnings

def main():
    """Main validation function."""
    benchmarks_dir = Path('benchmarks')
    
    if not benchmarks_dir.exists():
        print("No benchmarks directory found.")
        return 0
    
    all_errors = []
    all_warnings = []
    
    # Find all benchmark directories
    for benchmark_dir in benchmarks_dir.iterdir():
        if not benchmark_dir.is_dir():
            continue
        
        print(f"\nValidating benchmark: {benchmark_dir.name}")
        
        # Validate structure
        errors, warnings = validate_benchmark_structure(benchmark_dir)
        all_errors.extend([f"{benchmark_dir.name}: {e}" for e in errors])
        all_warnings.extend([f"{benchmark_dir.name}: {w}" for w in warnings])
        
        # Validate metadata if file exists
        metadata_path = benchmark_dir / 'metadata.yml'
        if metadata_path.exists():
            errors, warnings = validate_metadata(metadata_path)
            all_errors.extend([f"{benchmark_dir.name}: {e}" for e in errors])
            all_warnings.extend([f"{benchmark_dir.name}: {w}" for w in warnings])
    
    # Print results
    if all_warnings:
        print("\n⚠️  WARNINGS:")
        for warning in all_warnings:
            print(f"  - {warning}")
    
    if all_errors:
        print("\n❌ ERRORS:")
        for error in all_errors:
            print(f"  - {error}")
        return 1
    else:
        print("\n✅ All validations passed!")
        return 0

if __name__ == '__main__':
    sys.exit(main())
