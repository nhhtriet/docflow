from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_list_documents():
    response = client.get('/documents/')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]['title'] == 'Sample Document'
