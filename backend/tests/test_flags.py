from fastapi.testclient import TestClient
from backend.main import app
from pathlib import Path


def test_flags_after_upload():
    client = TestClient(app)
    sample = Path(__file__).parents[2] / "data" / "sample_financials.csv"
    with sample.open("rb") as f:
        files = {"file": ("sample_financials.csv", f, "text/csv")}
        r = client.post("/upload", files=files)
        assert r.status_code == 200
    rf = client.get("/flags")
    assert rf.status_code == 200
    body = rf.json()
    assert "flags" in body
    assert isinstance(body["flags"], list)
