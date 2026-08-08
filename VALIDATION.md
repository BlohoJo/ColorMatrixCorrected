# Validation performed for this release

The following checks were run before packaging:

- `tests/test_mode_index.py` passed.
- The explicit Rec.601 -> Rec.709 index resolves to 10 in the 5x5 table.
- The hint/D2V row offsets and legacy SIMD dispatcher groups were checked
  against the corrected five-wide numbering.
- `tools/patch_hybrid_binaries.py` reproduced the expected x86 and x64 output
  hashes from the exact supplied Hybrid DLLs.
- `tests/test_patched_pe.py` passed for both patched Hybrid DLLs.
- The portable clang-cl build completed for both x86 and x64.
- Two consecutive portable builds produced identical SHA-256 hashes.
- The compiled outputs were inspected as PE32 i386 and PE32+ x86-64 DLLs.
- The compiled x86 DLL exports `_AvisynthPluginInit2@4` and
  `_AvisynthPluginInit3@8`; the compiled x64 DLL exports
  `AvisynthPluginInit2` and `AvisynthPluginInit3`.

Runtime execution inside Selur Hybrid/AviSynth was not possible in the Linux
build container. The ABI-preserving `hybrid-drop-in` binaries in the separate
binary package are therefore recommended for actual Hybrid testing.
