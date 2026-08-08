# Patch notes

## Root cause in the upstream source

The source defines five luma coefficient sets in this order:

| Index | Matrix |
|---:|---|
| 0 | Rec.709 |
| 1 | FCC |
| 2 | Rec.601 / SMPTE 170M |
| 3 | SMPTE 240M |
| 4 | Rec.2020 |

`calc_coefficients()` generates every source/destination pair in nested loops,
so `yuv_convert` is row-major with a row width of five. ColorMatrix 2.6 still
used the old four-wide expression in explicit mode selection and old row
offsets in `findMode()`.

Requested `Rec.601 -> Rec.709` therefore selected:

- buggy index: `2 * 4 + 0 = 8`
- actual entry 8 in a 5×5 table: `FCC -> SMPTE 240M`
- correct index: `2 * 5 + 0 = 10`

The reporter independently reproduced the original ColorMatrix result in
VapourSynth by explicitly performing `FCC -> SMPTE 240M`, confirming the
misindexed operation.

## Source changes

- Added `YUV_CONVERSION_COUNT` and `MATRIX_MODE_INDEX`.
- Replaced explicit and hint/D2V index arithmetic with the helper.
- Remapped legacy SIMD modes:
  - kernel 1: `1, 2, 3, 16, 17`
  - kernel 2: `5, 8, 10, 13, 15`
  - kernel 3: `7`
  - kernel 4: `11`
- Replaced the stale four-wide debug-name chain with a 25-entry table.
- Added a defensive index bounds check.

## Hybrid-compatible binary patches

The supplied Hybrid binaries are separate API3/x64 ports whose exact source
was not in the repository archive. `tools/patch_hybrid_binaries.py` therefore
performs a narrow, hash-locked patch of those exact DLLs.

### x86

The original normal-path branch at RVA `0x4115` was:

```asm
jne 0x416c
```

RVA `0x416c` was the old `source * 4 + dest` calculation. R1 replaced the
constructor block at `0x4161` with a trampoline, but left this earlier branch
target unchanged. For `source != dest`, execution therefore jumped past the
trampoline into NOP padding and never stored the corrected mode.

R2 changes the short branch displacement from `75 55` to `75 4A`, making it:

```asm
jne 0x4161
```

The trampoline at `0x4161` then reaches an executable code cave that computes
`source * 5 + dest`, stores the mode, and returns to `0x4175`.

### x64

The original normal-path branch at RVA `0x30E7` was:

```asm
jne 0x3156
```

R1 rewrote the block beginning at `0x3145`. In the replacement layout,
`0x3156` was the second byte of a seven-byte `mov` instruction. The unchanged
branch therefore entered the middle of an instruction and crashed.

R2 changes the short branch displacement from `75 6D` to `75 5C`, making it:

```asm
jne 0x3145
```

The replacement block at `0x3145` computes `source * 5 + dest`, stores it, and
continues at `0x3160`.

### D2V/hint indexing

The x64 `findMode()` row offsets and both inlined x86 copies are also changed
from `8/12/4` to `10/15/5`.

The Hybrid binaries contain only the C conversion path, so no binary SIMD
dispatch changes are required.

The legacy debug-label selector embedded in the exact Hybrid binaries is not
rewritten. With `debug=true`, a corrected five-wide mode can be reported as
`unknown`; this does not affect pixel processing.

## 64-bit source-build limitation

The upstream snapshot's `avisynth.h` is from the older AviSynth 2.5-style C++
interface. Hybrid's x64 runtime loads API3 plugins and supplies an
`AVS_Linkage` table through `AvisynthPluginInit3`. The first portable source
build merely retained that pointer while continuing to use the old header's
inline C++ ABI. It compiled, but the reporter confirmed that it crashes in
Hybrid's x64 path.

This is independent of the five-wide source correction. A supported source-
based x64 DLL requires the matching classic x64/AviSynth 2.6 API3 header and
port source. Until that is available, the R2 ABI-preserving binary patch is the
supported x64 Hybrid replacement.
