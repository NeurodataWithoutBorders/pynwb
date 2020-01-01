import os
import ruamel.yaml as yaml
import json
from glob import glob
from argparse import ArgumentParser

import jsonschema


def validate_spec(fpath_spec, fpath_schema):

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


def validate_core_spec():
    cur_file = os.path.dirname(os.path.realpath(__file__))
    fpath_schema = os.path.join(os.path.split(cur_file)[0], 'nwb-schema', 'nwb.schema.json')
    core_dir = os.path.join(os.path.split(cur_file)[0], 'nwb-schema', 'core')

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


def main():

    parser = ArgumentParser(description="Validate an NWB specification")
    parser.add_argument("paths", type=str, nargs='+', help="yaml file paths")
    parser.add_argument("-m", "--metaschema", type=str,
                        help=".json.schema file used to validate yaml files")
    args = parser.parse_args()

    for path in args.paths:
        if os.path.isfile(path):
            validate_spec(path, args.metaschema)
        elif os.path.isdir(path):
            for ipath in glob(os.path.join(path, '*.yaml')):
                validate_spec(ipath, args.metaschema)
        else:
            raise ValueError('path must be a valid file or directory')


if __name__ == "__main__":
    main()
