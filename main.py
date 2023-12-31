import os
import openai
import requests
import argparse

from data_handler import MathHandler, MultipleChoiceHandler
from plotter import plotter


def parse_arguments():

    parser = argparse.ArgumentParser(description="Command line arguments handler")

    parser.add_argument(
        '--data-dir', required=True, help='Set data directory.')

    parser.add_argument(
        '--dataset', help='Choose the dataset to run.',
        choices=["derek-thomas--ScienceQA", "algebra__linear_2d", "algebra__linear_1d"]
    )

    parser.add_argument(
        '--range',
        type=lambda s: [int(item) for item in s.split(',')],
        required=True,
        help='Experiment range in the format "start,end".'
    )

    parser.add_argument(
        '--clean-data-load', action='store_true',
        help='Force cleaning of the whole data dictionary for this directory.'
    )

    parser.add_argument(
        '--clean-answers', action='store_true', help='Enable clean answers.')
    
    parser.add_argument('--model', default="gpt-3.5-turbo")

    args = parser.parse_args()

    return args


if __name__ == "__main__":

    args = parse_arguments()

    CLEAN_DATA_LOAD = args.clean_data_load
    CLEAN_ANSWERS = args.clean_answers
    EXPERIMENT_RANGE = tuple(args.range)
    TEMPERATURE = 0

    kwargs = {}

    if args.dataset in ("algebra__linear_2d", "algebra__linear_1d"):
        class_obj = MathHandler
        if args.dataset == "algebra__linear_1d":
            kwargs["dim"] = "1d"
        elif args.dataset == "algebra__linear_2d":
            print("WARNING this may need some work.")
            kwargs["dim"] = "2d"
        else:
            raise Exception(args.dataset)

    elif args.dataset in ("derek-thomas--ScienceQA",):
        class_obj = MultipleChoiceHandler

    else:
        raise Exception(args.type)

    data_handler = class_obj(
        data_dir=args.data_dir,
        data_config=args.dataset,
        clean=CLEAN_DATA_LOAD,
        temperature=TEMPERATURE,
        model=args.model,
        **kwargs
    )

    data_handler.get_data(*EXPERIMENT_RANGE)

    results = {
        "correct_and_changed": [],
        "correct_and_not_changed": [],
        "incorrect_and_changed_correct": [],
        "incorrect_and_changed_incorrect": [],
        "incorrect_and_not_changed": []
    }

    not_applicable = []
    errors = []
    table_data = [("idx", "raw", "first", "second")]
    error_idcs = {}

    # TEST: for question, answer in test_qas:
    for data_i in range(*EXPERIMENT_RANGE):  # range(*experiment_range):

        # Try except to skip timeouts
        try:
            data_item, clean_item = data_handler.query_gpt(data_i, force=CLEAN_ANSWERS)
        except requests.exceptions.ReadTimeout as rte:
            error_idcs[data_i] = f"{rte}"
            continue
        except openai.error.Timeout as rte:
            error_idcs[data_i] = f"{rte}"
            continue
            
        if data_item is None:
            assert clean_item is None
            not_applicable.append(data_i)
            continue


        # print(f"Returning\n{data_item}")
        # print(f"Returning\n{clean_item}")

        a = data_item[data_handler.RAW_ANSWER_KEY] or "None"
        b = data_item[data_handler.QUERY_KEY] or "None"
        c = data_item[data_handler.ARE_YOU_SURE_KEY] or "None"

        table_data.append((data_i, a, b, c))

        if (b == "None") or (c == "None"):
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
    
    talked_out_denom = (
        len(results["correct_and_changed"]) + len(results["correct_and_not_changed"]))
    if talked_out_denom:
        talked_out =\
            len(results["correct_and_changed"]) / talked_out_denom
    else:
        talked_out = 0

    corrected_denom = (
        len(results["incorrect_and_changed_correct"]) + len(results["incorrect_and_changed_incorrect"])
        + len(results["incorrect_and_not_changed"])
    )

    if corrected_denom:
        corrected = len(results["incorrect_and_changed_correct"]) / corrected_denom

    else:
        corrected = 0

    if error_idcs:
        print("Exceptions")
    for k, v in error_idcs.items():
        print(f"{k}: {v}")
    
    print(f"Incompatible questions: {len(not_applicable)}")

    for row in table_data:
        print("{: >20} {: >20} {: >20} {: >20}".format(*row))

    for title, result_list in results.items():
        print(f"{title}: {len(result_list)}")

    print(f"Corrected itself  {corrected * 100:.2f} % of incorrect answers")
    print(f"Talked itself out {talked_out * 100:.2f} % of correct answers")

    plotter(
        results,
        filename=os.path.join(
            os.getcwd(),
            args.data_dir,
            f"{args.dataset}-{EXPERIMENT_RANGE[0]}-{EXPERIMENT_RANGE[1]}-v{data_handler.PROMPT_VERSION}.png"
        ),
        display=False,
        title=f"Result of asking {args.model} 'Are you sure?"
    )
