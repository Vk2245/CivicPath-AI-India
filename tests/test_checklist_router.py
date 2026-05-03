"""test_checklist_router.py — Document validation endpoint tests."""

import base64


class TestValidateDoc:
    def test_validate_doc_success(self, client):
        fake_image = base64.b64encode(b"x" * 200).decode()
        response = client.post(
            "/checklist/validate-doc",
            json={"image_base64": fake_image, "document_type": "voter_id"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "is_valid" in data
        assert data["google_service"] == "Google Gemini Vision API"

    def test_validate_doc_too_short_image(self, client):
        response = client.post(
            "/checklist/validate-doc", json={"image_base64": "abc", "document_type": "voter_id"}
        )
        assert response.status_code == 422

    def test_validate_doc_default_type(self, client):
        fake_image = base64.b64encode(b"x" * 200).decode()
        response = client.post("/checklist/validate-doc", json={"image_base64": fake_image})
        assert response.status_code == 200
