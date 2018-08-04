class OrphanContainerWarning(UserWarning):
    """
    Raised when a container does not have a parent.

    Only the top level container (e.g. NWBFile) should be
    without a parent
    """
    pass


class MissingRequiredWarning(UserWarning):
    """
    Raised when a required field is missing.
    """
    pass
