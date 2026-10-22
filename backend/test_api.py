from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_routes():
    # 1. Health check
    res = client.get("/api/health")
    assert res.status_code == 200, res.text
    print("GET /api/health passed:", res.json())

    # 2. Samples
    res = client.get("/api/samples")
    assert res.status_code == 200, res.text
    samples = res.json()
    assert len(samples) >= 4
    print("GET /api/samples passed, sample count:", len(samples))

    # 3. Upload CSV
    with open("backend/app/samples/sample_cbc_anemia.csv", "rb") as f:
        res = client.post("/api/analyze/upload", files={"file": ("sample_cbc_anemia.csv", f, "text/csv")})
    assert res.status_code == 200, res.text
    data = res.json()
    print("POST /api/analyze/upload passed! Overall title:", data["summary"]["overall_title"])

    # 4. Export CSV
    res_csv = client.post("/api/export/csv", json=data)
    assert res_csv.status_code == 200
    print("POST /api/export/csv passed!")

    # 5. Export PDF
    res_pdf = client.post("/api/export/pdf", json=data)
    assert res_pdf.status_code == 200
    print("POST /api/export/pdf passed!")

    print("\nALL FASTAPI ROUTE TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_routes()
