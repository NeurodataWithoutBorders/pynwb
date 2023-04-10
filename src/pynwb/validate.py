# from warnings import warn

from .validation import validate_cli


if __name__ == "__main__":
#     warn("The use of `python -m pynwb.validate` is deprecated and will be removed in a future version of PyNWB. "
#          "Please use the console script `validate_nwb` instead.", DeprecationWarning)
    validate_cli()
