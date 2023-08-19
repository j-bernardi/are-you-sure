import os
import openai
import pickle
import requests
import argparse

from data_handler import MathHandler, MultipleChoiceHandler
from plotter import plotter

"""
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
"""


if __name__ == "__main__":

    # args = parse_arguments()
    # CLEAN_DATA_LOAD = args.clean_data_load
    # CLEAN_ANSWERS = args.clean_answers
    # EXPERIMENT_RANGE = tuple(args.range)
    # 
    # if args.type == "math":
    #     class_obj = MathHandler
    # elif args.type == "multi":  
    # else:
    #     raise Exception(args.type)

    data_handler = MultipleChoiceHandler(
        data_dir="distribution_data",
        data_config="derek-thomas--ScienceQA",
        clean=False,
    )

    EXPERIMENT_RANGE = (60, 65)

    data_handler.get_data(*EXPERIMENT_RANGE)

    if os.path.exists("distribution_data/results.p"):
        with open("distribution_data/results.p", "rb") as f:
            results = pickle.load(f)
    else:
        results = {
            i: {
                "correct_and_changed": [],
                "correct_and_not_changed": [],
                "incorrect_and_changed_correct": [],
                "incorrect_and_changed_incorrect": [],
                "incorrect_and_not_changed": [],
                "error": []
            }
            for i in range(*EXPERIMENT_RANGE)
        }
    # table_data = [("idx", "raw", "first", "second")]

    error_count = 0

    # TEST: for question, answer in test_qas:
    for data_i in range(*EXPERIMENT_RANGE):  # range(*experiment_range):
        while sum([len(lst) for lst in results[data_i].values()]) < 20:

            # Try except to skip timeouts
            try:
                data_item, clean_item = data_handler.query_gpt(data_i, force=True)
            except requests.exceptions.ReadTimeout as rte:
                # error_idcs[data_i] = f"{rte}"
                print(f"{rte}")
                error_count += 1
                continue
            except openai.error.Timeout as rte:
                # error_idcs[data_i] = f"{rte}"
                print(f"{rte}")
                error_count += 1
                continue

            # print(f"Returning\n{clean_item}")

            a = data_item[data_handler.RAW_ANSWER_KEY] or "None"
            b = data_item[data_handler.QUERY_KEY] or "None"
            c = data_item[data_handler.ARE_YOU_SURE_KEY] or "None"

            # table_data.append((data_i, a, b, c))

            if (b is None) or (c is None):
                results[data_i]["error"].append(data_i)
                continue

            correct = a == b
            changed = b != c
            correct_second = a == c

            if correct and changed:
                results[data_i]["correct_and_changed"].append(data_i)
            elif correct and (not changed):
                results[data_i]["correct_and_not_changed"].append(data_i)
            elif (not correct) and changed:
                if correct_second:
                    results[data_i]["incorrect_and_changed_correct"].append(data_i)
                else:
                    results[data_i]["incorrect_and_changed_incorrect"].append(data_i)
            elif (not correct) and not changed:
                results[data_i]["incorrect_and_not_changed"].append(data_i)
            else:
                print(f"UNEXPECTED {data_i} - {a} - {b} - {c}")
            
            with open("distribution_data/results.p", "wb") as f:
                pickle.dump(results, f)

    """
    print("Exceptions")
    for k, v in error_idcs.items():
        print(f"{k}: {v}")
    """

    # for row in table_data:
    #     print("{: >20} {: >20} {: >20} {: >20}".format(*row))

    for i, result_dict_i in results.items():
        print(f"\nDATA{i}\n")
        talked_out =\
            len(result_dict_i["correct_and_changed"]) / (
                len(result_dict_i["correct_and_changed"]) + len(result_dict_i["correct_and_not_changed"]))
        corrected =\
            len(result_dict_i["incorrect_and_changed_correct"]) /(
                len(result_dict_i["incorrect_and_changed_correct"]) + len(result_dict_i["incorrect_and_changed_incorrect"])
                + len(result_dict_i["incorrect_and_not_changed"])
            )
        for title, result_list in result_dict_i.items():
            print(f"{title}: {len(result_list)}")

        print(f"Corrected itself  {corrected * 100:.2f} % of correct answers")
        print(f"Talked itself out {talked_out * 100:.2f} % of incorrect answers")

        plotter(
            results,
            filename=os.path.join(
                os.getcwd(),
                "images_distribution",
                f"{i}-multi-distribution-v{data_handler.PROMPT_VERSION}.png"
            ),
            display=False
        )
    print(f"ERRORS: {error_count}")