"""
Automated Integration and Security Tests for Jarvis Companion Backend
Tests health check, pairing handshake, capability registry,
two-phase confirmation protocol, and chat execution.
"""

import sys
import unittest
from fastapi.testclient import TestClient
import companion_security as sec
from web_server import app

client = TestClient(app)

class TestJarvisCompanionBackend(unittest.TestCase):

    def setUp(self):
        # Clear tokens and pending actions between tests
        sec.AUTHORIZED_TOKENS.clear()
        sec.PENDING_ACTIONS.clear()

    def test_01_health_check(self):
        """Verify companion server reports healthy status and machine metadata."""
        response = client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["service"], "Jarvis Companion Core")
        self.assertIn("version", data)
        self.assertIn("hostname", data)

    def test_02_capabilities_registry(self):
        """Verify all capability tools are indexed with safety levels."""
        response = client.get("/api/capabilities")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertGreater(data["total"], 5)
        # Ensure high-impact actions like system_shutdown are categorized
        shutdown_cap = next((c for c in data["capabilities"] if c["id"] == "system_shutdown"), None)
        self.assertIsNotNone(shutdown_cap)
        self.assertEqual(shutdown_cap["safety"], "high_impact")

    def test_03_pairing_failure_invalid_code(self):
        """Verify device pairing fails with an incorrect code."""
        response = client.post("/api/auth/pair", json={
            "pairing_code": "000000",
            "device_name": "Test Phone"
        })
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertFalse(data["success"])

    def test_04_pairing_success_valid_code(self):
        """Verify valid pairing code issues a Bearer token."""
        response = client.post("/api/auth/pair", json={
            "pairing_code": sec.PAIRING_CODE,
            "device_name": "Google Pixel 8"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertTrue(data["token"].startswith("jarvis_sec_"))
        # Verify token is in authorized set
        self.assertTrue(sec.verify_token(data["token"]))

    def test_05_high_impact_action_confirmation_protocol(self):
        """
        Verify that requesting a high-impact operation (e.g. shutdown)
        does NOT execute immediately, but returns a confirmation requirement.
        """
        # Pair first
        pair_res = client.post("/api/auth/pair", json={"pairing_code": sec.PAIRING_CODE})
        token = pair_res.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Request shutdown
        req_res = client.post("/api/execute_tool", json={
            "action": "system_shutdown",
            "param": "30"
        }, headers=headers)

        self.assertEqual(req_res.status_code, 200)
        data = req_res.json()
        self.assertTrue(data["requires_confirmation"])
        self.assertIn("pending_action_id", data)
        action_id = data["pending_action_id"]

        # Confirm cancellation protocol
        cancel_res = client.post("/api/confirm_action", json={
            "action_id": action_id,
            "confirmed": False
        }, headers=headers)
        self.assertEqual(cancel_res.status_code, 200)
        self.assertFalse(cancel_res.json()["executed"])

    def test_06_chat_endpoint_nlp(self):
        """Verify /api/chat responds with Hinglish AI reply and metadata."""
        pair_res = client.post("/api/auth/pair", json={"pairing_code": sec.PAIRING_CODE})
        token = pair_res.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post("/api/chat", json={
            "message": "hello",
            "voice": "en-IN-PrabhatNeural"
        }, headers=headers)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertTrue(len(data["reply"]) > 0)


if __name__ == "__main__":
    unittest.main()
