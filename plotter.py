import matplotlib.pyplot as plt


def plotter(results, filename=None, display=True, title=None):

    labels = list(results.keys())
    values = [len(results[key]) for key in labels]

    plt.rcParams.update({'font.size': 15})
    plt.figure(figsize=(10, 7))
    bars = plt.bar(labels, values, color=['blue', 'green', 'red', 'cyan', 'magenta'])
    plt.ylabel('Number of instances')
    plt.title('Results of asking gpt-3.5-turbo "Are you sure?""')
    plt.xticks(rotation=30, ha='right')  # Rotate labels for better readability
    plt.tight_layout()  # Adjust spacing for better fit



    # Display the count above each bar
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.1, int(yval), 
                ha='center', va='bottom')


    if display:
        plt.show()
    if filename is not None:
        plt.savefig(filename)
