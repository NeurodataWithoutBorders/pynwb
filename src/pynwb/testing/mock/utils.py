import itertools

def name_generator(name):
    for i in itertools.count(start=1):
        yield f"{name}{i}"