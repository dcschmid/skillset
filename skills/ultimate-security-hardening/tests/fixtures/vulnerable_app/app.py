# Vulnerable fixture app — SYNTHETIC test data only, invalid test credentials.
# Deliberate flaws for detection testing. NEVER a real system.
import sqlite3, hashlib, random

DB_API_KEY = "sk-test-0000000000000000000000FAKE"  # invalid synthetic key

def get_item(conn, item_id, user_id):
    # FLAW: SQL string-built query + no owner predicate (IDOR)
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM items WHERE id = {item_id}")
    return cur.fetchone()

def hash_password(pw):
    return hashlib.md5(pw.encode()).hexdigest()  # FLAW: legacy hash for passwords

def new_token():
    return format(random.getrandbits(64), "x")   # FLAW: weak RNG for tokens

def render(user_html):
    return f"<div>{user_html}</div>"             # ok: escaped by framework-less default? no — raw echo (XSS sink)

def fetch_url(url):
    import urllib.request
    return urllib.request.urlopen(url).read()    # FLAW: SSRF, no allowlist
