from hipct_data_tools.data_model import load_scans, HiPCTScan

from copy import deepcopy
import difflib
import sys
from typing import List


def fix_old_names(datasets: List[HiPCTScan], bin_factor: int):
    # Rename existing downsampled JP2 directories if they have the wrong name
    differ = difflib.Differ()

    for dataset in datasets:
        original_path = dataset.esrf_jp2_path
        # Get expeted downsample path
        downsampled_dataset = deepcopy(dataset)
        downsample_res = bin_factor * dataset.resolution_um
        downsampled_dataset.resolution_um = downsample_res
        downsampled_path_expected = dataset.esrf_jp2_path.parent / downsampled_dataset.esrf_jp2_path.name


        downsample_dirs = list(original_path.parent.glob(f"{downsample_res}*_jp2_"))
        if len(downsample_dirs) == 1:
            downsample_path = downsample_dirs[0]
            if downsample_path != downsampled_path_expected:
                # Rename
                print("Rename?")
                sys.stdout.writelines(
                    list(
                        differ.compare(
                            [str(downsample_path) + "\n"],
                            [str(downsampled_path_expected) + "\n"]
                        )
                    )
                )
                inp = input("Continue? ")
                if inp != "y":
                    print("skipping...")
                else:
                    print("renaming...")
                    downsample_path.rename(downsampled_path_expected)

        elif len(downsample_dirs) > 1:
            print("Found more than one potential downsample directory:")
            for dir in downsample_dirs:
                print(dir)

    print("Finished fixing directory names")



if __name__ == '__main__':
    datasets = load_scans()
    bin_factor = 2

    fix_old_names(datasets, bin_factor)


    """
    print("Following downsampled datasets not available:")
    for dataset in datasets:
        downsampled_dataset = deepcopy(dataset)
        downsampled_dataset.resolution_um = 2 * dataset.resolution_um

        downsampled_path = dataset.esrf_jp2_path.parent / downsampled_dataset.esrf_jp2_path.name
        if not(downsampled_path.exists()):
            print(downsampled_path)
    """
