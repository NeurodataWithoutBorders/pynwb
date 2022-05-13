name_generator_registry = dict()


def name_generator(name):
    if name not in name_generator_registry:
        name_generator_registry[name] = 1
        return name
    else:
        name_generator_registry[name] += 1
        return f"{name}{name_generator_registry[name]}"