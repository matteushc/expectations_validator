from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any
from pyspark.sql import SparkSession

import pandas as pd


def _read_csv(path: Path, engine: str) -> Any:
    if engine == "pandas":
        return pd.read_csv(path)

    os.environ.setdefault("SPARK_LOCAL_IP", "127.0.0.1")
    spark = (
        SparkSession.builder.appName("dataframe-expectations-validator")
        .master("local[*]")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")
    return spark.read.csv(str(path), header=True, inferSchema=True)