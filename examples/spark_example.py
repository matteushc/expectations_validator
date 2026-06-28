import os
from pathlib import Path

from pyspark.sql import SparkSession

from df_expectations_validator import validate_dataframe

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    os.environ.setdefault("SPARK_LOCAL_IP", "127.0.0.1")
    spark = (
        SparkSession.builder.appName("gx-spark-example")
        .master("local[*]")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")
    dataframe = spark.read.csv(
        str(PROJECT_ROOT / "data" / "customers.csv"),
        header=True,
        inferSchema=True,
    )

    result = validate_dataframe(
        dataframe=dataframe,
        config_path=str(PROJECT_ROOT / "config" / "customer_expectations.yaml"),
        engine="spark",
    )

    print(result.to_dict())
    spark.stop()


if __name__ == "__main__":
    main()
