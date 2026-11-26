"""The package version, built from the release block in version.py."""
from os.path import dirname, join

_block = {}
with open(join(dirname(__file__), "version.py"), encoding="utf-8") as f:
    exec(f.read(), _block)

__version__ = f"{_block['VERSION_MAJOR']}.{_block['VERSION_MINOR']}.{_block['VERSION_BUILD']}"
if _block["VERSION_ALPHA"]:
    __version__ += f"a{_block['VERSION_ALPHA']}"
