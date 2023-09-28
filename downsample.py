from hipct_data_tools.data_model import load_scans, HiPCTScan

from copy import deepcopy
import difflib
import sys
from typing import List


differ = difflib.Differ()


def print_diff(a: str, b: str) -> None:
    """
    Print a visual diff of two strings.
    """
    sys.stdout.writelines(list(differ.compare([a + "\n"], [b + "\n"])))


def fix_old_names(datasets: List[HiPCTScan], bin_factor: int) -> None:
    # Rename existing downsampled JP2 directories if they have the wrong name
    for dataset in datasets:
        original_path = dataset.esrf_jp2_path
        # Get expeted downsample path
        downsampled_dataset = deepcopy(dataset)
        downsample_res = bin_factor * dataset.resolution_um
        downsampled_dataset.resolution_um = downsample_res
        downsampled_path_expected = (
            dataset.esrf_jp2_path.parent / downsampled_dataset.esrf_jp2_path.name
        )
        if downsampled_path_expected.exists():
            continue

        downsample_dirs = list(original_path.parent.glob(f"{downsample_res}*_jp2_"))
        # Some datasets are truncated to 2 decimal points...
        downsample_dirs += list(
            original_path.parent.glob(f"{downsample_res:.02f}*_jp2_")
        )
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

    print("Finished fixing directory names")


if __name__ == "__main__":
    datasets = load_scans()
    bin_factor = 2

    fix_old_names(datasets, bin_factor)

    print("Following downsampled datasets not available:")
    for dataset in datasets:
        downsampled_dataset = deepcopy(dataset)
        downsampled_dataset.resolution_um = 2 * dataset.resolution_um

        downsampled_path_expected = (
            dataset.esrf_jp2_path.parent / downsampled_dataset.esrf_jp2_path.name
        )
        if not (downsampled_path_expected.exists()):
            print(downsampled_path_expected.parent)
            print(downsampled_path_expected)
            print(
                f"python rebin.py {dataset.esrf_jp2_path} "
                "--bin-factor=2 "
                "--num-workers=128 "
                f"--output-directory={downsampled_path_expected} "
                f"--fname-prefix={downsampled_path_expected.name[:-4]} " # -4 to strip jp2_ from end
                "--cratio=10"
            )
            print()
