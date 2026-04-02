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

VALID_TASK_TYPES = {'regression', 'classification', 'counterfactual'}
VALID_CF_OUTPUT_TYPES = {'quantiles', 'summary_stats', 'probability'}
RANK_BASED_METRICS = {'auroc', 'auprc'}


def validate_tasks(tasks, benchmark_path):
    """Validate task schema: types, required fields, output_format, truth_file consistency."""
    errors = []

    for i, task in enumerate(tasks):
        label = f"Task {i+1} ({task.get('name', '?')})"
        task_type = task.get('type')

        if not task_type:
            # type is recommended but not required — handled as warning in validate_metadata
            continue

        if task_type not in VALID_TASK_TYPES:
            errors.append(
                f"{label}: invalid type '{task_type}', "
                f"must be one of {sorted(VALID_TASK_TYPES)}"
            )
            continue

        if not task.get('metric'):
            errors.append(f"{label}: missing required field 'metric'")

        output_format = task.get('output_format')
        if not output_format:
            errors.append(f"{label}: missing required field 'output_format'")
            continue

        if task_type in ('regression', 'classification'):
            if task.get('scenario'):
                errors.append(f"{label}: 'scenario' is not allowed for {task_type} tasks")
            if task.get('truth_file'):
                errors.append(f"{label}: 'truth_file' is not allowed for {task_type} tasks")

        if task_type == 'regression':
            if not task.get('target'):
                errors.append(f"{label}: 'target' is required for regression tasks")

        if task_type == 'classification':
            of_type = output_format.get('type')
            metric = task.get('metric', '')
            if metric in RANK_BASED_METRICS and of_type != 'probabilities':
                errors.append(
                    f"{label}: metric '{metric}' requires output_format.type 'probabilities', "
                    f"got '{of_type}'"
                )

        if task_type == 'counterfactual':
            of_type = output_format.get('type')

            if of_type == 'individual_predictions':
                errors.append(
                    f"{label}: output_format.type 'individual_predictions' is not valid "
                    f"for counterfactual tasks"
                )
            elif of_type not in VALID_CF_OUTPUT_TYPES:
                errors.append(
                    f"{label}: invalid counterfactual output_format.type '{of_type}', "
                    f"must be one of {sorted(VALID_CF_OUTPUT_TYPES)}"
                )

            if task.get('target'):
                errors.append(f"{label}: 'target' is not allowed for counterfactual tasks")

            if not task.get('scenario'):
                errors.append(f"{label}: 'scenario' is required for counterfactual tasks")

            truth_file = task.get('truth_file')
            if not truth_file:
                errors.append(f"{label}: 'truth_file' is required for counterfactual tasks")
            else:
                truth_path = benchmark_path / truth_file
                if not truth_path.exists():
                    errors.append(
                        f"{label}: truth_file '{truth_file}' not found at {truth_path}"
                    )
                else:
                    try:
                        with open(truth_path) as f:
                            truth = yaml.safe_load(f)
                        estimates = truth.get('estimates', {})

                        if of_type == 'quantiles':
                            declared = set(output_format.get('quantiles', []))
                            actual = set(estimates.keys())
                            if declared != actual:
                                errors.append(
                                    f"{label}: truth_file estimates keys {sorted(actual)} "
                                    f"do not match declared quantiles {sorted(declared)}"
                                )
                        elif of_type == 'summary_stats':
                            declared = set(output_format.get('stats', []))
                            actual = set(estimates.keys())
                            if declared != actual:
                                errors.append(
                                    f"{label}: truth_file estimates keys {sorted(actual)} "
                                    f"do not match declared stats {sorted(declared)}"
                                )
                        elif of_type == 'probability':
                            if 'p' not in estimates:
                                errors.append(
                                    f"{label}: truth_file estimates must contain key 'p' "
                                    f"for output_format.type 'probability'"
                                )
                    except yaml.YAMLError as e:
                        errors.append(
                            f"{label}: truth_file '{truth_file}' has invalid YAML: {e}"
                        )

    return errors

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
