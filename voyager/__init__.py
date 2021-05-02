import pkg_resources
if not 'gdstk' in {pkg.key for pkg in pkg_resources.working_set} and not 'gdspy' in {pkg.key for pkg in pkg_resources.working_set}:
    raise ImportError("Not gdstk, nor gdspy is installed. The package will not work.")

from .pls import Positionlist, read_pls
from .wor import WorkingArea, read_wor
