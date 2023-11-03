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
    - None, but plots the distribution.
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
    plt.show()


def load_and_print_results(input_file):
    """
    Load analysis results from a Parquet file and print them.
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
            f"Logistic Regression Accuracy Score: {row['logistic_regression_accuracy']:.4f}"
        )
        print(f"Number of Significant Features: {row['num_significant_features']}")

        if row["num_significant_features"] > 0:
            visualize_channels(row["significant_features"])

        print(70 * "=")
