from pathlib import Path

from df_expectations_validator.config import load_suite_config


def test_load_suite_config() -> None:
    config = load_suite_config(Path("config/customer_expectations.yaml"))

    assert config.suite_name == "customer_quality_suite"
    assert len(config.expectations) == 6
    assert config.expectations[0].type == "ExpectTableColumnsToMatchSet"

