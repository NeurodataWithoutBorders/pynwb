"""Utilities for creating a custom TypeMap for testing so that we don't use the global type map."""
import tempfile
from pynwb import get_type_map
from pynwb.spec import NWBNamespaceBuilder, export_spec


NAMESPACE_NAME = "test_core"


def create_test_extension(specs, container_classes, mappers=None):
    ns_builder = NWBNamespaceBuilder(
        name=NAMESPACE_NAME,
        version="0.1.0",
        doc="test extension",
    )
    ns_builder.include_namespace("core")

    output_dir = tempfile.TemporaryDirectory()
    export_spec(ns_builder, specs, output_dir.name)

    # this will copy the global pynwb TypeMap and add the extension types to the copy
    type_map = get_type_map(f"{output_dir.name}/{NAMESPACE_NAME}.namespace.yaml")
    for type_name, container_cls in container_classes.items():
        type_map.register_container_type(NAMESPACE_NAME, type_name, container_cls)
    if mappers:
        for type_name, mapper_cls in mappers.items():
            container_cls = container_classes[type_name]
            type_map.register_map(container_cls, mapper_cls)

    output_dir.cleanup()
    return type_map
