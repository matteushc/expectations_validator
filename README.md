# DataFrame Expectations Validator

Validate pandas or Spark DataFrames with Great Expectations rules stored in a YAML file.

The project builds a Great Expectations suite at runtime from YAML, validates an in-memory DataFrame, and returns a JSON result with `valid: true` or `valid: false`.

## Install

```bash
cd expectations_validator
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[spark]"
```

If you only need pandas:

```bash
pip install -e .
```

## Run with pandas

```bash
python -m df_expectations_validator.cli \
  --engine pandas \
  --data data/customers.csv \
  --config config/customer_expectations.yaml
```

## Run with Spark

```bash
python -m df_expectations_validator.cli \
  --engine spark \
  --data data/customers.csv \
  --config config/customer_expectations.yaml
```

## YAML format

```yaml
suite_name: customer_quality_suite
expectations:
  - type: ExpectTableColumnsToMatchSet
    kwargs:
      column_set: [customer_id, email, age, country, signup_date]
      exact_match: true
  - type: ExpectColumnValuesToNotBeNull
    kwargs:
      column: customer_id
  - type: ExpectColumnValuesToBeBetween
    kwargs:
      column: age
      min_value: 18
      max_value: 100
```

`type` is the Great Expectations class name from `great_expectations.expectations`, and `kwargs` are passed directly to that expectation.

## Use from Python

```python
import pandas as pd

from df_expectations_validator import validate_dataframe

df = pd.read_csv("data/customers.csv")
result = validate_dataframe(df, "config/customer_expectations.yaml", engine="pandas")

print(result.valid)
print(result.to_dict())
```

