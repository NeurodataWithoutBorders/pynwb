# Understanding PyNWB's Internal Workflow: A Hands-on Tutorial

This tutorial demonstrates the internal workflow of PyNWB by showing how to manually use the internal components to create an NWB file. We'll create a simple TimeSeries and see exactly how TypeMap, BuildManager, and ObjectMapper work together.

## Setup and Imports

```python
from datetime import datetime
from uuid import uuid4
import numpy as np
from dateutil import tz

from pynwb import NWBHDF5IO, NWBFile, TimeSeries, get_type_map
from hdmf.build import GroupBuilder, DatasetBuilder, BuildManager
from hdmf.common import DynamicTable

# First, let's create our data
data = np.linspace(0, 100, 1000)
timestamps = np.linspace(0, 100, 1000)
```

## 1. Creating Containers

First, let's create our containers the normal way:

```python
# Create an NWBFile container
nwbfile = NWBFile(
    session_description='Demonstrating internal workflow',
    identifier=str(uuid4()),
    session_start_time=datetime.now(tz=tz.gettz('US/Pacific'))
)

# Create a TimeSeries container
time_series = TimeSeries(
    name='test_timeseries',
    data=data,
    timestamps=timestamps,
    unit='meters'
)

# Add the TimeSeries to the file
nwbfile.add_acquisition(time_series)
```

## 2. Manual Build Process

Now let's see how to manually build these containers using the internal components:

```python
# Get the namespace catalog and type map
type_map = get_type_map()

# Create a BuildManager with the type map
build_manager = BuildManager(type_map)

# Get the ObjectMapper for the TimeSeries
# The type map will find the appropriate mapper based on the container type
ts_mapper = type_map.get_map(time_series)

# Manually create the TimeSeries builder
ts_builder = GroupBuilder(
    name='test_timeseries',
    attributes={
        'namespace': 'core',
        'neurodata_type': 'TimeSeries',
        'unit': 'meters'
    },
    datasets={
        'data': DatasetBuilder(
            name='data',
            data=data,
            attributes={'unit': 'meters'}
        ),
        'timestamps': DatasetBuilder(
            name='timestamps',
            data=timestamps
        )
    }
)

# Get the ObjectMapper for the NWBFile
# The type map will find the appropriate mapper based on the container type
nwbfile_mapper = type_map.get_map(nwbfile)

# Manually create the NWBFile builder with required fields
nwbfile_builder = GroupBuilder(
    name='root',
    attributes={
        'nwb_version': '2.0.0',
        'session_description': 'Demonstrating internal workflow',
        'identifier': nwbfile.identifier,
        'session_start_time': nwbfile.session_start_time,
        'namespace': 'core',
        'neurodata_type': 'NWBFile'
    }
)

# Create and add acquisition group
acquisition_group = GroupBuilder(
    name='acquisition',
    groups={'test_timeseries': ts_builder}
)
nwbfile_builder.set_group(acquisition_group)
```

## 3. Demonstrating the Build Process

Let's see how BuildManager normally handles this process:

```python
# The normal automatic build process
def demonstrate_build_process():
    """
    Demonstrate how BuildManager automatically handles the build process
    """
    # Initialize a new BuildManager
    build_manager = BuildManager(type_map)
    
    # Build the TimeSeries container into a builder
    # BuildManager will:
    # 1. Get the appropriate ObjectMapper from TypeMap
    # 2. Use the ObjectMapper to convert the container to a builder
    # 3. Cache the builder for future reference
    ts_builder = build_manager.build(time_series, source='example.nwb')
    print("TimeSeries builder created:")
    print(f"- Name: {ts_builder.name}")
    print(f"- Attributes: {ts_builder.attributes}")
    print(f"- Datasets: {list(ts_builder.datasets.keys())}")
    
    # Build the NWBFile container into a builder
    # The same process happens:
    # 1. Get NWBFileMap from TypeMap
    # 2. Use NWBFileMap to convert NWBFile to a builder
    # 3. Cache the builder
    nwbfile_builder = build_manager.build(nwbfile, source='example.nwb')
    print("\nNWBFile builder created:")
    print(f"- Name: {nwbfile_builder.name}")
    print(f"- Attributes: {nwbfile_builder.attributes}")
    print(f"- Groups: {list(nwbfile_builder.groups.keys())}")
    
    return nwbfile_builder

# Run the demonstration to see the automatic build process
built_file = demonstrate_build_process()
```

## 4. Writing to File

Finally, let's write our manually built file:

```python
def write_nwb_file(builder, filename='example.nwb'):
    """Write an NWB file from a builder"""
    with NWBHDF5IO(filename, 'w') as io:
        io.write_builder(builder)
    
    # Verify by reading it back
    with NWBHDF5IO(filename, 'r') as io:
        read_nwbfile = io.read()
        print(f"\nFile written and read back successfully:")
        print(f"- Session description: {read_nwbfile.session_description}")
        ts = read_nwbfile.acquisition['test_timeseries']
        print(f"- TimeSeries data shape: {ts.data.shape}")
        print(f"- TimeSeries unit: {ts.unit}")

# Write the file using our manually created builder
write_nwb_file(nwbfile_builder)
```

## 5. Understanding the Components

### TypeMap
The TypeMap is our schema registry that maintains mappings between Python classes and NWB specifications. It provides:

1. Namespace Management:
```python
# Access the namespace catalog
namespace_catalog = type_map.namespace_catalog

# Get container class for a data type
container_cls = type_map.get_dt_container_cls(data_type='TimeSeries', 
                                            namespace='core')
```

2. Mapping Management:
```python
# Get the mapper for a container
mapper = type_map.get_map(container)

# Get the class for a builder
cls = type_map.get_cls(builder)

# Build a container into a builder
builder = type_map.build(container, build_manager)

# Construct a container from a builder
container = type_map.construct(builder, build_manager)
```

### ObjectMapper
ObjectMappers handle the conversion between containers and builders. Each mapper:

1. Manages Specifications:
```python
# Access the specification this mapper handles
spec = mapper.spec

# Get attribute specification
attr_spec = mapper.get_attr_spec('data')

# Get constructor argument specification
carg_spec = mapper.get_carg_spec('name')
```

2. Handles Conversion:
```python
# Build a container into a builder
builder = mapper.build(container, build_manager)

# Construct a container from a builder
container = mapper.construct(builder, build_manager)

# Get attribute value from container
value = mapper.get_attr_value(spec, container, build_manager)

# Convert data types according to spec
value, dtype = mapper.convert_dtype(spec, value)
```

### BuildManager
The BuildManager orchestrates the build process. It provides:

1. Build Management:
```python
# Build a container into a builder
builder = build_manager.build(container, source='file.nwb')

# Construct a container from a builder
container = build_manager.construct(builder)
```

2. Cache Management:
```python
# Get cached builder for a container
builder = build_manager.get_builder(container)

# Clear the build cache
build_manager.clear_cache()
```

3. Reference Handling:
```python
# Queue a reference to be built later
build_manager.queue_ref(ref_builder)

# Get proxy for a container
proxy = build_manager.get_proxy(container)
```

This tutorial showed how these components work together to convert between Python objects and the NWB format. The BuildManager uses TypeMap to find the right ObjectMapper for each container, and the ObjectMapper handles the actual conversion according to the NWB specification.
