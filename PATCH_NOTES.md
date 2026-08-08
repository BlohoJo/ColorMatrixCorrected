# Patch notes

## Root cause

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

## Hybrid binary patches

The supplied Hybrid binaries are separate API3/64-bit ports whose exact source
was not in the repository archive. `tools/patch_hybrid_binaries.py` therefore
performs a narrow, hash-locked patch of those exact DLLs:

- x64: rewrites the constructor arithmetic in place and changes `findMode()`
  row offsets from `8/12/4` to `10/15/5`.
- x86: redirects the constructor's old four-wide calculation to an executable
  code cave inside existing `.text` padding, then changes both inlined
  `findMode()` copies from `8/12/4` to `10/15/5`.

The Hybrid binaries contain only the C conversion path, so no binary SIMD
mode-dispatch changes are needed.

The legacy debug-label selector embedded in the exact Hybrid binaries is not
rewritten. With `debug=true`, a corrected five-wide mode can therefore be
reported as `unknown`; this does not affect pixel processing. The newly
compiled source builds contain corrected diagnostic names.
