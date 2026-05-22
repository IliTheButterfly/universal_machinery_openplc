# openplc_backend

Backend for [universal_machinery](https://github.com/IliTheButterfly/universal_machinery) targeting the [OpenPLC runtime](https://openplcproject.com/).

OpenPLC accepts IEC 61131-3 programs in PLCopen TC6 XML or Structured Text format.  This package wires the parent project's ST and PLCopen XML emitters into the `Backend` ABC so callers can target OpenPLC the same way they'd target any other vendor.

## Usage

```python
from openplc_backend import OpenPlcBackend

backend = OpenPlcBackend()
backend.write(program, "myprog.st")     # IEC §3 Structured Text
backend.write(program, "myprog.xml")    # PLCopen TC6 XML
program2 = backend.read("myprog.xml")   # round-trip via XML
```

Or via the parent's backend registry:

```python
import openplc_backend  # registers as side-effect
from universal_machinery.backends import get_backend
backend = get_backend("openplc")
```

## Capabilities

| Capability | Supported |
|---|---|
| LD (Ladder Diagram) | yes |
| ST (Structured Text) | yes |
| SFC (Sequential Function Chart) | yes |
| Timers (TON/TOF/TP) | yes |
| Counters (CTU/CTD/CTUD) | yes |
| Compare / Math / Move | yes |
| FUNCTION POUs | yes |
| FUNCTION_BLOCK POUs | yes |
| Jump / Label | yes |
| Parallel branches | yes |
| IEC 3rd-edition OOP (METHOD / INTERFACE / EXTENDS) | no -- matiec rejects |
| Standalone DATA_BLOCK declarations | no -- S7 / CLICK extension, not IEC |
| Reading `.st` back into IL | not yet -- no full-program ST parser upstream |

The capability set tracks what OpenPLC's compiler (matiec) parser-accepts; verified by the parent's `tests/test_matiec_roundtrip.py` (32/32 cases).

## Dependencies

Requires the parent `universal_machinery` project on the Python path -- this backend dispatches all lowering / parsing to it.  In a local checkout:

```bash
pip install -e ./universal_machinery[dev]
pip install -e ./universal_machinery/backends/openplc[dev]
```

## License

AGPL-3.0-or-later, same as the parent project.
See [`LICENSE`](LICENSE) for the full text.

Contributions require a `Signed-off-by` line per the
[Developer Certificate of Origin](https://developercertificate.org/).
