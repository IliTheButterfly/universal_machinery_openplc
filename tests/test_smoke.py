"""Smoke + round-trip tests for openplc_backend.

``OpenPlcBackend`` dispatches ``write()`` to ``universal_machinery``'s
ST / PLCopen XML emitters and ``read()`` to the PLCopen XML reader.
These tests pin the public API surface and exercise the real lowering
end-to-end against representative IL programs.
"""
from __future__ import annotations

from pathlib import Path

import pytest


# -----------------------------------------------------------------------------
# Public API surface
# -----------------------------------------------------------------------------


def test_package_imports_cleanly():
    import openplc_backend
    assert openplc_backend.__all__ == ["OpenPlcBackend"]


def test_version_exported():
    import openplc_backend
    assert isinstance(openplc_backend.__version__, str)
    assert openplc_backend.__version__


def test_backend_class_instantiable():
    from openplc_backend import OpenPlcBackend
    backend = OpenPlcBackend()
    assert backend is not None


def test_backend_advertises_name():
    """The Backend ABC contract: each backend has a ``name`` attribute.
    OpenPlcBackend's must be 'openplc'."""
    from openplc_backend import OpenPlcBackend
    assert OpenPlcBackend.name == "openplc"


def test_backend_capabilities_is_a_frozenset():
    """``capabilities`` is the Backend ABC's declaration of which IL
    constructs this backend faithfully lowers.  OpenPLC's compiler
    (matiec) accepts the full IEC 2nd-edition surface but rejects
    3rd-edition OOP (METHOD / INTERFACE / EXTENDS); the capability
    set reflects that subset."""
    from openplc_backend import OpenPlcBackend
    assert isinstance(OpenPlcBackend.capabilities, frozenset)
    # Sanity-check the headline capabilities are present.
    for cap in ("ld", "st", "sfc", "timers", "counters", "functions",
                "function_blocks"):
        assert cap in OpenPlcBackend.capabilities, (
            f"OpenPlcBackend missing expected capability: {cap}"
        )


def test_backend_registered_in_universal_machinery():
    """``@register('openplc')`` makes the backend discoverable via
    ``universal_machinery.backends.get_backend('openplc')`` after the
    package is imported."""
    import openplc_backend  # noqa: F401  (side-effect: registers)
    from universal_machinery.backends import get_backend, registered_names
    assert "openplc" in registered_names()
    backend = get_backend("openplc")
    assert backend.__class__.__name__ == "OpenPlcBackend"


# -----------------------------------------------------------------------------
# Round-trip: write + read via PLCopen XML
# -----------------------------------------------------------------------------


def _representative_program():
    """A small Program exercising the headline IL surface: LD body
    with contacts/coils/timer/counter + ST control flow inside a
    FUNCTION POU + a Configuration block.  Used as the smoke target
    for the real round-trip path."""
    from universal_machinery.builders import (
        assign, coil, fcall_expr, fn, no, prog, program, rung, ton,
        var, var_in,
    )
    from universal_machinery.il import NamedType, TagType
    from universal_machinery.il.ast import Var, VarDirection
    return program(subroutines=[
        fn("Doubled",
           return_type=TagType.INT,
           inputs=[var_in("x", TagType.INT)],
           st_body=[assign("Doubled", "x")]),
        prog("Main", main=True,
             local_vars=[
                 var("trigger", TagType.BOOL),
                 var("done", TagType.BOOL),
                 Var(name="t1", data_type=NamedType("TON"),
                     direction=VarDirection.LOCAL),
             ],
             rungs=[
                 rung(no("trigger"),
                       ton("t1", 1000, done_bit="done")),
                 rung(no("done"), coil("done")),
             ]),
    ])


def test_write_xml_produces_xsd_valid_output(tmp_path):
    """``backend.write(program, '*.xml')`` must produce XSD-valid
    PLCopen TC6 v2.01 -- delegated to the parent's emitter, but pin
    the integration here so a regression upstream surfaces in the
    backend's CI rather than requiring a parent run."""
    from openplc_backend import OpenPlcBackend
    from universal_machinery.emitters.plcopen_xml import validate_plcopen_xml
    backend = OpenPlcBackend()
    out = tmp_path / "prog.xml"
    backend.write(_representative_program(), str(out))
    xml = out.read_text()
    # validate_plcopen_xml raises on schema violations; passing
    # means the emit shape matches the bundled XSD.
    validate_plcopen_xml(xml)


def test_write_st_emits_iec_3_structured_text(tmp_path):
    """``backend.write(program, '*.st')`` produces IEC §3 ST.  We
    don't validate against matiec here (that lives in the parent's
    test suite); we pin that the file is non-empty and contains the
    distinctive ST headers."""
    from openplc_backend import OpenPlcBackend
    backend = OpenPlcBackend()
    out = tmp_path / "prog.st"
    backend.write(_representative_program(), str(out))
    text = out.read_text()
    assert "PROGRAM Main" in text
    assert "FUNCTION Doubled" in text
    assert "END_PROGRAM" in text
    assert "END_FUNCTION" in text


def test_round_trip_via_xml_preserves_pou_structure(tmp_path):
    """``backend.write -> backend.read`` over PLCopen XML must
    preserve the POU set.  Lossless round-trip is the cert-grade
    bar that matters; deeper structural fidelity is covered by the
    parent's XML reader test suite (``tests/parsers/``)."""
    from openplc_backend import OpenPlcBackend
    backend = OpenPlcBackend()
    out = tmp_path / "prog.xml"
    src = _representative_program()
    backend.write(src, str(out))
    parsed = backend.read(str(out))
    assert sorted(s.name for s in parsed.subroutines) == \
        sorted(s.name for s in src.subroutines)


# -----------------------------------------------------------------------------
# Error handling: unsupported suffixes + unimplemented .st read
# -----------------------------------------------------------------------------


def test_write_rejects_unknown_suffix(tmp_path):
    """A suffix the backend doesn't know how to emit must raise
    ``ValueError`` with a clear message rather than silently
    producing the wrong format."""
    from openplc_backend import OpenPlcBackend
    backend = OpenPlcBackend()
    out = tmp_path / "prog.txt"
    with pytest.raises(ValueError, match="unsupported suffix"):
        backend.write(_representative_program(), str(out))


def test_read_st_parses_via_parse_program(tmp_path):
    """``.st`` parsing wired in via the parent's
    ``parsers.st_text.parse_program`` (universal_machinery PR
    #84).  Round-trip pinned: write ST, read it back, check the
    POU set survives.

    Limited to what ``parse_program`` v1 supports (no FB instance
    types like TON, no AT clauses, no SFC) -- use a minimal LD
    program with no FB references for the round-trip."""
    from openplc_backend import OpenPlcBackend
    from universal_machinery.builders import (
        coil, no, prog, program, rung, var,
    )
    from universal_machinery.il import TagType
    backend = OpenPlcBackend()
    out = tmp_path / "prog.st"
    p = program(subroutines=[
        prog("Main", main=True,
             local_vars=[var("x", TagType.BOOL), var("y", TagType.BOOL)],
             rungs=[rung(no("x"), coil("y"))]),
    ])
    backend.write(p, str(out))
    parsed = backend.read(str(out))
    assert sorted(s.name for s in parsed.subroutines) == ["Main"]


def test_read_rejects_unknown_suffix(tmp_path):
    from openplc_backend import OpenPlcBackend
    backend = OpenPlcBackend()
    bogus = tmp_path / "prog.txt"
    bogus.write_text("nope")
    with pytest.raises(ValueError, match="unsupported suffix"):
        backend.read(str(bogus))
