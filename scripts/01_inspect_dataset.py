"""Download and audit official UCI diabetes data (no ML training)."""
from __future__ import annotations

import argparse
import io
import json
from datetime import datetime, timezone
from pathlib import Path
import platform
import sys
import urllib.request
import zipfile

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data_contract import audit_frame, sha256_file  # noqa: E402

UCI_URL = (
    "https://archive.ics.uci.edu/static/public/296/"
    "diabetes%2B130-us%2Bhospitals%2Bfor%2Byears%2B1999-2008.zip"
)
UCI_PAGE = "https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008"
DEFAULT_CSV = ROOT / "data" / "raw" / "diabetic_data.csv"


def download_csv(dest: Path) -> str:
    """Download official ZIP and copy only the named CSV. Return ZIP SHA-256."""
    import hashlib
    req = urllib.request.Request(UCI_URL, headers={"User-Agent": "ResearchDatasetAudit/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            payload = response.read()
    except Exception as exc:
        raise RuntimeError(
            f"Unable to download UCI archive: {exc}. "
            "Download manually from the official UCI page and use --csv."
        ) from exc
    zip_hash = hashlib.sha256(payload).hexdigest()
    try:
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            matches = [n for n in archive.namelist() if Path(n).name == "diabetic_data.csv"]
            if len(matches) != 1:
                raise ValueError(f"Expected one diabetic_data.csv in archive, found {len(matches)}")
            csv_payload = archive.read(matches[0])
    except (zipfile.BadZipFile, ValueError) as exc:
        raise RuntimeError(f"UCI download is not a recognized data archive: {exc}") from exc
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(csv_payload)
    return zip_hash


def main() -> None:
    parser = argparse.ArgumentParser(description="UCI #296 data-contract audit (no model fitting).")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--download", action="store_true", help="Download official ZIP if CSV is absent")
    source.add_argument("--csv", type=Path, help="Use local CSV file (e.g. manually downloaded)")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results", help="Where to write JSON audit files")
    args = parser.parse_args()
    path = (args.csv if args.csv is not None else DEFAULT_CSV).resolve()
    zip_sha256 = None
    acquisition = "existing-local-file"
    if args.download and not path.exists():
        zip_sha256 = download_csv(path)
        acquisition = "downloaded-from-uci-archive"
    if not path.exists():
        parser.error(f"Missing {path}; use --download or --csv PATH")
    df = pd.read_csv(path, na_values=["?"], low_memory=False)
    audit = audit_frame(df)
    manifest = {
        "data_source_page": UCI_PAGE,
        "official_archive_url": UCI_URL,
        "source_doi": "10.24432/C5230J",
        "source_license": "CC BY 4.0",
        "acquisition": acquisition,
        "original_archive_sha256_if_downloaded": zip_sha256,
        "csv_sha256": sha256_file(path),
        "csv_filename": path.name,
        "bytes": path.stat().st_size,
        "audit_generated_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": platform.python_version(),
        "pandas_version": pd.__version__,
        "raw_csv_not_committed": True,
    }
    results = args.output_dir.resolve()
    results.mkdir(exist_ok=True)
    for name, content in (("data_audit.json", audit), ("dataset_manifest.json", manifest)):
        (results / name).write_text(json.dumps(content, indent=2) + "\n", encoding="utf-8")

    print("DATA AUDIT COMPLETE — no model was trained")
    print(f"Encounters: {audit['n_encounters']:,} | Patients: {audit['n_unique_patients']:,}")
    print(f"Readmission categories: {audit['target_distribution']}")
    print("Inpatient/emergency values differ in:", audit["candidate_swap_audit"]["n_rows_values_differ"], "rows")
    print("Source CSV SHA-256:", manifest["csv_sha256"])
    print("Row count matches UCI 101,766:", audit["matches_uci_published_101766_rows"])
    print("Saved:", results / "data_audit.json", "and", results / "dataset_manifest.json")
    if not audit["matches_uci_published_101766_rows"]:
        print("WARNING: Row count differs from official UCI page. Verify the source before research modeling.")


if __name__ == "__main__":
    main()
