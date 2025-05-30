import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import textwrap

def read_and_process_csv(file):
    """
    Process topic CSV into DataFrame for plotting.
    """
    df = pd.read_csv(file)

    rounds = sum(df['Count'])

    # Remove the first row, which contains the miscellanous topic
    df = df[1:]

    # Keep only the top 10 largest topics. In the paper for some topics, we kept 4 topics for some plots and changed names manually for space reasons.
    df = df.nlargest(10, 'Count')

    # Sort by size in descending order
    df = df.sort_values(by='Count', ascending=False)

    def get_first_line(text):
        if isinstance(text, str):
            # Extract the desired substring
            substring = text.split("_")[1].split('\n')[0]

            # Wrap text at 40 characters without breaking words if possible
            wrapped_text = "\n".join(textwrap.wrap(substring, width=30, break_long_words=False, break_on_hyphens=False))

            return wrapped_text
        return None
    df['Name'] = df['Name'].apply(get_first_line)

    # Add sort field
    df['label_ordered'] = pd.Categorical(df['Name'], categories=df['Name'], ordered=True)

    return df, rounds

def create_topic_plot(df, filename, rounds):
    """
    Create a topic plot based on the DataFrame provided.
    """
    plt.figure(figsize=(2, 10))

    # Create a figure and axes first.
    fig, ax = plt.subplots(figsize=(4, 10))

    # Create the barplot on the provided axes.
    sns.barplot(
        ax=ax,
        y=df['label_ordered'],
        x=df['Count'] / rounds * 100,
        palette='viridis'
    )

    # Add a "super" x-label that's centered across the entire figure.
    plt.xlabel("Fraction of Insights (%)", fontsize=18)

    # Adjust tick label sizes.
    ax.tick_params(axis='x', labelsize=18)
    ax.tick_params(axis='y', labelsize=18)

    # Optionally remove the y-axis label.
    ax.set_ylabel('')

    # Add a grid along the y-axis.
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    # Save and show the figure.
    plt.savefig(filename, dpi=300, bbox_inches="tight")

def create_topic_plots(file_glob):
    """
    Create all topic plots.
    """

    # Use glob to get all files matching topics_*.csv
    files = glob.glob(file_glob)

    # Iterate through all CSV files
    for file in files:
        # Reading and processing CSV data
        df, rounds = read_and_process_csv(file)

        # Extract the suffix part of the CSV file name
        # os.path.splitext(file)[0] will remove the .csv suffix,
        # Then use replace("topics_", "") to remove the prefix "topics_"
        suffix = os.path.splitext(os.path.basename(file))[0].replace("topics_", "")

        # Output path using the extracted suffix
        output_path = f"./plots/topic_distribution_{suffix}.png"

        create_topic_plot(df, output_path, rounds)


if __name__ == "__main__":
    output_folder = "data"
    create_topic_plots(f"{output_folder}/topics_*.csv")