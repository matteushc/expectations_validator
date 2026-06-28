from __future__ import annotations

import argparse
import json
from pathlib import Path

from df_expectations_validator.load_data import _read_csv
from df_expectations_validator.validator import validate_dataframe
from df_expectations_validator.validator_checkpoint import validate_dataframe_with_checkpoint


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a pandas or Spark DataFrame with Great Expectations YAML rules."
    )
    parser.add_argument("--engine", choices=["pandas", "spark"], default="pandas")
    parser.add_argument("--data", required=True, help="Path to a CSV file.")
    parser.add_argument("--config", required=True, help="Path to expectations YAML.")
    parser.add_argument("--output", help="Optional path to write JSON validation output.")
    parser.add_argument("--checkpoint", action="store_true", help="Use checkpoint validation instead of direct validation.")
    
    args = parser.parse_args()

    dataframe = _read_csv(Path(args.data), args.engine)
    
    checkpoint_validation = args.checkpoint
    
    if checkpoint_validation:
        validation_output = validate_dataframe_with_checkpoint(args.config, dataframe)
    else:
        validation_output = validate_dataframe(
            dataframe=dataframe,
            config_path=args.config,
            engine=args.engine,
    )
    
    validation_output = validate_dataframe_with_checkpoint(args.config, dataframe)
    print(validation_output.describe())

    json_output = json.dumps(validation_output, indent=2, default=str)

    if args.output:
        Path(args.output).write_text(json_output + "\n", encoding="utf-8")

    return 0 if validation_output.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
