"""Copy BER pilots comparison PNGs from run dirs to summary/pilots/ if missing."""
from pathlib import Path
import shutil

_summary = Path(__file__).resolve().parent
pilots_dir = _summary / "pilots"
pilots_dir.mkdir(exist_ok=True)

root = _summary.parent.parent  # results -> project root
for eq in ["zf", "mmse"]:
    name = f"ber_comparison_pilots_5000symbols_{eq}.png"
    dst = pilots_dir / name
    if dst.exists():
        continue
    src = root / "results" / f"5000_symbols_multipath_{eq}_pilots" / "images" / name
    if src.exists():
        shutil.copy2(src, dst)
        print(f"Copied: {name} -> summary/pilots/")
    else:
        print(f"Source not found: {src}")
print("Done.")
