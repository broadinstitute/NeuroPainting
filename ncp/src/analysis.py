import pandas as pd
import numpy as np

from sklearn.linear_model import LogisticRegression
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GroupKFold
from sklearn.metrics import accuracy_score

from scipy import stats as ss
import statsmodels.stats.multitest
import os


def logistic_regression(X, y):
    """
    Fit logistic regression with imputation.

    Parameters:
    - X: DataFrame, the feature data.
    - y: Series, the target data.

    Returns:
    - pipeline: Fitted pipeline object.
    """
    # Create a pipeline with an imputer and the logistic regression model
    pipeline = make_pipeline(
        SimpleImputer(strategy="median"), LogisticRegression(max_iter=10000)
    )

    # Fit the model using the pipeline
    pipeline.fit(X, y)

    return pipeline


def group_kfold_cross_validate_logistic_regression(
    df, feature_cols, target_col, group_col, n_splits=5
):
    """
    Perform Group K-Fold cross-validation on logistic regression and return the mean accuracy.

    Parameters:
    - df: DataFrame, the data.
    - feature_cols: list, the feature columns.
    - target_col: str, the target column.
    - group_col: str, the column to group by for cross-validation.
    - n_splits: int, number of folds for Group K-Fold cross-validation.

    Returns:
    - mean_accuracy: float, the mean accuracy across all folds.
    - std_accuracy: float, the std accuracy across all folds.
    - feature_importances: DataFrame, the feature importances averaged over all folds.
    """
    # Initialize the Group K-Fold
    gkf = GroupKFold(n_splits=n_splits)

    # Prepare features, target, and groups
    X = df[feature_cols]
    y = df[target_col]
    groups = df[group_col]

    # Store each fold's accuracy and feature importances
    accuracies = []
    feature_importances = []

    # Perform cross-validation
    for train_index, test_index in gkf.split(X, y, groups=groups):
        # Split the data
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]

        # Fit logistic regression
        pipeline = logistic_regression(X_train, y_train)

        # Predict on the test data and calculate accuracy
        y_pred = pipeline.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        accuracies.append(accuracy)

        # Get feature importances
        logistic_regr = pipeline.named_steps["logisticregression"]
        feature_importances.append(logistic_regr.coef_[0])

    # Calculate the mean and std accuracy across all folds
    mean_accuracy = np.mean(accuracies)
    std_accuracy = np.std(accuracies)

    # Calculate mean feature importances
    mean_feature_importances = np.mean(feature_importances, axis=0)
    feature_importances_df = pd.DataFrame(
        mean_feature_importances, index=feature_cols, columns=["importance"]
    ).sort_values(by="importance", ascending=False)

    return mean_accuracy, std_accuracy, feature_importances_df


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

    # Attempt to map the target_col values using the provided dictionary
    df[target_col_encoded] = df[target_col].map(target_col_mapping_dict)

    # Check if there are any NA values after mapping
    if df[target_col_encoded].isna().any():
        # Identify the values in target_col that were not mapped
        unmapped_values = df.loc[df[target_col_encoded].isna(), target_col].unique()
        print(
            f"WARNING: The following values in {target_col} were not mapped and will be excluded from the analysis: {unmapped_values}"
        )
        # Drop the rows with unmapped values
        df = df.dropna(subset=[target_col_encoded])

    for category in categories:
        print(f"Analyzing category: {category}")
        category_df = df[df[category_col] == category]

        # Perform logistic regression with Group K-Fold cross-validation
        (
            mean_accuracy,
            std_accuracy,
            feature_importances,
        ) = group_kfold_cross_validate_logistic_regression(
            category_df,
            feature_cols=feature_cols,
            target_col=target_col_encoded,
            group_col="Metadata_line_ID",  # your group column here
            n_splits=5,
        )

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
            "logistic_regression_accuracy_mean": mean_accuracy,
            "logistic_regression_accuracy_std": std_accuracy,
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
