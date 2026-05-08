"""OpenPLC backend skeleton.  Not yet functional."""

from __future__ import annotations


class OpenPlcBackend:
    """Lower a universal_machinery.il Program into PLCopen XML or
    Structured Text consumable by the OpenPLC runtime.

    Output formats:
      .st   Structured Text (IEC 61131-3 Part 3)
      .xml  PLCopen TC6 XML

    NOT YET IMPLEMENTED.  Roadmap:
      - Structured-Text emitter for the IL ops in universal_machinery.il
      - PLCopen XML emitter (LadderDiagram for visual fidelity)
      - Reader that imports .st back into IL
    """

    name = "openplc"
    capabilities = frozenset({
        # populate as implemented:
        # "ld",   # ladder diagram output
        # "st",   # structured text output
    })

    def write(self, program, path: str) -> None:
        raise NotImplementedError(
            "OpenPLC backend is a skeleton -- emitter not yet written. "
            "Track progress at https://github.com/iliana/universal_machinery_openplc"
        )

    def read(self, path: str):
        raise NotImplementedError(
            "OpenPLC backend is a skeleton -- reader not yet written."
        )
