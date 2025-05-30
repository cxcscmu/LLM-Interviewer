import glob
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Define the file pattern. This will match all files ending with "ratings_by_record.csv"
def create_correlation_plots(output_folder, plot_folder):
    """
    Create plots for rating correlation.
    """
    file_pattern = f"{output_folder}/*ratings_by_record_recreated.csv"
    file_list = glob.glob(file_pattern)

    if not file_list:
        print("No files found matching the pattern:", file_pattern)
        exit()

    print("Found files:")
    for f in file_list:
        print(f)

    # List to hold each file's DataFrame.
    dataframes = []

    # Loop through each file, read it, and add it to the list.
    for file in file_list:
        # Read the CSV file. Pandas automatically uses the first row as header.
        df = pd.read_csv(file)
        dataframes.append(df)

    # Concatenate all DataFrames, resetting the index so that it's sequential.
    combined_df = pd.concat(dataframes, ignore_index=True)

    # Uncomment the following lines if you want to save the combined CSV file.
    # output_file = "combined_ratings_by_record.csv"
    # combined_df.to_csv(output_file, index=False)
    # print(f"Combined CSV has been saved as '{output_file}'")

    # Work with the concatenated data.
    df = combined_df

    # Select only the columns of interest.
    cols = ['RQ1', 'RQ2', 'RQ3','RQ6', 'RQ4']
    df_sub = df[cols]

    # Convert the data to numeric values (non-convertible entries become NaN).
    df_sub = df_sub.apply(pd.to_numeric, errors='coerce')

    # Rename the columns.
    rename_dict = {
        'RQ1': 'Understanding',
        'RQ2': 'Meet Need',
        'RQ3': 'Credibility',
        'RQ4': 'Explicit Rating',
        'RQ6': 'General'
    }
    df_sub.rename(columns=rename_dict, inplace=True)

    # Optionally, drop rows with missing values if you want to work only with complete cases.
    # df_sub = df_sub.dropna()

    # Calculate the Spearman correlation matrix.
    spearman_corr = df_sub.corr(method='spearman')
    print("Spearman Correlation Matrix:")
    print(spearman_corr)

    # Plot the Spearman correlation heatmap.
    plt.figure(figsize=(12, 10))
    from matplotlib.colors import LinearSegmentedColormap

    # Sample data; replace this with your own dataset.
    # data = np.random.randn(10, 10)

    # Create a custom diverging colormap.
    # This will map negative values to green, zero to white, and positive values to blue.
    # custom_cmap = LinearSegmentedColormap.from_list("blue_green", ["white", "green", "blue"])

    ax = sns.heatmap(spearman_corr, annot=True, cmap="RdBu", vmin=-1, vmax=1, fmt=".2f", annot_kws={"size": 35}, cbar=False)
    # Set the x-axis tick labels to horizontal (rotation=0)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90, fontsize=30)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=30)
    # plt.title('Spearman Correlation Heatmap of Evaluation Dimensions')
    plt.savefig(f"{plot_folder}/correlation_matrix.png", dpi=300, bbox_inches="tight")

    # --- Plot scatter plots between Satisfaction (RQ4) and the other dimensions ---
    # Define the list of variables to compare against Satisfaction.
    other_vars = ['Understanding', 'Meet Need', 'Credibility', 'General']

    # Create a 2x2 grid of subplots.
    # fig, axs = plt.subplots(2, 2, figsize=(12, 10))
    # axs = axs.flatten()  # Flatten the 2D array for easy iteration.

    for var in other_vars:
        # Group by the x and y variables and count occurrences.
        aggregated = df_sub.groupby([var, 'Explicit Rating']).size().reset_index(name='count')

        plt.figure(figsize=(5, 6))
        # Multiply by a scale factor to adjust the bubble sizes.
        plt.scatter(aggregated[var], aggregated['Explicit Rating'], s=aggregated['count'] * 30, alpha=0.7)
        plt.xlabel(var, fontsize=20)
        plt.ylabel('Explicit Rating', fontsize=20)
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        plt.locator_params(axis='x', nbins=3)
        plt.locator_params(axis='y', nbins=5)

        var_sanitized = var.replace(" ", "_")
        plt.savefig(f"{plot_folder}/correlation_{var_sanitized}.png", dpi=300, bbox_inches="tight")

if __name__ == "__main__":
    output_folder = "data"
    plot_folder = "plots"
    create_correlation_plots(output_folder, plot_folder)