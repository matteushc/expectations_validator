import pkgutil
import inspect
from df_expectations_validator.validator import ValidationOutput, validate_dataframe
from df_expectations_validator import expectations

__all__ = ["ValidationOutput", "validate_dataframe"]

# Dynamically import all classes from expectations folder
for importer, modname, ispkg in pkgutil.iter_modules(expectations.__path__):
    module = __import__(f"df_expectations_validator.expectations.{modname}", fromlist=[modname])
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and obj.__module__.startswith("df_expectations_validator.expectations"):
            __all__.append(name)
            globals()[name] = obj


def __getattr__(name: str):
    if name in __all__:
        return globals().get(name)

    raise AttributeError(f"module 'df_expectations_validator' has no attribute {name!r}")
