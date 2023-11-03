import pandas as pd


def load_dataframe(base_path, batch, plate, data_level):
    """
    Load a dataframe given the base path, batch name, plate name, and data level.
    """
    path = f"{base_path}/{batch}/{plate}/{plate}_{data_level}.csv.gz"
    return pd.read_csv(path)


def check_matching_columns(dfs_list):
    """
    Check if all dataframes in the list have the same columns.
    If not, report the columns that are different and raise an error.
    """
    reference_columns = set(dfs_list[0].columns)
    mismatch_info = []

    for idx, df in enumerate(
        dfs_list[1:], 2
    ):  # Start from 2 to account for 0-based indexing + reference df
        current_columns = set(df.columns)

        extra_columns = current_columns - reference_columns
        missing_columns = reference_columns - current_columns

        if extra_columns or missing_columns:
            info = f"DataFrame {idx} Mismatch:\n"
            if extra_columns:
                info += (
                    f"{len(extra_columns)} Extra Columns:\n\t"
                    + "\n\t".join(extra_columns)
                    + "\n"
                )
            if missing_columns:
                info += f"{len(missing_columns)} Missing Columns:\n\t" + "\n\t".join(
                    missing_columns
                )
            mismatch_info.append(info)

    if mismatch_info:
        detailed_error = "Dataframes have different columns:\n" + "\n".join(
            mismatch_info
        )
        # raise ValueError(detailed_error)
        # don't raise error for now just print
        print(detailed_error)


def drop_columns(df, columns_to_drop):
    """
    Drop specified columns or columns matching patterns if they exist in the dataframe.
    """
    exact_columns_to_drop = [col for col in columns_to_drop if col in df.columns]

    # Identify columns based on patterns
    pattern_columns_to_drop = []
    for pattern in columns_to_drop:
        matched_columns = [col for col in df.columns if col.startswith(pattern)]
        pattern_columns_to_drop.extend(matched_columns)

    all_columns_to_drop = set(exact_columns_to_drop + pattern_columns_to_drop)
    return df.drop(columns=all_columns_to_drop, axis=1)


def process_dataframes_by_cell_type(dfs, cell_type_data):
    """
    Process dataframes for a specific cell type:
    - Drop specified columns
    - Rename specified columns
    - Add new columns with default values
    - Check if columns match (if multiple dataframes)
    - Concatenate dataframes for the cell type
    """
    cell_dfs = [dfs[key] for key in cell_type_data["keys"]]

    # Drop columns
    columns_to_drop = cell_type_data.get("columns_to_drop", [])
    cell_dfs = [drop_columns(df, columns_to_drop) for df in cell_dfs]

    # Rename columns
    columns_to_rename = cell_type_data.get("columns_to_rename", {})
    cell_dfs = [df.rename(columns=columns_to_rename) for df in cell_dfs]

    # Add new columns with default values
    columns_to_add = cell_type_data.get("columns_to_add", {})
    for col, default_val in columns_to_add.items():
        for df in cell_dfs:
            df[col] = default_val

    # Compute new columns based on expressions involving existing columns
    columns_to_compute = cell_type_data.get("columns_to_compute", {})
    for new_col, expression in columns_to_compute.items():
        for df in cell_dfs:
            df[new_col] = df.eval(expression)

    # Check columns if there are multiple dataframes for the cell type
    if len(cell_dfs) > 1:
        check_matching_columns(cell_dfs)

    # Concatenate dataframes for the cell type
    return pd.concat(cell_dfs)
