import os

from data_handler import DataHandler


if __name__ == "__main__":

    test_data_dir = os.path.join(os.getcwd(), "test_data")

    d = DataHandler(test_data_dir, clean=False)

    data_returned = d.get_data(50, 201)

    print("Returned rows: ", len(data_returned))
    # print(d.data)
