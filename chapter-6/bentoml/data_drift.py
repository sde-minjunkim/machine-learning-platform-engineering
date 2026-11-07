from evidently.report import Report
from evidently.ui.workspace import Workspace
import pandas
import datetime
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class MonitoringService:
    def __init__(
        self,
        report: Report,
        reference: pandas.DataFrame,
        workspace: Workspace,
        project_id: str,
        window_size: int,
    ):
        self.window_size = int(window_size)
        self.report = report
        self.new_rows = 0
        self.reference = reference
        self.workspace = workspace
        self.project_id = project_id
        self.current = pandas.DataFrame()

    def iterate(self, new_rows: pandas.DataFrame):
        rows_count = new_rows.shape[0]

        self.current = pandas.concat([self.current, new_rows], ignore_index=True)
        self.new_rows += rows_count
        current_size = self.current.shape[0]
        if current_size > self.window_size:
            self.current = self.current.iloc[-self.window_size :]
            self.current.reset_index(drop=True, inplace=True)
        if current_size < self.window_size:
            logger.info(
                f"Not enough data for measurement: {current_size} of {self.window_size}."
                f" Waiting more data"
            )
            return
        self.report.timestamp = datetime.datetime.now()
        logger.info("Running report")
        self.report.run(
            reference_data=self.reference,
            current_data=self.current,
        )
        self.workspace.add_report(project_id=self.project_id, report=self.report)
