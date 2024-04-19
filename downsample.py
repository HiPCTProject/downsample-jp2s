from hipct_data_tools.data_model import HiPCTDataSet
from hipct_data_tools import load_datasets

from copy import deepcopy
from pathlib import Path
import difflib
import sys
from typing import List
import subprocess

LOG_DIR = Path("/data/projects/hop/data_repository/Various/logs/rebinning")

differ = difflib.Differ()


def print_diff(a: str, b: str) -> None:
    """
    Print a visual diff of two strings.
    """
    sys.stdout.writelines(list(differ.compare([a + "\n"], [b + "\n"])))


def downsample_dataset(dataset: HiPCTDataSet, bin_factor: int) -> HiPCTDataSet:
    """
    Create a copy of a dataset, with a downsampled resolution.
    """
    downsampled_dataset = deepcopy(dataset)
    downsampled_dataset.resolution_um = bin_factor * dataset.resolution_um
    return downsampled_dataset


def fix_old_names(datasets: List[HiPCTDataSet], bin_factor: int) -> None:
    # Rename existing downsampled JP2 directories if they have the wrong name
    print(f"Checking for broken directory names (bin by {bin_factor})...")
    for dataset in datasets:
        fix_old_name(dataset, bin_factor)
    print(f"Finished fixing directory names (bin by {bin_factor})")


def fix_old_name(dataset: HiPCTDataSet, bin_factor: int) -> None:
    original_path = dataset.esrf_jp2_path
    # Get expeted downsample path
    downsampled_dataset = downsample_dataset(dataset, bin_factor)
    downsampled_path_expected = (
        dataset.esrf_jp2_path.parent / downsampled_dataset.esrf_jp2_path.name
    )
    if downsampled_path_expected.exists():
        return

    downsample_res = downsampled_dataset.resolution_um
    downsample_dirs = list(original_path.parent.glob(f"{downsample_res}*_jp2_"))
    # Some datasets are truncated to 2 decimal points...
    downsample_dirs += list(original_path.parent.glob(f"{downsample_res:.02f}*_jp2_"))
    if len(downsample_dirs) == 1:
        downsample_path = downsample_dirs[0]
        if downsample_path != downsampled_path_expected:
            # Rename
            print("Rename?")
            print_diff(str(downsample_path), str(downsampled_path_expected))
            inp = input("Continue? ")
            if inp != "y":
                print("skipping...")
            else:
                print("renaming...")
                downsample_path.rename(downsampled_path_expected)


def get_slurm_script(
    input_jp2_folder: Path, output_jp2_folder: Path, bin_factor: int, fname_prefix: str
) -> str:
    """
    Construct a slurm script for running jp2 > n5 conversion on a single directory.
    """
    log_dir = LOG_DIR / "logs"
    job_name = f"rebin_{output_jp2_folder.name}"
    n_cpus = 8

    sh_script = f"""#!/bin/bash
#SBATCH --output={log_dir}/%j-%x.log
#SBATCH --ntasks=1
#SBATCH --cpus-per-task={n_cpus}
#SBATCH --job-name={job_name}
#SBATCH --time=8:00:00
#SBATCH --chdir={Path(__file__).parent / 'rebin'}
echo ------------------------------------------------------

echo SLURM_NNODES: $SLURM_NNODES
echo SLURM_JOB_NODELIST: $SLURM_JOB_NODELIST
echo SLURM_SUBMIT_DIR: $SLURM_SUBMIT_DIR
echo SLURM_SUBMIT_HOST: $SLURM_SUBMIT_HOST
echo SLURM_JOB_ID: $SLURM_JOB_ID
echo SLURM_JOB_NAME: $SLURM_JOB_NAME
echo SLURM_JOB_PARTITION: $SLURM_JOB_PARTITION
echo SLURM_NTASKS: $SLURM_NTASKS
echo SLURM_CPUS-PER-TASK: $SLURM_CPUS_PER_TASK
echo SLURM_TASKS_PER_NODE: $SLURM_TASKS_PER_NODE
echo SLURM_NTASKS_PER_NODE: $SLURM_NTASKS_PER_NODE
echo ------------------------------------------------------

echo Starting virtual environment
conda activate data-tools
echo Running rebin command
srun python rebin.py --directory {input_jp2_folder} --output-directory {output_jp2_folder} --fname-prefix={fname_prefix} --bin-factor={bin_factor} --cratio=10 --num-workers={n_cpus}
"""

    return sh_script


def downsample(dataset: HiPCTDataSet, bin_factor: int) -> None:
    downsampled_dataset = downsample_dataset(dataset, bin_factor)

    downsampled_path_expected = (
        dataset.esrf_jp2_path.parent / downsampled_dataset.esrf_jp2_path.name
    )
    if not (downsampled_path_expected.exists()):
        print("Downsampling:")
        print(downsampled_path_expected.parent)
        print(downsampled_path_expected)
        slurm_script = get_slurm_script(
            input_jp2_folder=dataset.esrf_jp2_path,
            output_jp2_folder=downsampled_path_expected,
            bin_factor=bin_factor,
            fname_prefix=downsampled_path_expected.name[:-4],  # -4 to strip 'jp2_'
        )

        # For permissions 770 == rwxrwx---
        downsampled_path_expected.mkdir(mode=0o770, exist_ok=True)
        job_file = LOG_DIR / "scripts" / f"{downsampled_path_expected.name}.sh"
        with open(job_file, "w") as f:
            f.write(slurm_script)

        print(f"sbatch {job_file}")
        subprocess.run(["sbatch", str(job_file)])
        print()


def create_all_downsamples(dataset: HiPCTDataSet):
    bin_factor = 1
    downsampled_size = dataset.compressed_size_gb
    # Downsample until there's a dataset that fits in <= 4GB of memory
    while downsampled_size > 4 / 10:
        bin_factor *= 2
        downsampled_size = dataset.compressed_size_gb / bin_factor**3

        downsample(dataset, bin_factor=bin_factor)


if __name__ == "__main__":
    datasets = load_datasets()

    """
    fix_old_names(datasets, bin_factor=2)
    fix_old_names(datasets, bin_factor=4)
    print()
    """

    for dataset in datasets:
        create_all_downsamples(dataset)
