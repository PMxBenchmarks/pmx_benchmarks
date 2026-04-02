import pytest
from pathlib import Path
import yaml
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / '.github' / 'scripts'))
from validate_benchmark import validate_tasks


# ── helpers ───────────────────────────────────────────────────────────────────

def regression_task(**overrides):
    task = {
        'name': 'pred-accuracy',
        'type': 'regression',
        'target': 'DV',
        'output_format': {'type': 'individual_predictions', 'columns': ['ID', 'TIME', 'PRED']},
        'metric': 'rmse',
    }
    task.update(overrides)
    return task


def classification_task(**overrides):
    task = {
        'name': 'dropout-pred',
        'type': 'classification',
        'output_format': {'type': 'probabilities', 'columns': ['ID', 'P_DROPOUT']},
        'metric': 'auroc',
    }
    task.update(overrides)
    return task


def counterfactual_task(truth_file='tasks/cmax_truth.yml', **overrides):
    task = {
        'name': 'cmax-exceedance',
        'type': 'counterfactual',
        'scenario': '2x observed dose, same schedule',
        'output_format': {'type': 'quantiles', 'quantiles': [0.1, 0.5, 0.9]},
        'truth_file': truth_file,
        'metric': 'quantile_coverage',
    }
    task.update(overrides)
    return task


def write_truth_file(path, estimates):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        yaml.dump(
            {'scenario': 'test', 'n_sim': 100, 'population': 'all', 'estimates': estimates},
            f
        )


# ── Rule 1: type must be valid ────────────────────────────────────────────────

def test_valid_tasks_produce_no_errors(tmp_path):
    write_truth_file(tmp_path / 'tasks/cmax_truth.yml', {0.1: 1.0, 0.5: 2.0, 0.9: 3.0})
    tasks = [regression_task(), classification_task(), counterfactual_task()]
    errors = validate_tasks(tasks, tmp_path)
    assert errors == []


def test_invalid_type_is_error(tmp_path):
    errors = validate_tasks([regression_task(type='something_invalid')], tmp_path)
    assert any('invalid type' in e for e in errors)


def test_missing_type_is_warning_not_error(tmp_path):
    task = regression_task()
    del task['type']
    errors = validate_tasks([task], tmp_path)
    # Missing type produces a warning (returned in second element) not an error
    assert errors == []


# ── Rule 2: counterfactual cannot use individual_predictions ──────────────────

def test_counterfactual_individual_predictions_is_error(tmp_path):
    write_truth_file(tmp_path / 'tasks/cmax_truth.yml', {})
    task = counterfactual_task(
        output_format={'type': 'individual_predictions', 'columns': ['ID', 'PRED']}
    )
    errors = validate_tasks([task], tmp_path)
    assert any('individual_predictions' in e for e in errors)


# ── Rule 3: counterfactual requires scenario and truth_file ───────────────────

def test_counterfactual_missing_scenario_is_error(tmp_path):
    write_truth_file(tmp_path / 'tasks/cmax_truth.yml', {0.1: 1.0, 0.5: 2.0, 0.9: 3.0})
    task = counterfactual_task()
    del task['scenario']
    errors = validate_tasks([task], tmp_path)
    assert any("'scenario' is required" in e for e in errors)


def test_counterfactual_missing_truth_file_field_is_error(tmp_path):
    task = counterfactual_task()
    del task['truth_file']
    errors = validate_tasks([task], tmp_path)
    assert any("'truth_file' is required" in e for e in errors)


def test_counterfactual_with_target_field_is_error(tmp_path):
    write_truth_file(tmp_path / 'tasks/cmax_truth.yml', {0.1: 1.0, 0.5: 2.0, 0.9: 3.0})
    task = counterfactual_task(target='DV')
    errors = validate_tasks([task], tmp_path)
    assert any("'target' is not allowed" in e for e in errors)


# ── Rule 4: regression requires target; scenario/truth_file forbidden ─────────

def test_regression_missing_target_is_error(tmp_path):
    task = regression_task()
    del task['target']
    errors = validate_tasks([task], tmp_path)
    assert any("'target' is required" in e for e in errors)


def test_regression_with_scenario_is_error(tmp_path):
    errors = validate_tasks([regression_task(scenario='some intervention')], tmp_path)
    assert any("'scenario' is not allowed" in e for e in errors)


