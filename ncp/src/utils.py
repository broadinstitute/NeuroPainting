import pandas as pd
from itertools import combinations

from analysis import perform_and_save_analysis
from visualization import visualize_results


def apply_function_to_groups(df, group_col, func, *args, **kwargs):
    """
    Applies a function to subsets of a DataFrame grouped by a specified column.

    Parameters:
    - df: pandas.DataFrame, the input DataFrame.
    - group_col: str, the name of the column to group by.
    - func: callable, the function to apply to each group.
    - *args: arguments passed to the function.
    - **kwargs: keyword arguments passed to the function.

    Returns:
    - pandas.DataFrame, the concatenated results after applying the function to each group.
    """
    # Placeholder for the results
    results = []

    # Iterate over each group
    for group_value, group_df in df.groupby(group_col):
        # Apply the function to the group
        result = func(group_df, *args, **kwargs)
        # Add a column to track the group value if necessary
        result[group_col] = group_value
        results.append(result)

    # Concatenate all results into one DataFrame
    return pd.concat(results, ignore_index=True)


def run_analysis(data_level, feature_cols_pattern="Cells_|Cytoplasm_|Nuclei_"):
    data_path = f"output/processed/{data_level}/combined.parquet"

    df = pd.read_parquet(data_path)

    # select only rows where the Metadata_line_source is "human"
    df = df.query("Metadata_line_source == 'human'")
    feature_cols = df.columns[
        df.columns.str.contains(feature_cols_pattern, regex=True)
    ].tolist()

    cols_to_drop_stem_cell = [
        "Nuclei_ObjectSkeleton_NumberNonTrunkBranches_CellImageSkel",
        "Nuclei_ObjectSkeleton_NumberBranchEnds_CellImageSkel",
        "Nuclei_ObjectSkeleton_TotalObjectSkeletonLength_CellImageSkel",
    ]

    # HACK to reduce the number of features
    import random

    random.seed(42)
    random.shuffle(feature_cols)
    feature_cols = feature_cols[:30]

    # ------------------------------------------------------------
    # Control vs Deletion, per cell type
    # ------------------------------------------------------------

    target_col_mapping_dict = {"control": 0, "deletion": 1}
    perform_and_save_analysis(
        df=df,
        category_col="Metadata_cell_type",
        target_col="Metadata_line_condition",
        target_col_mapping_dict=target_col_mapping_dict,
        feature_cols=feature_cols,
        output_dir=f"output/analysis_results/{data_level}/control_vs_deletion/",
    )

    # ------------------------------------------------------------
    # Cell type A vs B, per condition
    # ------------------------------------------------------------

    # Define the cell types
    cell_types = ["stem", "neuron", "progen", "astro"]

    # Create all unique pairs of cell types
    cell_type_pairs = list(combinations(cell_types, 2))

    # Perform analysis for each pair
    for cell_type_0, cell_type_1 in cell_type_pairs:
        cols_to_drop = (
            cols_to_drop_stem_cell if "stem" in [cell_type_0, cell_type_1] else []
        )

        target_col_mapping_dict = {cell_type_0: 0, cell_type_1: 1}

        output_dir = f"output/analysis_results/{data_level}/cell_type_a_vs_b/{cell_type_0}_vs_{cell_type_1}/"

        perform_and_save_analysis(
            df=df.drop(columns=cols_to_drop, errors="ignore"),
            category_col="Metadata_line_condition",
            target_col="Metadata_cell_type",
            target_col_mapping_dict=target_col_mapping_dict,
            feature_cols=feature_cols,
            output_dir=output_dir,
        )


def inspect_analysis(data_level):
    # ------------------------------------------------------------
    # Control vs Deletion, per cell type
    # ------------------------------------------------------------

    output_dir = f"output/analysis_results/{data_level}/control_vs_deletion/"
    results_file = f"{output_dir}/summary_results.parquet"

    visualize_results(
        input_file=results_file,
        output_dir=output_dir,
    )

    # ------------------------------------------------------------
    # Cell type A vs B, per condition
    # ------------------------------------------------------------

    from itertools import combinations

    cell_types = ["stem", "neuron", "progen", "astro"]

    cell_type_pairs = list(combinations(cell_types, 2))

    for cell_type_0, cell_type_1 in cell_type_pairs:
        print(f"{data_level}:{cell_type_0}_vs_{cell_type_1}")

        output_dir = f"output/analysis_results/{data_level}/cell_type_a_vs_b/{cell_type_0}_vs_{cell_type_1}/"

        results_file = f"{output_dir}/summary_results.parquet"

        visualize_results(
            input_file=results_file,
            output_dir=output_dir,
        )
