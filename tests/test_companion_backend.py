"""
Automated Integration and Security Tests for Jarvis Companion Backend
Tests health check, single-use pairing handshake, capability registry,
two-phase confirmation protocol, shell injection protection, and voice transcription.
"""

import io
import wave
import unittest
from fastapi.testclient import TestClient
import companion_security as sec
from web_server import app

client = TestClient(app)

def create_dummy_wav() -> bytes:
    """Generate a valid minimal in-memory WAV file for audio tests."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(b"\x00\x00" * 1600)  # 0.1 second of silence
    return buf.getvalue()


class TestJarvisCompanionBackend(unittest.TestCase):

    def setUp(self):
        sec.AUTHORIZED_TOKENS.clear()
        sec.PENDING_ACTIONS.clear()
        # Reset pairing state for testing
        sec.PAIRING_STATE["consumed"] = False
        sec.PAIRING_STATE["code"] = "749201"
        sec.PAIRING_STATE["expires_at"] = 9999999999.0
        sec.FAILED_ATTEMPTS["count"] = 0
        sec.FAILED_ATTEMPTS["cooldown_until"] = 0.0

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
        active_code = sec.get_active_pairing_code()
        response = client.post("/api/auth/pair", json={
            "pairing_code": active_code,
            "device_name": "Google Pixel 8"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertTrue(data["token"].startswith("jarvis_sec_"))
        self.assertTrue(sec.verify_token(data["token"]))

    def test_05_high_impact_action_confirmation_protocol(self):
        """
        Verify that requesting a high-impact operation (e.g. shutdown)
        does NOT execute immediately, but returns a confirmation requirement.
        """
        active_code = sec.get_active_pairing_code()
        pair_res = client.post("/api/auth/pair", json={"pairing_code": active_code})
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
        active_code = sec.get_active_pairing_code()
        pair_res = client.post("/api/auth/pair", json={"pairing_code": active_code})
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

    def test_07_pairing_code_single_use_and_rotation(self):
        """Verify that pairing codes cannot be reused once consumed."""
        active_code = sec.get_active_pairing_code()

        # First use succeeds
        res1 = client.post("/api/auth/pair", json={
            "pairing_code": active_code,
            "device_name": "Device 1"
        })
        self.assertEqual(res1.status_code, 200)

        # Second use of SAME code must fail (single-use enforcement)
        res2 = client.post("/api/auth/pair", json={
            "pairing_code": active_code,
            "device_name": "Attacker Device"
        })
        self.assertEqual(res2.status_code, 401)

    def test_08_shell_command_injection_rejected(self):
        """Verify that parameters with dangerous shell metacharacters are rejected."""
        active_code = sec.get_active_pairing_code()
        pair_res = client.post("/api/auth/pair", json={"pairing_code": active_code})
        token = pair_res.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Attempt command injection
        res = client.post("/api/execute_tool", json={
            "action": "open_app",
            "param": "calc.exe & dir"
        }, headers=headers)

        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertFalse(data["success"])
        self.assertIn("Security violation", data.get("error", ""))

    def test_09_voice_transcription_endpoint(self):
        """Verify voice upload transcription endpoint accepts audio."""
        active_code = sec.get_active_pairing_code()
        pair_res = client.post("/api/auth/pair", json={"pairing_code": active_code})
        token = pair_res.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        wav_bytes = create_dummy_wav()
        files = {"file": ("test_voice.wav", wav_bytes, "audio/wav")}

        res = client.post("/api/voice/transcribe", files=files, headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertIn("transcript", data)

    def test_10_high_impact_token_binding(self):
        """Verify that pending high-impact actions cannot be confirmed by a different token."""
        active_code = sec.get_active_pairing_code()
        pair_res1 = client.post("/api/auth/pair", json={"pairing_code": active_code, "device_name": "Device 1"})
        token1 = pair_res1.json()["token"]

        active_code2 = sec.get_active_pairing_code()
        pair_res2 = client.post("/api/auth/pair", json={"pairing_code": active_code2, "device_name": "Device 2"})
        token2 = pair_res2.json()["token"]

        # Device 1 initiates shutdown
        req_res = client.post("/api/execute_tool", json={
            "action": "system_shutdown",
            "param": "30"
        }, headers={"Authorization": f"Bearer {token1}"})
        aid = req_res.json()["pending_action_id"]

        # Device 2 tries to confirm Device 1's action with token2 -> must be rejected
        tamper_res = client.post("/api/confirm_action", json={
            "action_id": aid,
            "confirmed": True
        }, headers={"Authorization": f"Bearer {token2}"})
        self.assertEqual(tamper_res.status_code, 404)

        # Device 1 cancels its own action -> succeeds
        cancel_res = client.post("/api/cancel_action", json={
            "action_id": aid,
            "confirmed": False
        }, headers={"Authorization": f"Bearer {token1}"})
        self.assertEqual(cancel_res.status_code, 200)

    def test_11_real_tool_execution_routing(self):
        """Verify real tool execution for datetime and net_status via /api/execute_tool."""
        active_code = sec.get_active_pairing_code()
        pair_res = client.post("/api/auth/pair", json={"pairing_code": active_code})
        token = pair_res.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Test datetime tool
        dt_res = client.post("/api/execute_tool", json={"action": "datetime"}, headers=headers)
        self.assertEqual(dt_res.status_code, 200)
        self.assertTrue(dt_res.json()["success"])
        self.assertTrue(len(dt_res.json()["result"]) > 5)

        # Test net_status tool
        net_res = client.post("/api/execute_tool", json={"action": "net_status"}, headers=headers)
        self.assertEqual(net_res.status_code, 200)
        self.assertTrue(net_res.json()["success"])
        self.assertIn("Internet speed", net_res.json()["result"])

    def test_12_pairing_rate_limiting_brute_force(self):
        """Verify brute-force pairing attempts trigger cooldown protection."""
        # 5 consecutive failed pairing attempts
        for _ in range(5):
            client.post("/api/auth/pair", json={"pairing_code": "999999", "device_name": "Attacker"})

        # 6th attempt even with correct code is locked out during cooldown
        active_code = sec.get_active_pairing_code()
        blocked_res = client.post("/api/auth/pair", json={"pairing_code": active_code, "device_name": "Attacker"})
        self.assertEqual(blocked_res.status_code, 401)

    def test_13_dangerous_metacharacters_rejected(self):
        """Verify various shell metacharacters (\n, ;, |, $, `, etc.) are rejected."""
        active_code = sec.get_active_pairing_code()
        pair_res = client.post("/api/auth/pair", json={"pairing_code": active_code})
        token = pair_res.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        payloads = [
            "notepad.exe\ncalc.exe",
            "calc; dir",
            "calc | dir",
            "calc $(whoami)",
            "calc `id`",
            "calc & pause"
        ]
        for payload in payloads:
            res = client.post("/api/execute_tool", json={
                "action": "open_app",
                "param": payload
            }, headers=headers)
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertFalse(data["success"], f"Payload '{payload}' should have been rejected")
            self.assertIn("Security violation", data.get("error", ""))


if __name__ == "__main__":
    unittest.main()
