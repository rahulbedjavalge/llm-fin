from fastapi.testclient import TestClient
from backend.main import app
from pathlib import Path


def test_upload_and_ratios():
    client = TestClient(app)
    sample = Path(__file__).parents[2] / "data" / "sample_financials.csv"
    with sample.open("rb") as f:
        files = {"file": ("sample_financials.csv", f, "text/csv")}
        r = client.post("/upload", files=files)
        assert r.status_code == 200
        data = r.json()
        assert "ratios" in data
        assert set(data["ratios"].keys()) >= {
            "gross_margin",
            "operating_margin",
            "net_margin",
            "debt_to_assets",
        }
