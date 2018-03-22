#!/bin/bash

download_if_does_not_exist() {
    # Root of the git repository
    root=$(git rev-parse --show-toplevel)
    path=$root/tests/integration/test_read/data
    if ! [ -f $path/$1 ]; then
    	curl -o $path/$1 $2
    fi
}

download_if_does_not_exist 570014520.nwb "https://data.kitware.com/api/v1/file/5a4f91618d777f5e872f8101/download"
download_if_does_not_exist ophys_example.nwb "https://data.kitware.com/api/v1/file/5ab3e3398d777f068578ed1d/download"
