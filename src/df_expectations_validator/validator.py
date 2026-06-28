from __future__ import annotations

from dataclasses import dataclass
import pkgutil
from typing import Any, Literal
from uuid import uuid4

import inspect
import great_expectations as gx

from df_expectations_validator.config import load_suite_config
from df_expectations_validator import expectations

Engine = Literal["pandas", "spark"]


@dataclass(frozen=True)
class ExpectationResult:
    type: str
    success: bool
    kwargs: dict[str, Any]
    details: dict[str, Any]


@dataclass(frozen=True)
class ValidationOutput:
    valid: bool
    suite_name: str
    engine: str
    evaluated_expectations: int
    successful_expectations: int
    unsuccessful_expectations: int
    results: list[ExpectationResult]

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "suite_name": self.suite_name,
            "engine": self.engine,
            "evaluated_expectations": self.evaluated_expectations,
            "successful_expectations": self.successful_expectations,
            "unsuccessful_expectations": self.unsuccessful_expectations,
            "results": [
                {
                    "type": result.type,
                    "success": result.success,
                    "kwargs": result.kwargs,
                    "details": result.details,
                }
                for result in self.results
            ],
        }


def validate_dataframe(
    dataframe: Any,
    config_path: str,
    engine: Engine = "pandas",
) -> ValidationOutput:
    suite_config = load_suite_config(config_path)
    batch = _build_batch(dataframe=dataframe, engine=engine)

    expectation_results: list[ExpectationResult] = []
    for expectation_config in suite_config.expectations:
        expectation = _create_expectation(expectation_config.type, expectation_config.kwargs)
        result = batch.validate(expectation, result_format=suite_config.result_format)
        result_dict = result.to_json_dict()

        expectation_results.append(
            ExpectationResult(
                type=expectation_config.type,
                success=bool(result_dict.get("success")),
                kwargs=expectation_config.kwargs,
                details=result_dict.get("result", {}),
            )
        )

    successful = sum(1 for result in expectation_results if result.success)
    total = len(expectation_results)

    return ValidationOutput(
        valid=successful == total,
        suite_name=suite_config.suite_name,
        engine=engine,
        evaluated_expectations=total,
        successful_expectations=successful,
        unsuccessful_expectations=total - successful,
        results=expectation_results,
    )


def _build_batch(dataframe: Any, engine: Engine):
    context = gx.get_context(mode="ephemeral")
    context.variables.progress_bars = {
        "globally": False,
        "metric_calculations": False,
    }
    unique_suffix = uuid4().hex
    data_source_name = f"{engine}_runtime_source_{unique_suffix}"
    data_asset_name = f"{engine}_runtime_asset"
    batch_definition_name = f"{engine}_runtime_batch"

    if engine == "pandas":
        data_source = context.data_sources.add_pandas(name=data_source_name)
    elif engine == "spark":
        data_source = context.data_sources.add_spark(name=data_source_name)
    else:
        raise ValueError("engine must be 'pandas' or 'spark'.")

    data_asset = data_source.add_dataframe_asset(name=data_asset_name)
    batch_definition = data_asset.add_batch_definition_whole_dataframe(batch_definition_name)
    return batch_definition.get_batch(batch_parameters={"dataframe": dataframe})


def _normalize_expectation_type(expectation_type: str) -> str:
    if expectation_type.startswith("expect_"):
        return "".join(part.capitalize() for part in expectation_type.split("_"))
    return expectation_type


def _create_expectation(expectation_type: str, kwargs: dict[str, Any]):
    _normalized_expectation_type = _normalize_expectation_type(expectation_type)
    
    try:
        expectation_class = getattr(gx.expectations, _normalized_expectation_type)
    except (AttributeError, ValueError):
        
        for _, modname, _ in pkgutil.iter_modules(expectations.__path__):
            module = __import__(f"df_expectations_validator.expectations.{modname}", fromlist=[modname])
            for name, obj in inspect.getmembers(module):
                if name == _normalized_expectation_type:
                    expectation_class = obj
                    break

    if expectation_class is None:
        raise ValueError(
            f"Unknown expectation type '{expectation_type}'. "
            "Use a class name from great_expectations.expectations."
        )

    return expectation_class(**kwargs)
