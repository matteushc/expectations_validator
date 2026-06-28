__all__ = ["ValidationOutput", "validate_dataframe"]


def __getattr__(name: str):
    if name in __all__:
        from df_expectations_validator.validator import ValidationOutput, validate_dataframe

        return {
            "ValidationOutput": ValidationOutput,
            "validate_dataframe": validate_dataframe,
        }[name]

    raise AttributeError(f"module 'df_expectations_validator' has no attribute {name!r}")
