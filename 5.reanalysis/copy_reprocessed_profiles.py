import shutil
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)

# Define file mappings
files = [
    (
        Path("~/Documents/GitHub/jump-profiling-recipe/outputs/stem_public/profiles_var_mad_int_featselect.parquet").expanduser(),
        Path("output/processed/var_mad_int_featselect/combined.parquet").expanduser(),
    ),
    (
        Path("~/Documents/GitHub/jump-profiling-recipe/outputs/stem_public/profiles_var_mad_int.parquet").expanduser(),
        Path("output/processed/var_mad_int/combined.parquet").expanduser(),
    ),
]

# Copy and rename files
for source, target in files:
    if not source.exists():
        logging.warning(f"Source file {source} does not exist. Skipping.")
        continue

    if target.exists():
        logging.warning(f"Target file {target} already exists. Skipping.")
        continue

    target_dir = target.parent
    if not target_dir.exists():
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logging.error(f"Error creating directory {target_dir}: {e}")
            continue

    try:
        shutil.copy(source, target)
        logging.info(f"Copied {source} to {target}")
    except IOError as e:
        logging.error(f"Error copying file {source} to {target}: {e}")
