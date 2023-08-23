import os
import openai
import pickle
import requests

from data_handler import MultipleChoiceHandler
from plotter import plotter


if __name__ == "__main__":

    TEMPERATURE = 1.  # OpenAI default = 1.
    DATA_DIR = f"distribution_data_t{TEMPERATURE}"
    REPEAT_COUNT = 20

    # TODO - find valid indices 
    EXPERIMENT_IDCS = [188, 189, 190, 191, 193, 195]

    data_handler = MultipleChoiceHandler(
        data_dir=DATA_DIR,
        data_config="derek-thomas--ScienceQA",
        clean=False,
        temperature=TEMPERATURE,
    )

    data_handler.get_data(EXPERIMENT_IDCS[0], EXPERIMENT_IDCS[-1])

    if os.path.exists(f"{DATA_DIR}/results.p"):
        with open(f"{DATA_DIR}/results.p", "rb") as f:
            results = pickle.load(f)
    else:
        results = {}

    for i in EXPERIMENT_IDCS:
        if i not in results:
            results[i] = {
                "correct_and_changed": [],
                "correct_and_not_changed": [],
                "incorrect_and_changed_correct": [],
                "incorrect_and_changed_incorrect": [],
                "incorrect_and_not_changed": [],
                "error": []
            }

    # table_data = [("idx", "raw", "first", "second")]

    error_count = 0

    # TEST: for question, answer in test_qas:
    for data_i in EXPERIMENT_IDCS:  # range(*experiment_range):
        while sum([len(lst) for lst in results[data_i].values()]) < REPEAT_COUNT:

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
            
            with open(f"{DATA_DIR}/results.p", "wb") as f:
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

        talked_out_denom = (
            len(result_dict_i["correct_and_changed"]) + len(result_dict_i["correct_and_not_changed"]))
        if talked_out_denom:
            talked_out =\
                len(result_dict_i["correct_and_changed"]) / talked_out_denom
        else:
            talked_out = 0

        corrected_denom = (
                len(result_dict_i["incorrect_and_changed_correct"]) + len(result_dict_i["incorrect_and_changed_incorrect"])
                + len(result_dict_i["incorrect_and_not_changed"])
        )

        if corrected_denom:
            corrected =\
                len(result_dict_i["incorrect_and_changed_correct"]) / corrected_denom
        else:
            corrected = 0

        for title, result_list in result_dict_i.items():
            print(f"{title}: {len(result_list)}")

        print(f"Corrected itself  {corrected * 100:.2f} % of incorrect answers")
        print(f"Talked itself out {talked_out * 100:.2f} % of correct answers")

        plotter(
            result_dict_i,
            filename=os.path.join(
                DATA_DIR,
                f"{i}-multi-distribution-v{data_handler.PROMPT_VERSION}-t={TEMPERATURE}.png"
            ),
            display=False,
            title=f"Asking GPT-3.5-turbo Are You Sure {REPEAT_COUNT} Times - data_i={i}"
        )
    print(f"ERRORS: {error_count}")
