from pathlib import Path

import pandas as pd

from df_expectations_validator import validate_dataframe

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    dataframe = pd.read_csv(PROJECT_ROOT / "data" / "customers.csv")
    result = validate_dataframe(
        dataframe=dataframe,
        config_path=str(PROJECT_ROOT / "config" / "customer_expectations.yaml"),
        engine="pandas",
    )

    print(result.to_dict())


if __name__ == "__main__":
    main()