def test_regression_with_truth_file_is_error(tmp_path):
    errors = validate_tasks([regression_task(truth_file='tasks/foo.yml')], tmp_path)
    assert any("'truth_file' is not allowed" in e for e in errors)


# ── Rule 5: truth_file must exist on disk ────────────────────────────────────

def test_counterfactual_truth_file_not_on_disk_is_error(tmp_path):
    task = counterfactual_task(truth_file='tasks/nonexistent.yml')
    errors = validate_tasks([task], tmp_path)
    assert any('not found' in e for e in errors)


# ── Rule 6: truth_file estimates keys must match output_format ────────────────

def test_quantile_keys_match_is_ok(tmp_path):
    write_truth_file(tmp_path / 'tasks/cmax_truth.yml', {0.1: 1.0, 0.5: 2.0, 0.9: 3.0})
    task = counterfactual_task(
        output_format={'type': 'quantiles', 'quantiles': [0.1, 0.5, 0.9]}
    )
    errors = validate_tasks([task], tmp_path)
    assert errors == []


def test_quantile_keys_mismatch_is_error(tmp_path):
    write_truth_file(tmp_path / 'tasks/cmax_truth.yml', {0.1: 1.0, 0.5: 2.0})  # missing 0.9
    task = counterfactual_task(
        output_format={'type': 'quantiles', 'quantiles': [0.1, 0.5, 0.9]}
    )
    errors = validate_tasks([task], tmp_path)
    assert any('do not match declared quantiles' in e for e in errors)


def test_summary_stats_keys_match_is_ok(tmp_path):
    write_truth_file(tmp_path / 'tasks/er_truth.yml', {'mean': 12.4, 'sd': 3.1})
    task = counterfactual_task(
        truth_file='tasks/er_truth.yml',
        output_format={'type': 'summary_stats', 'stats': ['mean', 'sd']}
    )
    errors = validate_tasks([task], tmp_path)
    assert errors == []


def test_summary_stats_keys_mismatch_is_error(tmp_path):
    write_truth_file(tmp_path / 'tasks/er_truth.yml', {'mean': 12.4})  # missing sd
    task = counterfactual_task(
        truth_file='tasks/er_truth.yml',
        output_format={'type': 'summary_stats', 'stats': ['mean', 'sd']}
    )
    errors = validate_tasks([task], tmp_path)
    assert any('do not match declared stats' in e for e in errors)


def test_probability_truth_file_with_p_key_is_ok(tmp_path):
    write_truth_file(tmp_path / 'tasks/safety_truth.yml', {'p': 0.23})
    task = counterfactual_task(
        truth_file='tasks/safety_truth.yml',
        output_format={'type': 'probability', 'threshold': 100, 'direction': 'above'}
    )
    errors = validate_tasks([task], tmp_path)
    assert errors == []


def test_probability_truth_file_missing_p_key_is_error(tmp_path):
    write_truth_file(tmp_path / 'tasks/safety_truth.yml', {'probability': 0.23})  # wrong key
    task = counterfactual_task(
        truth_file='tasks/safety_truth.yml',
        output_format={'type': 'probability', 'threshold': 100, 'direction': 'above'}
    )
    errors = validate_tasks([task], tmp_path)
    assert any("key 'p'" in e for e in errors)


# ── Rule 7: rank-based metrics require probabilities ─────────────────────────

def test_auroc_with_class_predictions_is_error(tmp_path):
    task = classification_task(
        output_format={'type': 'class_predictions', 'columns': ['ID', 'CLASS']},
        metric='auroc',
    )
    errors = validate_tasks([task], tmp_path)
    assert any('auroc' in e and 'probabilities' in e for e in errors)


def test_auroc_with_probabilities_is_ok(tmp_path):
    task = classification_task(
        output_format={'type': 'probabilities', 'columns': ['ID', 'P_EVENT']},
        metric='auroc',
    )
    errors = validate_tasks([task], tmp_path)
    assert errors == []


def test_accuracy_with_class_predictions_is_ok(tmp_path):
    task = classification_task(
        output_format={'type': 'class_predictions', 'columns': ['ID', 'CLASS']},
        metric='accuracy',
    )
    errors = validate_tasks([task], tmp_path)
    assert errors == []
