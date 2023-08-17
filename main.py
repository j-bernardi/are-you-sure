import os
import argparse

from data_handler import MathHandler, MultipleChoiceHandler
from plotter import plotter


def parse_arguments():

    parser = argparse.ArgumentParser(description="Command line arguments handler")

    parser.add_argument(
        '--clean-data-load', action='store_true', help='Enable clean data load.')

    parser.add_argument(
        '--clean-answers', action='store_true', help='Enable clean answers.')
    
    # Choices:
    #  algebra__linear_1d
    #  algebra__linear_2d
    # derek-thomas--ScienceQA

    parser.add_argument(
        '--dataset', help='Enable clean answers.')
    
    parser.add_argument(
        '--data-dir', required=True, help='Set data directory.')
    
    parser.add_argument(
        '--type', required=True, choices=["math", "multi"], help='Set experiment type.')

    parser.add_argument(
        '--range',
        type=lambda s: [int(item) for item in s.split(',')],
        required=True,
        help='Experiment range in the format "start,end".'
    )

    args = parser.parse_args()

    return args


if __name__ == "__main__":

    args = parse_arguments()

    CLEAN_DATA_LOAD = args.clean_data_load
    CLEAN_ANSWERS = args.clean_answers
    EXPERIMENT_RANGE = tuple(args.range)

    if args.type == "math":
        class_obj = MathHandler
    elif args.type == "multi":
        class_obj = MultipleChoiceHandler
    else:
        raise Exception(args.type)

    data_handler = class_obj(
        data_dir=args.data_dir,
        data_config=args.dataset,
        clean=CLEAN_DATA_LOAD
    )

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
            "images",
            f"{args.type}-{args.dataset}-{EXPERIMENT_RANGE[0]}-{EXPERIMENT_RANGE[1]}.png"
        ),
        display=False
    )
