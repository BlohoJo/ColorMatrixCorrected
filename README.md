# ColorMatrix 2.6.1 — five-wide indexing fix

This repository is a corrected derivative of the user-supplied
`sorayuki/ColorMatrix` master snapshot.

## Fixed defect

ColorMatrix 2.6 expanded its luma-coefficient list from four matrices to five
when Rec.2020 support was added, so the flattened conversion table became 5×5.
Several call sites still indexed it as a four-column table. In particular:

```cpp
source * 4 + dest
```

has been replaced with a single five-wide helper:

```cpp
#define MATRIX_MODE_INDEX(source, dest) \
    ((source) * YUV_COEFFS_LUMA_COUNT + (dest))
```

For `Rec.601 -> Rec.709`, the correct index is now `2 * 5 + 0 = 10` rather than
8. Index 8 belongs to `FCC -> SMPTE 240M` in the five-wide table.

## Other corrections

- D2V/hint-based source detection now uses the same five-wide index helper.
- Legacy MMX/SSE2 dispatcher mode numbers were remapped to the 5×5 table.
- Diagnostic conversion names cover all 25 source/destination pairs.
- Conversion-array bounds are checked before use.
- The coefficient scratch array uses the shared conversion-count constant.
- Small portability changes permit C-only x86/x64 reference builds.

## Binaries

The separately supplied binary package contains two kinds of DLLs:

1. **`hybrid-drop-in` — recommended for Hybrid.** These are byte-level patches
   of the exact 32-bit and 64-bit DLLs supplied with the report. Their original
   exports, imports, ABI, and all unrelated machine code are retained.
2. **`source-build` — review/reference builds.** These are newly compiled from
   this repository using the script under `build/`. They are C-only and have
   not been runtime-tested in Hybrid or AviSynth on Windows.

Back up the original Hybrid DLLs and test a short clip before adopting a
replacement.

## Tests

```bash
python tests/test_mode_index.py
build/build_portable_clang_cl.sh
```

The machine-code patcher verifies the exact SHA-256 of each supported original
DLL and refuses to modify unknown binaries.

## License

The upstream source is distributed under GPLv2; see `gpl.txt`.
