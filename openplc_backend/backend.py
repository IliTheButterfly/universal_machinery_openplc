"""OpenPLC backend: emit / read PLCopen XML and IEC §3 Structured Text.

OpenPLC (https://openplcproject.com/) accepts IEC 61131-3 programs in
either PLCopen TC6 XML or Structured Text format -- both are produced
by ``universal_machinery``'s emitter suite.  This package wires those
emitters into the project's ``Backend`` ABC so callers can target
OpenPLC the same way they'd target any other vendor.

The lowering work itself happens upstream in
``universal_machinery.emitters`` -- this backend is a thin dispatcher
that picks the right emitter / parser based on the file suffix and
declares which IL capabilities OpenPLC's compiler accepts.  That
keeps the IEC §3 ST emit and PLCopen XML emit shared with the
parent project's matiec round-trip harness (32/32 cases pass against
``iec2c``), so any matiec compatibility fix benefits OpenPLC
automatically.

Usage::

    from openplc_backend import OpenPlcBackend
    backend = OpenPlcBackend()
    backend.write(program, "myprog.st")     # Structured Text
    backend.write(program, "myprog.xml")    # PLCopen TC6 XML
    program2 = backend.read("myprog.xml")   # round-trip via XML
"""

from __future__ import annotations

from pathlib import Path

from universal_machinery.backends import Backend, register
from universal_machinery.emitters.plcopen_xml import emit_xml
from universal_machinery.emitters.st import emit_program
from universal_machinery.il import Program
from universal_machinery.parsers.plcopen_xml import parse_plcopen_xml_file


@register("openplc")
class OpenPlcBackend(Backend):
    """Lower a ``universal_machinery.il.Program`` into a PLCopen XML
    or Structured Text file accepted by the OpenPLC runtime.

    Output formats:
      ``.st``   IEC §3 Structured Text (the simpler path)
      ``.xml``  PLCopen TC6 XML (preserves visual ladder / FBD topology)

    Capability set is bounded by what OpenPLC's compiler (matiec)
    parser-accepts.  See the parent project's
    ``tests/test_matiec_roundtrip.py`` for the full validated corpus.
    """

    name = "openplc"
    #: Capabilities that OpenPLC's compiler (matiec, IEC 2nd-edition)
    #: accepts via our ST / PLCopen XML emit.  Verified by the parent
    #: project's ``tests/test_matiec_roundtrip.py`` (32/32 cases as
    #: of the integration commit).  Notably absent: IEC 3rd-edition
    #: OOP (METHOD / INTERFACE / EXTENDS) -- matiec rejects those
    #: at the parser level (see ``docs/IEC_CONFORMANCE.md`` in
    #: the parent for the doubly-blocked posture).
    capabilities = frozenset({
        "ld",
        "st",
        "sfc",
        "timers",
        "counters",
        "compare",
        "math",
        "call",
        "functions",
        "function_blocks",
        "jump",
        "parallel",
    })

    def write(self, program: Program, path: str) -> None:
        """Lower ``program`` and write it to ``path``.

        Dispatch is by file suffix: ``.st`` routes to the IEC §3
        Structured Text emitter; ``.xml`` routes to the PLCopen TC6
        XML emitter.  Any other suffix raises ``ValueError`` -- be
        explicit rather than guess what format the caller wanted.
        """
        p = Path(path)
        suffix = p.suffix.lower()
        if suffix == ".st":
            p.write_text(emit_program(program), encoding="utf-8")
        elif suffix == ".xml":
            p.write_text(emit_xml(program), encoding="utf-8")
        else:
            raise ValueError(
                f"OpenPlcBackend.write: unsupported suffix {suffix!r} "
                f"for {p}; expected .st or .xml"
            )

    def read(self, path: str) -> Program:
        """Parse a file from ``path`` and return a Program.

        ``.xml`` routes to the PLCopen TC6 XML reader, which is the
        canonical round-trip path (XSD-validated, lossless for the
        IL features the v2.01 schema covers).

        ``.st`` is not yet supported on the read side: the parent
        project has an ST expression / statement parser
        (``universal_machinery.parsers.st_text``) but no full-program
        ST parser that reconstructs ``Subroutine`` declarations
        with their VAR blocks, ``CONFIGURATION`` / ``RESOURCE`` /
        ``TASK`` blocks, and ``TYPE ... END_TYPE`` blocks.  Callers
        wanting a round-trip should emit + re-read XML for now.
        """
        p = Path(path)
        suffix = p.suffix.lower()
        if suffix == ".xml":
            return parse_plcopen_xml_file(p)
        elif suffix == ".st":
            raise NotImplementedError(
                "OpenPlcBackend.read: .st parsing not yet wired up.  "
                "The parent project ships an ST statement parser at "
                "``universal_machinery.parsers.st_text`` but no full-"
                "program ST parser yet (no Subroutine / Configuration "
                "/ TYPE block reconstruction).  Round-trip via .xml "
                "(``backend.read(path.with_suffix('.xml'))``) until "
                "the ST-program parser lands."
            )
        else:
            raise ValueError(
                f"OpenPlcBackend.read: unsupported suffix {suffix!r} "
                f"for {p}; expected .xml (or .st once parsing lands)"
            )
