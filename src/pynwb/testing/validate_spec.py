import os
import yaml
import json
from glob import glob

import jsonschema

print(os.path.dirname(os.path.realpath(__file__)))

cur_file = os.path.dirname(os.path.realpath(__file__))
fpath_schema = os.path.join(os.path.split(cur_file)[0], 'nwb-schema', 'nwb.schema.json')
fpath_core = os.path.join(os.path.split(cur_file)[0], 'nwb-schema', 'core')


def validate_spec(fpath_spec, fpath_schema=fpath_schema):

    schemaAbs = 'file://' + os.path.abspath(fpath_schema)

    f_schema = open(fpath_schema, 'r')
    schema = json.load(f_schema)

    class FixResolver(jsonschema.RefResolver):
        def __init__(self):
            jsonschema.RefResolver.__init__(self,
                                            base_uri=schemaAbs,
                                            referrer=None)
            self.store[schemaAbs] = schema

    new_resolver = FixResolver()

    f_nwb = open(fpath_spec, 'r')
    instance = yaml.load(f_nwb, Loader=yaml.FullLoader)

    jsonschema.validate(instance, schema, resolver=new_resolver)


def validate_core_spec(core_dir=fpath_core, fpath_schema=fpath_schema):
    errors = []
    yaml_files = glob(os.path.join(core_dir, "*.yaml"))
    print('files to validate: \n')
    print(yaml_files)

    for yaml_file in yaml_files:
        if '.namespace.yaml' not in yaml_file:
            try:
                validate_spec(yaml_file, fpath_schema)
            except jsonschema.ValidationError as err:
                print('*'*60)
                print(yaml_file)
                print(err)
                errors.append(err)
    if errors:
        raise jsonschema.ValidationError(str(errors))


validate_core_spec()
