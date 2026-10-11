"""Missing Person Alert - tiny local server (Python 3.8+, no packages needed).

Serves the alert page at http://localhost:8000 (a normal browser tab, so
WhatsApp and Gmail links open without the sandbox error) and can email every
agency automatically, with the photo attached, through your Gmail account.
"""
import base64, json, os, re, smtplib, ssl
from email.message import EmailMessage
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
PORT = int(os.environ.get("PORT", "8000"))
HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
USE_SSL = os.environ.get("SMTP_SSL", "1") == "1"
USER = os.environ.get("GMAIL_USER", "")
PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "").replace(" ", "")
MAX_BODY = 15 * 1024 * 1024
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
ALLOWED_HOSTS = {"localhost:%d" % PORT, "127.0.0.1:%d" % PORT}
ALLOWED_ORIGINS = {"http://" + h for h in ALLOWED_HOSTS}


def build_message(to, subject, body, photos):
    m = EmailMessage()
    m["From"], m["To"], m["Subject"] = USER, to, subject
    m.set_content(body)
    for p in photos:
        data = base64.b64decode(p["data"])
        kind, _, sub = (p.get("type") or "image/jpeg").partition("/")
        m.add_attachment(data, maintype=kind or "image", subtype=sub or "jpeg",
                         filename=p.get("name") or "photo.jpg")
    return m


def send_all(emails, subject, body, photos):
    results = []
    if USE_SSL:
        smtp = smtplib.SMTP_SSL(HOST, SMTP_PORT, context=ssl.create_default_context(), timeout=30)
    else:
        smtp = smtplib.SMTP(HOST, SMTP_PORT, timeout=30)
    with smtp:
        if USER and PASSWORD:
            smtp.login(USER, PASSWORD)
        for to in emails:
            try:
                smtp.send_message(build_message(to, subject, body, photos))
                results.append({"to": to, "ok": True})
            except Exception as e:  # keep going if one address fails
                results.append({"to": to, "ok": False, "error": str(e)[:120]})
    return results


class Handler(BaseHTTPRequestHandler):
    def _json(self, code, obj):
        raw = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _safe(self, post=False):
        """Block other websites from talking to this local server (CSRF / DNS rebinding)."""
        if (self.headers.get("Host") or "").lower() not in ALLOWED_HOSTS:
            self._json(403, {"error": "forbidden host"})
            return False
        if post:
            origin = self.headers.get("Origin")
            if origin and origin.lower() not in ALLOWED_ORIGINS:
                self._json(403, {"error": "forbidden origin"})
                return False
            if not (self.headers.get("Content-Type") or "").lower().startswith("application/json"):
                self._json(415, {"error": "JSON only"})
                return False
        return True

    def do_GET(self):
        if not self._safe():
            return
        if self.path.split("?")[0] in ("/", "/index.html"):
            raw = (HERE / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
        elif self.path == "/api/ping":
            self._json(200, {"ok": True, "email": bool(USER and PASSWORD)})
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):
        if not self._safe(post=True):
            return
        if self.path != "/api/email":
            return self._json(404, {"error": "not found"})
        size = int(self.headers.get("Content-Length", "0"))
        if size <= 0 or size > MAX_BODY:
            return self._json(413, {"error": "request too large (max 15 MB)"})
        try:
            d = json.loads(self.rfile.read(size))
            emails = [e.strip() for e in d.get("emails", []) if EMAIL_RE.match(e.strip())]
            if not emails:
                return self._json(400, {"error": "no valid email addresses"})
            if not (USER and PASSWORD):
                return self._json(400, {"error": "GMAIL_USER / GMAIL_APP_PASSWORD not set"})
            subject = " ".join(str(d.get("subject") or "URGENT: Missing person").split())[:200]
            res = send_all(emails, subject, str(d.get("body", "")), d.get("photos", []))
            self._json(200, {"results": res})
        except (BrokenPipeError, ConnectionResetError):
            pass
        except smtplib.SMTPAuthenticationError:
            self._json(401, {"error": "Gmail login failed. Use a Gmail App Password, not your normal password."})
        except Exception as e:
            self._json(500, {"error": str(e)[:200]})

    def log_message(self, fmt, *a):
        print("[%s] %s" % (self.log_date_time_string(), fmt % a))


if __name__ == "__main__":
    # Bound to 127.0.0.1 so only this computer can use it (it holds your Gmail password).
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print("Open http://localhost:%d in Chrome/Edge/Safari" % PORT)
    print("Auto email:", "READY (%s)" % USER if USER and PASSWORD else "OFF (set GMAIL_USER and GMAIL_APP_PASSWORD)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
