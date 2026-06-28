from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class ExpectationConfig:
    type: str
    kwargs: dict[str, Any]


@dataclass(frozen=True)
class SuiteConfig:
    suite_name: str
    expectations: list[ExpectationConfig]
    result_format: str = "SUMMARY"
    
    
def load_yaml_config(path: str | Path) -> dict[str, Any]:
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as file:
        raw_config = yaml.safe_load(file) or {}

    if not isinstance(raw_config, dict):
        raise ValueError(f"Expectation config must be a YAML mapping: {config_path}")

    return raw_config


def load_suite_config(path: str | Path) -> SuiteConfig:
    raw_config = load_yaml_config(path)

    if not isinstance(raw_config, dict):
        raise ValueError(f"Expectation config must be a YAML mapping: {path}")

    suite_name = raw_config.get("name")
    raw_expectations = raw_config.get("expectations")

    if not isinstance(raw_expectations, list) or not raw_expectations:
        raise ValueError("Expectation config must contain a non-empty 'expectations' list.")

    expectations: list[ExpectationConfig] = []
    for index, raw_expectation in enumerate(raw_expectations, start=1):
        if not isinstance(raw_expectation, dict):
            raise ValueError(f"Expectation #{index} must be a mapping.")

        expectation_type = raw_expectation.get("type")
        kwargs = raw_expectation.get("kwargs", {})

        if not isinstance(expectation_type, str) or not expectation_type:
            raise ValueError(f"Expectation #{index} must define a non-empty 'type'.")
        if not isinstance(kwargs, dict):
            raise ValueError(f"Expectation #{index} 'kwargs' must be a mapping.")

        expectations.append(ExpectationConfig(type=expectation_type, kwargs=kwargs))

    return SuiteConfig(
        suite_name=str(suite_name),
        expectations=expectations,
        result_format=str(raw_config.get("meta", {}).get("result_format", "SUMMARY")),
    )

