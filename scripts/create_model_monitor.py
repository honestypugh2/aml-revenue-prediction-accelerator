"""Create the Azure ML model-monitoring schedule for the net-revenue model.

The YAML in ``mlops/monitoring/monitoring-schedule.yml`` documents the intended
signals, but ``azure-ai-ml`` has no ``load_schedule`` loader, so the schedule is
built with SDK entities here.

Prerequisites:

1. Register the referenced data assets first:
   ``revenue_training_reference``, ``revenue_inference_recent``,
   ``revenue_predictions_reference``, ``revenue_predictions_recent``.
2. If the workspace uses identity-based datastore auth
   (``system_datastores_auth_mode = identity``, required when the storage
   account has shared keys disabled), the workspace must also have a
   **user-assigned identity**. Serverless Spark monitoring jobs authenticate
   through it, and the system-assigned identity alone is rejected with
   "no User-Assigned Identity present in the workspace".

   Attaching a UAI moves the workspace to ``SystemAssigned,UserAssigned``,
   which cannot be reverted to system-assigned only.

Usage:
    uv run python scripts/create_model_monitor.py --env dev
"""

from __future__ import annotations

import argparse

from azure.ai.ml.constants import MonitorDatasetContext
from azure.ai.ml.entities import (
    AlertNotification,
    CategoricalDriftMetrics,
    DataDriftMetricThreshold,
    DataDriftSignal,
    DataQualityMetricsCategorical,
    DataQualityMetricsNumerical,
    DataQualityMetricThreshold,
    DataQualitySignal,
    MonitorDefinition,
    MonitorSchedule,
    NumericalDriftMetrics,
    PredictionDriftMetricThreshold,
    PredictionDriftSignal,
    ProductionData,
    RecurrenceTrigger,
    ReferenceData,
    ServerlessSparkCompute,
)
from azure.ai.ml.entities._inputs_outputs import Input

from revenue_prediction.config.loader import load_settings
from revenue_prediction.integrations.azureml.client import get_ml_client

SCHEDULE_NAME = "revenue-model-monitoring"


def _folder(asset: str) -> Input:
    return Input(type="uri_folder", path=asset)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", default="dev")
    parser.add_argument("--emails", nargs="*", default=[])
    args = parser.parse_args()

    settings = load_settings(args.env)
    client = get_ml_client(settings.azure_ml)

    inference = ProductionData(
        input_data=_folder("azureml:revenue_inference_recent:1"),
        data_context=MonitorDatasetContext.MODEL_INPUTS,
    )
    training = ReferenceData(
        input_data=_folder("azureml:revenue_training_reference:1"),
        data_context=MonitorDatasetContext.TRAINING,
    )
    predictions = ProductionData(
        input_data=_folder("azureml:revenue_predictions_recent:1"),
        data_context=MonitorDatasetContext.MODEL_OUTPUTS,
    )
    predictions_ref = ReferenceData(
        input_data=_folder("azureml:revenue_predictions_reference:1"),
        data_context=MonitorDatasetContext.MODEL_OUTPUTS,
    )

    signals = {
        "input_drift": DataDriftSignal(
            production_data=inference,
            reference_data=training,
            metric_thresholds=DataDriftMetricThreshold(
                numerical=NumericalDriftMetrics(jensen_shannon_distance=0.1),
                categorical=CategoricalDriftMetrics(jensen_shannon_distance=0.1),
            ),
        ),
        "prediction_drift": PredictionDriftSignal(
            production_data=predictions,
            reference_data=predictions_ref,
            metric_thresholds=PredictionDriftMetricThreshold(
                numerical=NumericalDriftMetrics(jensen_shannon_distance=0.1),
            ),
        ),
        "data_quality": DataQualitySignal(
            production_data=inference,
            reference_data=training,
            metric_thresholds=DataQualityMetricThreshold(
                numerical=DataQualityMetricsNumerical(null_value_rate=0.05),
                categorical=DataQualityMetricsCategorical(null_value_rate=0.05),
            ),
        ),
    }

    definition = MonitorDefinition(
        compute=ServerlessSparkCompute(instance_type="standard_e4s_v3", runtime_version="3.4"),
        monitoring_signals=signals,
        alert_notification=AlertNotification(emails=args.emails) if args.emails else None,
    )

    schedule = MonitorSchedule(
        name=SCHEDULE_NAME,
        trigger=RecurrenceTrigger(frequency="week", interval=1),
        create_monitor=definition,
    )

    created = client.schedules.begin_create_or_update(schedule).result()
    print(f"monitor   : {created.name}")
    print(f"enabled   : {created.is_enabled}")
    print(f"signals   : {', '.join(signals)}")


if __name__ == "__main__":
    main()
