# Validation performed for R3

## Runtime-confirmed binaries

The reporter tested all three previously deliverable corrected DLLs in Selur
Hybrid on Windows 10 Pro 22H2:

- `hybrid-compatible/x86/colormatrix.dll`: no crash and no color shift.
- `hybrid-compatible/x64/ColorMatrix64.dll`: no crash and no color shift.
- `source-build/x86/colormatrix.dll`: no crash and no color shift.

The reporter also reproduced the original defect by explicitly converting
FCC to SMPTE 240M in VapourSynth, independently confirming the table-index
analysis.

## Source-level tests

- `tests/test_mode_index.py` passes.
- Explicit `Rec.601 -> Rec.709` resolves to index 10.
- Entry 8 remains `FCC -> SMPTE 240M`.
- Hint/D2V row offsets and legacy SIMD groups match the five-wide numbering.

## Hybrid-compatible PE tests

`tests/test_patched_pe.py` checks:

- exact output SHA-256 values;
- PE machine types;
- corrected incoming branch targets;
- x86 code-cave calculation and return target;
- x64 corrected instruction block;
- corrected D2V/hint row offsets.

Both Hybrid-compatible DLLs have additionally passed the reporter's runtime
validation.

## x64 source-build static validation

`tests/test_source_api3_x64.py` checks:

- x86 source-build hash remains byte-identical to the reporter-validated build;
- x64 source-build hash and PE32+ machine type;
- the x64 DLL exports only `AvisynthPluginInit3`;
- Init3 stores the host's second argument and calls `AddFunction` at vtable
  offset `0x30`;
- `IClip::GetVersion()` returns 6;
- the source header contains the expected linkage-offset and object-size
  assertions;
- the source uses a real `AVS_Linkage`-backed Init3 path.

The x64 source build was linked twice with `/Brepro`; both outputs had the same
SHA-256 value:

```text
2291DDA6A7FEE1D167F79D8846DB19BF4E974A22D795CB01D7BBF0B9764008EF
```

## Remaining runtime test

The R3 x64 source build cannot be executed in the Linux build container. It is
therefore a runtime candidate until tested in Hybrid on Windows. Static checks
substantially reduce ABI risk but do not replace that test.
