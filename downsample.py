from hipct_data_tools.data_model import load_scans

from copy import deepcopy

if __name__ == '__main__':
    datasets = load_scans()

    print("Following downsampled datasets not available:")
    for dataset in datasets:
        downsampled_dataset = deepcopy(dataset)
        downsampled_dataset.resolution_um = 2 * dataset.resolution_um

        downsampled_path = dataset.esrf_jp2_path.parent / downsampled_dataset.esrf_jp2_path.name
        if not(downsampled_path.exists()):
            print(downsampled_path)
