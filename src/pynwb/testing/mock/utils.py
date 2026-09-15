name_generator_registry = dict()


def name_generator(name):
    """
    Returns unique names of neurodata types using an incrementing number. The first time you pass "TimeSeries" it
    returns "TimeSeries". The second time, it returns "TimeSeries2", the third time it returns "TimeSeries3", etc.

    Parameters
    ----------
    name: str
        name of neurodata_type, e.g. TimeSeries

    Returns
    -------
    name of neurodata_object: str
    """
    if name not in name_generator_registry:
        name_generator_registry[name] = 1
        return name
    else:
        name_generator_registry[name] += 1
        return f"{name}{name_generator_registry[name]}"
