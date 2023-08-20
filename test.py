import os
import pandas as pd

from data_handler import DataHandler, MathHandler, MultipleChoiceHandler


if __name__ == "__main__":

    test_data_dir = os.path.join(os.getcwd(), "test_data_multi")

    parquet_file_path = os.path.join("raw_data", "math", "0000_1d.parquet")
    db = pd.read_parquet(parquet_file_path, engine="auto")

    print(db)
    print(len(db))

    # d = MultipleChoiceHandler(test_data_dir, data_config="derek-thomas--ScienceQA", clean=False)

    # data_returned = d.get_data(0, 1)

    # print("Returned rows: ", len(data_returned))
    # print(d.data)
