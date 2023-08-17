import matplotlib.pyplot as plt


def plotter(results, filename=None, display=True):

    labels = list(results.keys())
    values = [len(results[key]) for key in labels]

    plt.figure(figsize=(10, 7))
    bars = plt.bar(labels, values, color=['blue', 'green', 'red', 'cyan', 'magenta'])
    plt.ylabel('Number of Indices')
    plt.title('Indices by Category')
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
