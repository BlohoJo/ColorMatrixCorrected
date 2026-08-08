# Validation performed for R2

## Source-level validation

- `tests/test_mode_index.py` passes.
- Explicit `Rec.601 -> Rec.709` resolves to index 10 in the 5×5 table.
- Entry 8 remains `FCC -> SMPTE 240M`, matching the reporter's independent
  VapourSynth reproduction of the original defect.
- Hint/D2V row offsets and legacy SIMD dispatcher groups were checked against
  the corrected five-wide numbering.
- The reporter runtime-tested the 32-bit source build in Selur Hybrid: all 240
  frames encoded successfully, and the visible color error was corrected.

## R2 Hybrid binary validation

- The patcher accepts only these original SHA-256 values:
  - x86: `3d042d59df206cd45586348c72d2458dee6e5dd2fc5c8540916245da1a7c8ec2`
  - x64: `654454449f992122bfae5671003491db67212ee6b15fe0975f81b8b47223fedf`
- Every original byte sequence is verified before replacement.
- x86 R2 branch at RVA `0x4115` targets the trampoline at `0x4161`.
- x86 trampoline targets the code cave at `0x11200`; the cave computes
  `dest + source * 5`, stores it, and returns to `0x4175`.
- x64 R2 branch at RVA `0x30E7` targets the beginning of the rewritten block at
  `0x3145`, not the middle of the store instruction.
- x64 block computes `source * 5 + dest`, stores it, and continues at `0x3160`.
- `tests/test_patched_pe.py` checks those branches, instruction bytes, PE
  machine types, and exact output SHA-256 values.
- Both ZIP archives pass integrity testing.

## Runtime status

The R1 x86 and x64 binary patches were invalid and have been withdrawn. The R2
patches correct the identified control-flow errors, but Windows/Hybrid runtime
execution is not available in the build container. They therefore still need
short-clip confirmation on the reporter's system.

The earlier x64 portable source build is not a supported Hybrid binary: it
compiled against an incompatible old C++ header model and was confirmed to
crash. It is omitted from the R2 binary package.
