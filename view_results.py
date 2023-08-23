import pickle

if __name__ == "__main__":

    DATA_DIR = "local_multi_filter_image_gpt-4"
    IDCS = range(100, 130)

    with open(f"{DATA_DIR}/data.p", "rb") as f:
        all_data = pickle.load(f)

    for i in IDCS:

        data = all_data[i]
        if data is None:
            print(f"Data {i} required image")
            continue
        print("\n***********")
        print(f"QUESTION {i}")
        print(data["question"])
        print("\nFIRST")
        print(data["raw_model_first_answer_0.5"])
        print(f"->{data['model_first_answer_0.5']}")
        if data['model_first_answer_0.5'] is None:
            continue
        print("\nSECOND")
        print(data["raw_model_second_answer_0.5"])
        print(f"->{data['model_second_answer_0.5']}")
