# flake8: noqa: F401
import os.path

from .spec import NAME_WILDCARD
from .spec import Spec
from .spec import AttributeSpec
from .spec import DtypeSpec
from .spec import DtypeHelper
from .spec import RefSpec
from .spec import DatasetSpec
from .spec import LinkSpec
from .spec import GroupSpec
from .catalog import SpecCatalog
from .namespace import SpecNamespace
from .namespace import NamespaceCatalog
from .namespace import SpecReader
from .write import NamespaceBuilder
from .write import SpecWriter

from ..utils import docval
