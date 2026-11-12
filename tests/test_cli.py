"""The CLI must produce files for a controlled fixture; not a real-data audit."""
import json
import subprocess
import sys
from pathlib import Path

from test_data_contract import sample_frame

ROOT = Path(__file__).resolve().parents[1]


def test_cli_writes_audit_and_manifest(tmp_path):
    csv_file = tmp_path / "synthetic_fixture.csv"
    output = tmp_path / "out"
    sample_frame().to_csv(csv_file, index=False)
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "01_inspect_dataset.py"),
         "--csv", str(csv_file), "--output-dir", str(output)],
        capture_output=True, text=True, check=True,
        cwd=str(ROOT),
    )
    audit = json.loads((output / "data_audit.json").read_text())
    manifest = json.loads((output / "dataset_manifest.json").read_text())
    assert audit["n_encounters"] == 4
    assert not audit["matches_uci_published_101766_rows"]
    assert manifest["csv_filename"] == "synthetic_fixture.csv"
    assert len(manifest["csv_sha256"]) == 64
    assert "WARNING" in result.stdout
