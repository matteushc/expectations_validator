from pathlib import Path
from great_expectations.core.expectation_suite import ExpectationSuite
from great_expectations.data_context import EphemeralDataContext
from df_expectations_validator.config import load_yaml_config

import great_expectations as gx


def validate_dataframe_with_checkpoint(path: str | Path, df: object):
    
    context = gx.get_context(mode="ephemeral")
    suite_config = load_yaml_config(path)
    
    batch = batch_definition(context)
    
    suite = gx.core.ExpectationSuite(**suite_config)
    checkpoint_result =  validation_definition(context, df, suite, batch)
    return checkpoint_result


def batch_definition(context: EphemeralDataContext):
    
    batch_definition = (
        context.data_sources.add_spark(name="Spark Data Source")
        .add_dataframe_asset(name="Customer data")
        .add_batch_definition_whole_dataframe("batch definition")
    )
    return batch_definition


def validation_definition(context: EphemeralDataContext, df: object, suite: ExpectationSuite, batch_definition: dict):
    
    validation_definition = context.validation_definitions.add_or_update(
        gx.core.validation_definition.ValidationDefinition(
            name="validation definition",
            data=batch_definition,
            suite=suite,
        )
    )

    # Create Checkpoint, run Checkpoint, and capture result.
    checkpoint = context.checkpoints.add_or_update(
        gx.checkpoint.checkpoint.Checkpoint(
            name="checkpoint", validation_definitions=[validation_definition],
            result_format={
                    "result_format": "COMPLETE"
                },
        )
    )

    checkpoint_result = checkpoint.run(batch_parameters={"dataframe": df})
    return checkpoint_result
