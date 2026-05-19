"""Smoke tests for openplc_backend.

The package is currently a skeleton -- ``read`` / ``write`` raise
``NotImplementedError`` and the real emitter logic lives upstream
in the parent ``universal_machinery`` repository's
``universal_machinery.emitters`` package.  These tests pin the
skeleton's API surface so a future emitter implementation doesn't
accidentally change the public shape.
"""
import pytest


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
    """capabilities is a class-level frozenset; the skeleton declares
    it empty until the emitter implementation lands."""
    from openplc_backend import OpenPlcBackend
    assert isinstance(OpenPlcBackend.capabilities, frozenset)


def test_write_raises_not_implemented():
    """Skeleton contract: write() raises NotImplementedError with a
    message pointing to the roadmap, so users discovering this code
    aren't left guessing."""
    from openplc_backend import OpenPlcBackend
    backend = OpenPlcBackend()
    with pytest.raises(NotImplementedError):
        backend.write(None, "/tmp/dummy.st")


def test_read_raises_not_implemented():
    from openplc_backend import OpenPlcBackend
    backend = OpenPlcBackend()
    with pytest.raises(NotImplementedError):
        backend.read("/tmp/dummy.st")
