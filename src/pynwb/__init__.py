'''This package will contain functions, classes, and objects
for reading and writing data in NWB format
'''
import os  # noqa: E402
from warnings import warn  # noqa: E402

import h5py  # noqa: E402
import hdmf  # noqa: E402
from hdmf.data_utils import DataChunkIterator  # noqa: F401,E402
from hdmf.backends.hdf5 import H5DataIO  # noqa: F401,E402
from hdmf.utils import call_docval_func  # noqa E402

from . import io as __io  # noqa: F401,E402
# from .globals import NamespaceCatalog, __NS_CATALOG, __TYPE_MAP # noqa E402
from .core import NWBContainer, NWBData  # noqa: F401,E402
from .base import TimeSeries, ProcessingModule  # noqa: F401,E402
from .file import NWBFile  # noqa: F401,E402
from .spec import (  # noqa E402
    NWBDatasetSpec,
    NWBGroupSpec,
    NWBNamespace,
    NamespaceCatalog,
    __NS_CATALOG,
    __TYPE_MAP,
    hdmf_typemap,
)
from .validation import validate, ValidatorMap  # noqa: F401,E402

from . import behavior  # noqa: F401,E402
from . import device  # noqa: F401,E402
from . import ecephys  # noqa: F401,E402
from . import epoch  # noqa: F401,E402
from . import icephys  # noqa: F401,E402
from . import image  # noqa: F401,E402
from . import misc  # noqa: F401,E402
from . import ogen  # noqa: F401,E402
from . import ophys  # noqa: F401,E402
from . import retinotopy  # noqa: F401,E402
from . import legacy  # noqa: F401,E402

from .utils import (  # noqa: E402
    BuildManager,
    HDMFIO,
    NWBHDF5IO,
    Path,
    TypeMap,
    _HDF5IO,
    __get_resources,
    __resources,
    _get_resources,
    available_namespaces,
    deepcopy,
    docval,
    get_class,
    get_docval,
    get_manager,
    get_type_map,
    getargs,
    # hdmf_typemap,
    load_namespaces,
    popargs,
    register_class,
    register_map,
)
from .globals import CORE_NAMESPACE, __core_ns_file_name  # noqa: E402


from ._version import get_versions  # noqa: E402
__version__ = get_versions()['version']
del get_versions

from ._due import due, BibTeX  # noqa: E402

due.cite(BibTeX("""
@article {R{\"u}bel2021.03.13.435173,
    author = {R{\"u}bel, Oliver and Tritt, Andrew and Ly, Ryan and Dichter, Benjamin K. and Ghosh, Satrajit and Niu, Lawrence and Soltesz, Ivan and Svoboda, Karel and Frank, Loren and Bouchard, Kristofer E.},
    title = {The Neurodata Without Borders ecosystem for neurophysiological data science},
    elocation-id = {2021.03.13.435173},
    year = {2021},
    doi = {10.1101/2021.03.13.435173},
    publisher = {Cold Spring Harbor Laboratory},
    abstract = {The neurophysiology of cells and tissues are monitored electrophysiologically and optically in diverse experiments and species, ranging from flies to humans. Understanding the brain requires integration of data across this diversity, and thus these data must be findable, accessible, interoperable, and reusable (FAIR). This requires a standard language for data and metadata that can coevolve with neuroscience. We describe design and implementation principles for a language for neurophysiology data. Our software (Neurodata Without Borders, NWB) defines and modularizes the interdependent, yet separable, components of a data language. We demonstrate NWB{\textquoteright}s impact through unified description of neurophysiology data across diverse modalities and species. NWB exists in an ecosystem which includes data management, analysis, visualization, and archive tools. Thus, the NWB data language enables reproduction, interchange, and reuse of diverse neurophysiology data. More broadly, the design principles of NWB are generally applicable to enhance discovery across biology through data FAIRness.Competing Interest StatementThe authors have declared no competing interest.},
    URL = {https://www.biorxiv.org/content/early/2021/03/15/2021.03.13.435173},
    eprint = {https://www.biorxiv.org/content/early/2021/03/15/2021.03.13.435173.full.pdf},
    journal = {bioRxiv}
}
"""), description="The Neurodata Without Borders ecosystem for neurophysiological data science",  # noqa: E501
         path="pynwb/", version=__version__, cite_module=True)
del due, BibTeX
