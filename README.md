# downsample-jp2s
Script to create binned jpeg2000 datasets for HiP-CT data.

## Usage
- **Must be run on ESRF servers**
- Request enough resource allocation using `salloc --partition=bm18 --exclusive --mem=0 --ntasks=1 --time=24:00:00 srun --pty bash`
- Run:
```
python downsample.py
```

This will
1. Ask you to rename any folders that look like downsampled jp2 folders, but with slightly wrong names.
2. Generate any missing downsample-by-two datasets.
