# Portable reference build

`build_portable_clang_cl.sh` cross-compiles 32-bit and 64-bit Windows DLLs with
`clang-cl` and `lld-link`. It intentionally uses the C conversion path for both
architectures and supplies a small compatibility layer because the upstream
snapshot contains a Visual Studio 2005 Win32 project and an AviSynth 2.5-era
SDK header.

The resulting DLLs are placed in:

- `bin/source-build/x86/colormatrix.dll`
- `bin/source-build/x64/ColorMatrix64.dll`

These binaries prove that the corrected source compiles for both Windows
architectures, but they were **not runtime-tested inside Hybrid or AviSynth on
Windows**. The exact source of Hybrid's separately ported API3/x64 DLLs was not
present in the supplied repository archive. For Hybrid, use the
ABI-preserving `hybrid-drop-in` binaries from the separate binary package.
