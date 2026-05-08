# openplc_backend

Backend for [universal_machinery](https://github.com/iliana/universal_machinery) targeting the [OpenPLC runtime](https://openplcproject.com/).

**Status: skeleton — emitter not yet written.**

OpenPLC accepts programs in PLCopen XML or Structured Text (IEC 61131-3 Part 3).  This package will lower a vendor-neutral `universal_machinery.il` program into one of those formats.

## Roadmap

- [ ] Structured-Text emitter (the simpler path)
- [ ] PLCopen TC6 XML emitter (preserves visual ladder structure)
- [ ] Reverse: import .st back into `universal_machinery.il`
- [ ] Tests against the OpenPLC reference compiler

## License

GPL-3.0-or-later, same as the parent project.
