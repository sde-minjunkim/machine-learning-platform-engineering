import pandas as pd


prediction_mapper = {0: "<=50K", 1: ">50k"}


class InputMapper:
    def __init__(self, input_data, column_list):
        self.data = input_data
        self.column_list = column_list

    def generate_pandas_dataframe(self):
        dummyfied_input_data = pd.get_dummies(
            self.data, drop_first=True, sparse=False, dtype=float
        )
        transformed_input_data = dummyfied_input_data.reindex(
            columns=self.column_list, fill_value=0
        )
        return transformed_input_data


class OutputMapper:
    def __init__(self, prediction_value):
        self.prediction_value = prediction_value

    def map_prediction(self):
        return prediction_mapper.get(self.prediction_value)
