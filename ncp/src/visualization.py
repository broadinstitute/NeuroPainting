from parse_cp_features import parse_cp_features
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def visualize_channels(significant_features):
    """
    Visualize the distribution of channels for significant features.

    Parameters:
    - significant_features: list, features found to be significant.

    Returns:
    - ax: matplotlib.axes._axes.Axes, axes object of the plot.
    """

    channel_list = [parse_cp_features(feat)["channel"] for feat in significant_features]
    df_channel = pd.DataFrame(channel_list, columns=["channel"])
    df_channel_count = df_channel.groupby("channel").size().reset_index(name="counts")
    df_channel_count["percentage"] = (
        df_channel_count["counts"] / df_channel_count["counts"].sum()
    )
    df_channel_count["sort"] = df_channel_count["channel"].str.contains("_")
    df_channel_count = df_channel_count.sort_values(
        by=["sort", "percentage"], ascending=False
    )

    plt.figure(figsize=(10, 5))
    ax = sns.barplot(x="channel", y="percentage", data=df_channel_count)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right")
    plt.tight_layout()

    return ax


def visualize_results(input_file, output_dir):
    """
    Visualize the results of the analysis.

    Parameters:
    - input_file: str, path to the input file.
    - output_dir: str, path to the output directory.

    Returns:
    - None, saves the plots to the output directory.
    """

    # Load the results
    results_df = pd.read_parquet(input_file)

    # Convert the significant_features back to lists from strings
    results_df["significant_features"] = results_df["significant_features"].apply(
        lambda x: x.split(",") if pd.notnull(x) else []
    )

    # Print the results
    for _, row in results_df.iterrows():
        print(f"\nCategory: {row['category']}")
        print(
            f"Logistic Regression Accuracy Score: {row['logistic_regression_accuracy_mean']:.4f}"
        )
        print(f"Number of Significant Features: {row['num_significant_features']}")

        if row["num_significant_features"] > 0:
            ax = visualize_channels(row["significant_features"])
            output_file = f"{output_dir}/significant_features_{row['category']}.png"
            ax.figure.savefig(output_file)  # save the plot to a file
            plt.show()  # show the plot

        print(70 * "=")

    sns.scatterplot(
        data=results_df,
        x="logistic_regression_accuracy_mean",
        y="num_significant_features",
        hue="category",
        palette="deep",
        s=100,
    )
    # Add error bars
    for index, row in results_df.iterrows():
        plt.errorbar(
            row["logistic_regression_accuracy_mean"],
            row["num_significant_features"],
            xerr=row["logistic_regression_accuracy_std"],
            fmt=".",
            color="gray",
            capsize=3,  # Adds caps to the error bars
        )

    plt.title("Logistic Regression Accuracy vs Number of Significant Features")
    plt.xlabel("Logistic Regression Accuracy")
    plt.ylabel("Number of Significant Features")

    output_file = f"{output_dir}/classification_vs_significant_features.png"
    plt.savefig(output_file)
    plt.show()
