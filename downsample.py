from hipct_data_tools.data_model import load_scans

from copy import deepcopy

import difflib


if __name__ == '__main__':
    datasets = load_scans()
    bin_factor = 2
    differ = difflib.Differ()


    # Rename existing downsampled JP2 directories
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
            if downsample_path == downsampled_path_expected:
                # Already at correct path
                pass
            else:
                # Rename
                d = differ.compare(str(downsample_path), str(downsampled_path_expected))
                print(d)

    """
    print("Following downsampled datasets not available:")
    for dataset in datasets:
        downsampled_dataset = deepcopy(dataset)
        downsampled_dataset.resolution_um = 2 * dataset.resolution_um

        downsampled_path = dataset.esrf_jp2_path.parent / downsampled_dataset.esrf_jp2_path.name
        if not(downsampled_path.exists()):
            print(downsampled_path)
    """
