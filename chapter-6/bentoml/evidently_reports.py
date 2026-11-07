from evidently.metrics import ColumnDriftMetric
from evidently.metrics import ColumnSummaryMetric
from evidently.metrics import DatasetDriftMetric
from evidently.metrics import DatasetMissingValuesMetric
from evidently.report import Report

data_drift_report = Report(
    metrics=[
        DatasetDriftMetric(),
        DatasetMissingValuesMetric(),
        ColumnDriftMetric(column_name="Education"),
        ColumnSummaryMetric(column_name="Education"),
        ColumnDriftMetric(column_name="Marital-Status"),
        ColumnSummaryMetric(column_name="Marital-Status"),
        ColumnDriftMetric(column_name="Native_country"),
        ColumnSummaryMetric(column_name="Native_country"),
        ColumnDriftMetric(column_name="Occupation"),
        ColumnSummaryMetric(column_name="Occupation"),
        ColumnDriftMetric(column_name="Race"),
        ColumnSummaryMetric(column_name="Race"),
        ColumnDriftMetric(column_name="Relationship"),
        ColumnSummaryMetric(column_name="Relationship"),
        ColumnDriftMetric(column_name="Sex"),
        ColumnSummaryMetric(column_name="Sex"),
        ColumnDriftMetric(column_name="Workclass"),
        ColumnSummaryMetric(column_name="Workclass"),
    ],
)
