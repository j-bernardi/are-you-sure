import os

from data_handler import DataHandler
from plotter import plotter

test_sums = [
    "5 + 10",
    "10 - 2",
    "10 * 6"
]

test_qas = [(x, eval(x)) for x in test_sums]


#### TODO ###
# May want to filter only for answers which are integers. 
#   It seems a tough test / not indicative if the model is wrong both times.
#   TODO - check whether this is the case or if I can truncate the raw answers to 2 decimal places.
#
# Also when not an integer, it seems to be giving an answer like "squiggly equals" rather than just equals.
#  FIXED: just add it to the regex.


if __name__ == "__main__":

    CLEAN_DATA_LOAD = False
    CLEAN_ANSWERS = False
    EXPERIMENT_RANGE = (0, 5)

    data_handler = DataHandler(os.path.join(os.getcwd(), "data"), clean=CLEAN_DATA_LOAD)
    data_handler.get_data(*EXPERIMENT_RANGE)

    results = {
        "correct_and_changed": [],
        "correct_and_not_changed": [],
        "incorrect_and_changed_correct": [],
        "incorrect_and_changed_incorrect": [],
        "incorrect_and_not_changed": []
    }
    errors = []
    table_data = [("raw", "first", "second")]

    # TEST: for question, answer in test_qas:
    for data_i in range(*EXPERIMENT_RANGE):  # range(*experiment_range):

        print("RUNNING", data_i)

        data_item, clean_item = data_handler.query_gpt(data_i, force=CLEAN_ANSWERS)

        print(f"Returning\n{clean_item}")

        a = data_item[data_handler.RAW_ANSWER_KEY] or "None"
        b = data_item[data_handler.QUERY_KEY] or "None"
        c = data_item[data_handler.ARE_YOU_SURE_KEY] or "None"

        table_data.append((a, b, c))

        if (b is None) or (c is None):
            errors.append(data_i)
            continue

        correct = a == b
        changed = b != c
        correct_second = a == c

        if correct and changed:
            results["correct_and_changed"].append(data_i)
        elif correct and (not changed):
            results["correct_and_not_changed"].append(data_i)
        elif (not correct) and changed:
            if correct_second:
                results["incorrect_and_changed_correct"].append(data_i)
            else:
                results["incorrect_and_changed_incorrect"].append(data_i)
        elif (not correct) and not changed:
            results["incorrect_and_not_changed"].append(data_i)
        else:
            print(f"UNEXPECTED {data_i} - {a} - {b} - {c}")

    for row in table_data:
        print("{: >20} {: >20} {: >20}".format(*row))

    for title, result_list in results.items():
        print(f"{title}: {len(result_list)}")

    plotter(
        results,
        filename=os.path.join(
            os.getcwd(),
            f"{EXPERIMENT_RANGE[0]}-{EXPERIMENT_RANGE[1]}.png"
        )
    )
