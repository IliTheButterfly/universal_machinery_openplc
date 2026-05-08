"""openplc_backend -- emit PLCopen XML / Structured Text consumable by OpenPLC.

OpenPLC (https://openplcproject.com/) is an open-source IEC 61131-3 runtime
that accepts programs in PLCopen XML or Structured Text format.  This
backend converts a `universal_machinery.il` program into one of those.

Status: SKELETON.  No emitter yet.

Public API (planned)::

    from openplc_backend import OpenPlcBackend
    backend = OpenPlcBackend()
    backend.write(program, "myprogram.st")     # Structured Text
    backend.write(program, "myprogram.xml")    # PLCopen XML
"""
from .backend import OpenPlcBackend

__all__ = ["OpenPlcBackend"]
__version__ = "0.0.1"
