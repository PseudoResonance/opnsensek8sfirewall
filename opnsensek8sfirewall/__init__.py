import sys
import os
from pathlib import Path

sys.path.append(
    str(os.path.join(Path(__file__).absolute().parent.parent, "lib/pyopnsense"))
)
