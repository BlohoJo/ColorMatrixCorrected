# ColorMatrix 2.6.1 — five-wide indexing fix (R2)

This repository is a corrected derivative of the user-supplied
`sorayuki/ColorMatrix` master snapshot.

## Fixed source defect

ColorMatrix 2.6 expanded its luma-coefficient list from four matrices to five
when Rec.2020 support was added, so the flattened conversion table became 5×5.
Several call sites still indexed it as a four-column table. In particular:

```cpp
source * 4 + dest
```

has been replaced with a shared five-wide helper:

```cpp
#define MATRIX_MODE_INDEX(source, dest) \
    ((source) * YUV_COEFFS_LUMA_COUNT + (dest))
```

For `Rec.601 -> Rec.709`, the correct index is `2 * 5 + 0 = 10`. The
old expression selected index 8, which is `FCC -> SMPTE 240M` in the 5×5
table.

The corrected source was runtime-tested by the reporter through the 32-bit
source build in Selur Hybrid. The requested conversion completed normally and
produced the expected color result.

## Other source corrections

- D2V/hint-based source detection uses the same five-wide index helper.
- Legacy MMX/SSE2 dispatcher mode numbers are remapped to the 5×5 table.
- Diagnostic conversion names cover all 25 source/destination pairs.
- Conversion-array bounds are checked before use.
- The coefficient scratch array uses the shared conversion-count constant.

## R2 correction to the Hybrid binary patcher

The first binary-patch release changed the constructor calculation but failed
to retarget an earlier branch in each original Hybrid DLL:

- In x86, the normal `source != dest` path bypassed the new trampoline, so the
  conversion was not applied.
- In x64, the normal path jumped into the middle of the replacement instruction
  sequence, causing an immediate process crash.

`tools/patch_hybrid_binaries.py` now retargets those incoming branches before
rewriting the index calculation. See `PATCH_NOTES.md` for exact RVAs and byte
changes.

## Binaries

The separately supplied R2 binary package contains:

1. **`hybrid-compatible` — recommended for Selur Hybrid.** These are narrow,
   hash-locked binary patches of the exact original x86 and x64 Hybrid DLLs.
   Their original exports, imports, runtime, ABI, and unrelated machine code
   remain intact.
2. **`source-build/x86` — user-validated source build.** This was newly compiled
   from the corrected repository and has been confirmed to run correctly in
   Hybrid's 32-bit AviSynth path.

A 64-bit source build is deliberately not shipped as a supported Hybrid DLL.
The attached upstream snapshot contains an AviSynth 2.5-era C++ header, while
Hybrid's 64-bit runtime uses the AviSynth 2.6 API3 linkage ABI. The earlier
portable x64 build compiled but crashed in Hybrid. Producing a genuine x64
source build requires the matching classic x64/API3 SDK or the source of
Hybrid's separate 64-bit port; a superficial `AvisynthPluginInit3` wrapper is
not sufficient.

Back up the original Hybrid DLLs and test a short clip before adopting a
replacement. The R2 Hybrid-compatible binaries have been statically validated
but could not be executed in Windows from the build container.

## Tests

```bash
python tests/test_mode_index.py
python tests/test_patched_pe.py \
  --x86 path/to/patched/x86/colormatrix.dll \
  --x64 path/to/patched/x64/ColorMatrix64.dll
```

The patcher verifies the exact SHA-256 of each supported original DLL and every
instruction sequence before modifying it. It refuses unknown binaries.

## License

The upstream source is distributed under GPLv2; see `gpl.txt`.
