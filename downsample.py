from hipct_data_tools.data_model import HiPCTDataSet
from hipct_data_tools import load_datasets

from copy import deepcopy
import difflib
import sys
from typing import List

from rebin import rebin

differ = difflib.Differ()


def print_diff(a: str, b: str) -> None:
    """
    Print a visual diff of two strings.
    """
    sys.stdout.writelines(list(differ.compare([a + "\n"], [b + "\n"])))


def downample_dataset(dataset: HiPCTDataSet, bin_factor: int) -> HiPCTDataSet:
    """
    Create a copy of a dataset, with a downsampled resolution.
    """
    downsampled_dataset = deepcopy(dataset)
    downsampled_dataset.resolution_um = bin_factor * dataset.resolution_um
    return downsampled_dataset


def fix_old_names(datasets: List[HiPCTDataSet], bin_factor: int) -> None:
    # Rename existing downsampled JP2 directories if they have the wrong name
    for dataset in datasets:
        original_path = dataset.esrf_jp2_path
        # Get expeted downsample path
        downsampled_dataset = downample_dataset(dataset, bin_factor)
        downsampled_path_expected = (
            dataset.esrf_jp2_path.parent / downsampled_dataset.esrf_jp2_path.name
        )
        if downsampled_path_expected.exists():
            continue

        downsample_res = downsampled_dataset.resolution_um
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


def downsample(dataset: HiPCTDataSet, bin_factor: int) -> None:
    downsampled_dataset = downample_dataset(dataset, bin_factor)

    downsampled_path_expected = (
        dataset.esrf_jp2_path.parent / downsampled_dataset.esrf_jp2_path.name
    )
    if not (downsampled_path_expected.exists()):
        print("Downsampling:")
        print(downsampled_path_expected.parent)
        print(downsampled_path_expected)
        print()
        rebin.rebin(
            dataset.esrf_jp2_path,
            bin_factor=bin_factor,
            cratio=10,
            num_workers=64,
            output_directory=downsampled_path_expected,
            fname_prefix=downsampled_path_expected.name[:-4],  # -4 to strip 'jp2_'
        )


if __name__ == "__main__":
    datasets = load_datasets()

    fix_old_names(datasets, bin_factor=2)
    fix_old_names(datasets, bin_factor=4)

    print("Following downsampled datasets not available:")
    for dataset in datasets:
        downsample(dataset, bin_factor=2)
        # If bin-by-two is > 5GB, also add a bin-by-four
        if dataset.compressed_size_gb / 8 > 5:
            downsample(dataset, bin_factor=4)
