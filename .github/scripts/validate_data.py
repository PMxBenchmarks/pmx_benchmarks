#!/usr/bin/env python3
"""
Validate benchmark data files.
"""

import sys
from pathlib import Path
import pandas as pd
import yaml

def validate_csv_file(file_path):
    """Validate a CSV file can be read."""
    errors = []
    warnings = []
    
    try:
        df = pd.read_csv(file_path)
        
        if len(df) == 0:
            warnings.append(f"{file_path.name}: File is empty")
        
        if df.isnull().all().any():
            warnings.append(f"{file_path.name}: Contains completely empty columns")
        
        return errors, warnings, df
        
    except Exception as e:
        errors.append(f"{file_path.name}: Failed to read CSV - {str(e)}")
        return errors, warnings, None

def validate_data_dictionary(dict_path, data_columns):
    """Validate data dictionary covers all columns.

    Accepts either a yspec-style YAML (preferred) or a legacy CSV dictionary.
    """
    errors = []
    warnings = []

    suffix = dict_path.suffix.lower()
    try:
        if suffix in ('.yml', '.yaml'):
            with open(dict_path) as f:
                spec = yaml.safe_load(f) or {}
            # yspec convention: top-level keys are column names, with reserved
            # keys (e.g. SETUP__) wrapped in trailing __ or single underscores.
            documented_cols = {
                k for k in spec.keys()
                if isinstance(k, str) and not k.endswith('__') and not k.startswith('_')
            }
            label = dict_path.name
        elif suffix == '.csv':
            dict_df = pd.read_csv(dict_path)
            required_columns = ['column_name', 'description', 'type']
            for col in required_columns:
                if col not in dict_df.columns:
                    errors.append(f"{dict_path.name} missing required column: {col}")
            if 'column_name' not in dict_df.columns:
                return errors, warnings
            documented_cols = set(dict_df['column_name'].tolist())
            label = dict_path.name
        else:
            errors.append(f"Unsupported data dictionary format: {dict_path.name}")
            return errors, warnings

        data_cols = set(data_columns)
        missing = data_cols - documented_cols
        if missing:
            errors.append(f"{label} missing columns: {sorted(missing)}")
        extra = documented_cols - data_cols
        if extra:
            warnings.append(f"{label} has extra columns: {sorted(extra)}")

    except Exception as e:
        errors.append(f"Failed to validate data dictionary: {str(e)}")

    return errors, warnings

def validate_train_test_consistency(train_df, test_df):
    """Validate train and test files have consistent structure."""
    errors = []
    warnings = []
    
    if train_df is None or test_df is None:
        return errors, warnings
    
    train_cols = set(train_df.columns)
    test_cols = set(test_df.columns)
    
    if train_cols != test_cols:
        errors.append(f"Train and test files have different columns")
        errors.append(f"  Train only: {train_cols - test_cols}")
        errors.append(f"  Test only: {test_cols - train_cols}")
    
    # Check data types match
    for col in train_cols & test_cols:
        if train_df[col].dtype != test_df[col].dtype:
            warnings.append(f"Column '{col}' has different dtypes in train/test")
    
    return errors, warnings

def main():
    """Main validation function."""
    benchmarks_dir = Path('benchmarks')
    
    if not benchmarks_dir.exists():
        print("No benchmarks directory found.")
        return 0
    
    all_errors = []
    all_warnings = []
    
    for benchmark_dir in benchmarks_dir.iterdir():
        if not benchmark_dir.is_dir():
            continue
        
        print(f"\nValidating data for: {benchmark_dir.name}")
        
        data_dir = benchmark_dir / 'data'
        if not data_dir.exists():
            all_errors.append(f"{benchmark_dir.name}: No data directory found")
            continue
        
        # Validate train.csv
        train_path = data_dir / 'train.csv'
        if train_path.exists():
            errors, warnings, train_df = validate_csv_file(train_path)
            all_errors.extend([f"{benchmark_dir.name}: {e}" for e in errors])
            all_warnings.extend([f"{benchmark_dir.name}: {w}" for w in warnings])
        else:
            train_df = None
        
        # Validate test.csv
        test_path = data_dir / 'test.csv'
        if test_path.exists():
            errors, warnings, test_df = validate_csv_file(test_path)
            all_errors.extend([f"{benchmark_dir.name}: {e}" for e in errors])
            all_warnings.extend([f"{benchmark_dir.name}: {w}" for w in warnings])
        else:
            test_df = None
        
        # Validate consistency
        if train_df is not None and test_df is not None:
            errors, warnings = validate_train_test_consistency(train_df, test_df)
            all_errors.extend([f"{benchmark_dir.name}: {e}" for e in errors])
            all_warnings.extend([f"{benchmark_dir.name}: {w}" for w in warnings])
            
            # Validate data dictionary (prefer YAML, fall back to CSV).
            yml_path = data_dir / 'data-dictionary.yml'
            csv_path = data_dir / 'data-dictionary.csv'
            dict_path = yml_path if yml_path.exists() else (csv_path if csv_path.exists() else None)
            if dict_path is not None:
                errors, warnings = validate_data_dictionary(dict_path, train_df.columns)
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
        print("\n✅ All data validations passed!")
        return 0

if __name__ == '__main__':
    sys.exit(main())
