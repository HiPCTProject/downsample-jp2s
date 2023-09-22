from hipct_data_tools.data_model import load_scans

from copy import deepcopy

if __name__ == '__main__':
    datasets = load_scans()

    # Rename existing downsampled JP2 directories
    for dataset in datasets:
        original_path = dataset.esrf_jp2_path
        bin_factor = 2
        downsample_res = bin_factor * dataset.resolution_um
        downsample_dirs = list(original_path.parent.glob(f"{downsample_res}*_jp2_"))
        if len(downsample_dirs) == 1:
            print(downsample_dirs)

    """
    print("Following downsampled datasets not available:")
    for dataset in datasets:
        downsampled_dataset = deepcopy(dataset)
        downsampled_dataset.resolution_um = 2 * dataset.resolution_um

        downsampled_path = dataset.esrf_jp2_path.parent / downsampled_dataset.esrf_jp2_path.name
        if not(downsampled_path.exists()):
            print(downsampled_path)
    """
