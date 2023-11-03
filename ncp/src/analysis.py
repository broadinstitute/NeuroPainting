from sklearn.model_selection import GroupShuffleSplit
import pandas as pd


def split_data(
    df,
    target_col,
    feature_cols,
    group_split_col,
    train_size=0.8,
    random_state=42,
):
    """
    Split the data into training and test sets, keeping the DataFrame structure.

    Parameters:
    - df: DataFrame, the data.
    - target_col: str, the target variable column.
    - feature_cols: list, the feature columns.
    - group_split_col: str, the column to group by for splitting.
    - train_size: float, proportion of the dataset to include in the train split.
    - random_state: int, seed used by the random number generator.

    Returns:
    - X_train, X_test, y_train, y_test: DataFrames or Series, the split data.
    """

    if not set(feature_cols + [target_col, group_split_col]).issubset(df.columns):
        raise ValueError("One or more provided columns do not exist in the DataFrame.")

    X = df[feature_cols]
    y = df[target_col]
    gss = GroupShuffleSplit(
        n_splits=1, train_size=train_size, random_state=random_state
    )

    for train_idx, test_idx in gss.split(X, y, df[group_split_col]):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

    return X_train, X_test, y_train, y_test


from sklearn.linear_model import LogisticRegression
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline


def logistic_regression(X_train, y_train, X_test, y_test):
    """
    Perform logistic regression with imputation and return the accuracy score and feature weights.

    Parameters:
    - X_train, X_test: DataFrames, the training and test feature data.
    - y_train, y_test: Series, the training and test target data.

    Returns:
    - score: float, the accuracy of the model.
    - feature_weights: DataFrame, weights of each feature.
    """

    # Create a pipeline with an imputer and the logistic regression model
    # The imputer will fill in missing values with the median of the column
    pipeline = make_pipeline(
        SimpleImputer(strategy="median"), LogisticRegression(max_iter=10000)
    )

    # Train the model using the pipeline
    pipeline.fit(X_train, y_train)

    # Predict on the test data and calculate accuracy score using the pipeline
    score = pipeline.score(X_test, y_test)

    # Extract the trained logistic regression model from the pipeline
    logisticRegr = pipeline.named_steps["logisticregression"]

    # Extract feature weights and associate them with the feature names from X_train
    feature_weights = pd.DataFrame(
        logisticRegr.coef_[0],
        columns=["weight"],
        index=X_train.columns,  # Use the DataFrame's columns as the index for feature names
    ).sort_values(by="weight", ascending=False)

    return score, feature_weights


from scipy import stats as ss
import statsmodels.stats.multitest


def mann_whitney_u_test(df, feature_cols, target_col):
    """
    Conduct the Mann-Whitney U-test and return p-values and test statistics.

    Parameters:
    - df: DataFrame, the data.
    - feature_cols: list, columns to test.
    - target_col: str, column with groups to test. Assumed to be binary (0 and 1)

    Returns:
    - results: DataFrame, test statistics and p-values for each feature.
    """

    if target_col not in df.columns:
        raise ValueError(f"{target_col} does not exist in the DataFrame.")

    if not all(cond in df[target_col].unique() for cond in (0, 1)):
        raise ValueError("One or more target_groups do not exist in the group column.")

    # Filter the data for both target_groups once before the loop
    data_cond1 = df[df[target_col] == 0][feature_cols]
    data_cond2 = df[df[target_col] == 1][feature_cols]

    list_u = []
    list_p = []
    for feat in feature_cols:
        u, p = ss.mannwhitneyu(
            data_cond1[feat], data_cond2[feat], alternative="two-sided"
        )
        list_u.append(u)
        list_p.append(p)

    # Apply FDR correction
    _, p_values_fdr = statsmodels.stats.multitest.fdrcorrection(list_p, alpha=0.05)

    # Create a DataFrame for results
    results = pd.DataFrame(
        {
            "feature": feature_cols,
            "u_statistic": list_u,
            "p_value": list_p,
            "q_value": p_values_fdr,
        }
    )

    return results


import os


def perform_and_save_analysis(
    df, category_col, target_col, target_col_mapping_dict, feature_cols, output_dir
):
    """
    Perform analysis and save results to a Parquet file.

    Parameters:
    - df: DataFrame, the data.
    - category_col: str, the name of the column to define categories.
    - target_col: str, the name of the column to define groups for logistic regression and U-test.
    - target_col_mapping_dict: dict, a dictionary mapping target_col values to integers.
    - feature_cols: list, the list of feature columns to use for analysis.
    - output_dir: str, the directory to save the results to.
    """

    # Create a directory to store the results if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Create a DataFrame to store all summary results
    all_summary_results = pd.DataFrame()

    categories = df[category_col].unique()

    target_col_encoded = f"{target_col}_encoded"
    df[target_col_encoded] = df[target_col].map(target_col_mapping_dict).fillna(-1)

    for category in categories:
        print(f"Analyzing category: {category}")
        category_df = df[df[category_col] == category]

        # Prepare data for logistic regression
        X_train, X_test, y_train, y_test = split_data(
            category_df,
            feature_cols=feature_cols,
            target_col=target_col_encoded,
            group_split_col="Metadata_line_ID",
        )

        # Perform logistic regression
        score, feature_weights = logistic_regression(X_train, y_train, X_test, y_test)

        # Perform Mann-Whitney U-test
        test_results = mann_whitney_u_test(
            category_df, feature_cols=feature_cols, target_col=target_col_encoded
        )

        # Save the full test results to a Parquet file within the specified directory
        test_results_file = os.path.join(output_dir, f"test_results_{category}.parquet")
        test_results.to_parquet(test_results_file)

        # Filter for significant features
        significant_features = test_results.query("q_value < 0.05")["feature"].tolist()

        # Convert the list of significant features to a string for saving
        significant_features_str = ",".join(significant_features)

        # Store the summary of results, including the significant features
        category_summary = {
            "category": category,
            "logistic_regression_score": score,
            "num_significant_features": len(significant_features),
            "significant_features": significant_features_str,
            "full_test_results_file": test_results_file,  # Add the path of the full results file
        }

        # Convert to DataFrame
        category_summary_df = pd.DataFrame([category_summary])

        # Append to all summary results
        all_summary_results = pd.concat(
            [all_summary_results, category_summary_df], ignore_index=True
        )

    # Save all summary results to a Parquet file
    summary_results_file = os.path.join(output_dir, "summary_results.parquet")
    all_summary_results.to_parquet(summary_results_file)

    print(f"Analysis complete. Summary results saved to {summary_results_file}")
