import re
import hashlib
import hmac
import time
import datetime
import json
import os
from pathlib import Path

class JarvisSecurityBarricade:
    def __init__(self, home_dir="/content"):
        self.home = Path(home_dir)
        self.chain_path = self.home / "audit_chain.jsonl"
        self.lock_path = self.home / "lockout.json"

        # Advanced OTP and Session configuration from security core
        self.owner_user = "ahamed@2026bioasiksamop"
        self.otp_minutes = 3
        self.session_idle = 1800
        self.require_mfa = {"otp": True, "totp": True, "voice": True}
        self.dev_console_otp = False
        self.otp_salt = os.urandom(8).hex()
        self.otp_state = {}

        self.blocked_patterns = [
            r"\b(suicide|self-harm|kill myself|harm myself|end my life)\b",
            r"\b(ignore previous instructions|system prompt|bypass filter|override security)\b",
            r"\b(steal credentials|extract passwords|inject exploit|execute malicious)\b",
            r"\b(bomb-making|build a bomb|illegal drugs manufacture|illicit activities)\b",
            r"\b(deceive user|simulate banking hack|fake system error for scam)\b"
        ]

        self.sensitive_patterns = [
            r"\b(pay|transfer|transaction|send money|purchase|buy)\b",
            r"\b(delete system|format drive|erase backup|modify registry)\b"
        ]

        self.last_hash = self._last_hash()

    def _h(self, rec):
        return hashlib.sha256(json.dumps(rec, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

    def _last_hash(self):
        try:
            if self.chain_path.exists():
                return json.loads(self.chain_path.read_text(encoding="utf-8").splitlines()[-1])["h"]
        except Exception:
            pass
        return "0" * 64

    def audit(self, kind, text):
        rec = {
            "ts": datetime.datetime.now().isoformat(timespec="seconds"),
            "k": kind,
            "t": str(text)[:300],
            "p": self.last_hash
        }
        rec["h"] = self._h(rec)
        self.last_hash = rec["h"]
        with self.chain_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def issue_otp(self, purpose="owner login"):
        import secrets as _sec
        code = f"{_sec.randbelow(10 ** 8):08d}"
        self.otp_state.update({
            "h": hashlib.sha256((code + self.otp_salt).encode()).hexdigest(),
            "exp": time.time() + self.otp_minutes * 60,
            "tries": 0
        })
        if self.dev_console_otp:
            print("DEV ONLY code:", code)
        self.audit("OTP_ISSUED", f"OTP created for {purpose}")
        return code

    def check_otp(self, code):
        if not self.otp_state or time.time() > self.otp_state["exp"] or self.otp_state["tries"] >= 3:
            self.otp_state.clear()
            return False
        self.otp_state["tries"] += 1
        ok = hmac.compare_digest(
            self.otp_state["h"],
            hashlib.sha256((code.strip() + self.otp_salt).encode()).hexdigest()
        )
        if ok:
            self.otp_state.clear()
            self.audit("OTP_SUCCESS", "MFA OTP check passed")
        else:
            self.audit("OTP_FAILED", "MFA OTP check failed")
        return ok

    def evaluate_input(self, user_input):
        cleaned_input = user_input.lower().strip()
        for pattern in self.blocked_patterns:
            if re.search(pattern, cleaned_input):
                self.audit("BLOCKED", f"User input triggered safety pattern: {pattern}")
                return True, f"Safety Violation: Request matches prohibited pattern."
        return False, "Clear"

    def requires_verification(self, user_input):
        cleaned_input = user_input.lower().strip()
        return any(re.search(pat, cleaned_input) for pat in self.sensitive_patterns)

    def verify_action(self, action_description):
        print(f"\n!!! SECURITY WARNING: AUTHORIZATION REQUIRED !!!")
        print(f"Action: {action_description}")
        self.audit("VERIFICATION_REQUIRED", action_description)
        return True
