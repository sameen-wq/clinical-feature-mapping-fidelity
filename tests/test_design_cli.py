import json
import subprocess
import sys
from pathlib import Path

from test_experimental_design import frame


def test_design_cli_writes_json(tmp_path):
    root = Path(__file__).resolve().parents[1]
    csv_path = tmp_path / "synthetic.csv"
    out_path = tmp_path / "design.json"
    frame().to_csv(csv_path, index=False)
    process = subprocess.run([sys.executable, str(root / "scripts" / "02_prepare_design.py"), "--csv", str(csv_path), "--out", str(out_path)],
                             capture_output=True, text=True, cwd=root, check=True)
    assert "no models trained" in process.stdout
    saved=json.loads(out_path.read_text())
    assert saved["group_overlap_count"]==0
    assert saved["mapping_intervention"]["oracle_restore_exact"]
