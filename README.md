# Are You Sure?

When using ChatGPT, it'll sometimes give me an erroneous answer. I'll ask it "are you sure?", and it'll correct itself.

What happens if I ask it if it's sure when it gives a correct response? Let's find out.


# Setup

Go into main.py to set your api key file.

To run the script:

```bash
python your_script_name.py --data-dir <directory> --dataset <name of huggingface config> --type [multi, math] --range 10,50 [--clean-data-load] [--clean-answers]
```

This will set the EXPERIMENT_RANGE to (10, 50). This is a required argument.

This will force a clean load of data and clean queries to GPT-3.5. If you don't provide any arguments, both values default to false.

## Math equations
![Graph](images/0-100.png)


## Multiple choice questions
![Graph of other things](images/multi-derek-thomas--ScienceQA-0-50-v0.4.png)
