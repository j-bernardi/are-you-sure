from data_handler import MultipleChoiceHandler, MathHandler


if __name__ == "__main__":

    d = MultipleChoiceHandler("multi_data", None)

    print(d.data)

    for i, data in d.data.items():
        print(f"\nROW {i}")
        for k, v in data.items():
            print(f"{k}: {v}")
