# Portable source build

`build_portable_clang_cl.sh` cross-compiles the corrected source with
`clang-cl` and `lld-link`.

## Supported output

The default build produces:

- `bin/source-build/x86/colormatrix.dll`

This 32-bit DLL was runtime-tested by the reporter in Selur Hybrid and produced
the correct Rec.601 -> Rec.709 result.

## Unsupported x64 reference output

The supplied upstream repository contains an AviSynth 2.5-era C++ SDK header.
Hybrid's 64-bit runtime uses AviSynth 2.6 API3 linkage. A DLL cannot be made ABI
compatible merely by adding an `AvisynthPluginInit3` function and storing the
linkage pointer; the C++ inline wrappers and data/interface ABI also need the
matching API3 header.

For source-review purposes only, the old experimental x64 cross-build can be
requested with:

```bash
BUILD_UNSUPPORTED_X64_REFERENCE=1 build/build_portable_clang_cl.sh
```

It is placed under `bin/unsupported-reference/x64/` and **must not be installed
in Hybrid**. The reporter confirmed that this reference build crashes in the
64-bit Hybrid path.

Use the R2 `hybrid-compatible/x64/ColorMatrix64.dll`, which is a narrow patch of
Hybrid's original ABI-compatible x64 DLL, until the matching classic x64/API3
port source or SDK is available.
