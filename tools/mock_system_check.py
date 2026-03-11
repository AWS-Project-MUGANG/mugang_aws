import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from uuid import uuid4


BASE_URL = "http://localhost:8000"
TIMEOUT_SEC = 10


class CheckRunner:
    def __init__(self):
        self.results = []

    def _request(self, method: str, path: str, body=None):
        url = urllib.parse.urljoin(BASE_URL, path)
        data = None
        headers = {"Content-Type": "application/json"}
        if body is not None:
            data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(url=url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
                parsed = None
                if raw:
                    try:
                        parsed = json.loads(raw)
                    except json.JSONDecodeError:
                        parsed = raw
                return resp.status, parsed
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", errors="replace")
            try:
                parsed = json.loads(raw) if raw else None
            except json.JSONDecodeError:
                parsed = raw
            return e.code, parsed
        except Exception as e:
            return None, str(e)

    def run_check(self, name: str, fn):
        try:
            ok, detail = fn()
        except Exception as e:
            ok, detail = False, f"Unhandled exception: {e}"
        self.results.append((name, ok, detail))
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {name}: {detail}")

    def summary(self):
        passed = sum(1 for _, ok, _ in self.results if ok)
        total = len(self.results)
        print("\n=== Summary ===")
        print(f"{passed}/{total} checks passed")
        return passed == total


def main():
    runner = CheckRunner()
    rag_title = f"mock-rag-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:8]}"
    session_id = f"mock-chat-{uuid4().hex[:10]}"

    def health_check():
        code, data = runner._request("GET", "/api/health")
        if code != 200:
            return False, f"expected 200, got {code}, body={data}"
        if not isinstance(data, dict) or "message" not in data:
            return False, f"unexpected body: {data}"
        return True, "health endpoint reachable"

    def rag_upload_check():
        body = {"title": rag_title, "content": "mock rag content for system check"}
        code, data = runner._request("POST", "/api/v1/admin/rag/upload", body)
        if code != 200:
            return False, f"expected 200, got {code}, body={data}"
        if not isinstance(data, dict) or "message" not in data:
            return False, f"unexpected body: {data}"
        return True, f"uploaded rag doc title={rag_title}"

    def rag_persisted_as_notice_check():
        code, data = runner._request("GET", "/api/v1/notices")
        if code != 200:
            return False, f"expected 200, got {code}, body={data}"
        notices = data.get("notices") if isinstance(data, dict) else None
        if not isinstance(notices, list):
            return False, f"unexpected notices payload: {data}"
        matched = any(isinstance(n, dict) and n.get("title") == f"[RAG] {rag_title}" for n in notices)
        if not matched:
            return False, f"uploaded rag title not found in notices ({len(notices)} items)"
        return True, "rag upload persistence verified"

    def chat_check():
        body = {"user_id": 2, "session_id": session_id, "message": "수강신청 규정 알려줘"}
        code, data = runner._request("POST", "/api/v1/chat/ask", body)
        if code != 200:
            return False, f"expected 200, got {code}, body={data}"
        if not isinstance(data, dict):
            return False, f"unexpected body: {data}"
        if "reply" not in data or "sources" not in data:
            return False, f"missing keys in response: {data}"
        return True, "chat endpoint response schema ok"

    def enrollment_schedule_null_safe_check():
        payload = {
            "schedules": [
                {
                    "day_number": 0,
                    "open_datetime": None,
                    "close_datetime": None,
                    "restriction_type": "all",
                    "is_active": False,
                },
                {
                    "day_number": 1,
                    "open_datetime": "2026-03-11T00:00:00Z",
                    "close_datetime": "2026-03-12T00:00:00Z",
                    "restriction_type": "own_grade_dept",
                    "is_active": True,
                },
            ]
        }
        code, data = runner._request("POST", "/api/v1/admin/enrollment-schedule", payload)
        if code != 200:
            return False, f"expected 200, got {code}, body={data}"
        time.sleep(0.2)
        code2, data2 = runner._request("GET", "/api/v1/admin/enrollment-schedule")
        if code2 != 200:
            return False, f"GET failed after save, got {code2}, body={data2}"
        if not isinstance(data2, dict) or "schedules" not in data2:
            return False, f"unexpected body: {data2}"
        return True, "null-safe schedule save/get ok"

    runner.run_check("health", health_check)
    runner.run_check("rag_upload", rag_upload_check)
    runner.run_check("rag_persisted", rag_persisted_as_notice_check)
    runner.run_check("chat_api", chat_check)
    runner.run_check("enrollment_schedule_null_safe", enrollment_schedule_null_safe_check)

    ok = runner.summary()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
