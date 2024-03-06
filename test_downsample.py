import downsample
from hipct_data_tools import load_datasets
import pytest

from unittest.mock import call


@pytest.fixture
def datasets():
    return {d.name: d for d in load_datasets()}


def test_downsample_dataset(mocker, datasets):
    dataset = datasets["LADAF-2021-17_heart_complete-organ_8.01um_bm18"]

    mocker.patch("downsample.create_all_downsamples")
    downsample.create_all_downsamples(dataset)

    assert downsample.create_all_downsamples.call_count == 3
    downsample.create_all_downsamples.assert_has_calls(
        [
            call(dataset, bin_factor=2),
            call(dataset, bin_factor=4),
            call(dataset, bin_factor=8),
            call(dataset, bin_factor=16),
        ]
    )
