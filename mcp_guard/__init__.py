"""
MCP Guard - Security Scanner for MCP Servers
Audit capabilities, detect risks, generate security reports.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("mcp-guard-py")
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"

__author__ = "Yunare Maia"
__email__ = "yunare@gmail.com"
