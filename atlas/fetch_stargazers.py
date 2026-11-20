# -*- coding: utf-8 -*-
import json
import os
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "WUBING2023/PaperSpine"
OUT = os.path.join(HERE, "stargazers_raw.json")
LOG = os.path.join(HERE, "fetch_progress.txt")


def get_token():
    token = os.environ.get("ATLAS_GITHUB_TOKEN", "").strip()
    if token:
        return token
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        return token
    token_file = os.path.join(HERE, "token.txt")
    if os.path.exists(token_file):
        return open(token_file, encoding="utf-8").read().strip()
    raise RuntimeError("no ATLAS_GITHUB_TOKEN or GITHUB_TOKEN env var and no token.txt")


def log(msg):
    timestamped = f"{time.strftime('%H:%M:%S')} {msg}"
    print(timestamped, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(timestamped + "\n")

def write_json_atomic(path, value, *, indent=None):
    directory = os.path.dirname(path)
    fd, temp_path = tempfile.mkstemp(prefix=".stargazers-", suffix=".json", dir=directory)
    os.close(fd)
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(value, f, ensure_ascii=False, indent=indent)
        os.replace(temp_path, path)
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def api(url, token, retries=3, *, allow_404=False, sleeper=time.sleep):
    last_error = "unknown error"
    for attempt in range(retries):
        req = urllib.request.Request(url, headers={
            "User-Agent": "paperspine-map",
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2026-03-10",
        })
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404 and allow_404:
                return None
            try:
                response_body = e.read().decode("utf-8", errors="replace")
                response_message = json.loads(response_body).get("message", response_body)
            except Exception:
                response_message = "unable to decode GitHub error response"
            diagnostics = {
                "accepted_permissions": e.headers.get("X-Accepted-GitHub-Permissions", "not reported"),
                "rate_limit_remaining": e.headers.get("X-RateLimit-Remaining", "not reported"),
                "request_id": e.headers.get("X-GitHub-Request-Id", "not reported"),
            }
            last_error = (
                f"HTTP {e.code}: {response_message}; "
                f"accepted_permissions={diagnostics['accepted_permissions']}; "
                f"rate_limit_remaining={diagnostics['rate_limit_remaining']}; "
                f"request_id={diagnostics['request_id']}"
            )
            rate_limited = e.code == 429 or (
                e.code == 403 and diagnostics["rate_limit_remaining"] == "0"
            )
            if rate_limited:
                if attempt + 1 < retries:
                    sleeper(30 * (attempt + 1))
            elif e.code in (401, 403):
                break
            elif attempt + 1 < retries:
                sleeper(5)
        except Exception as e:
            last_error = f"{type(e).__name__}: {e}"
            if attempt + 1 < retries:
                sleeper(5)
    raise RuntimeError(f"GitHub API request failed after {retries} attempts: {last_error} ({url})")

def main():
    token = get_token()
    repo_meta = api(f"https://api.github.com/repos/{REPO}", token)
    expected_stars = int(repo_meta.get("stargazers_count", 0))
    if "stargazers_count" not in repo_meta or expected_stars < 0:
        raise ValueError("Missing repository star count")
    write_json_atomic(os.path.join(HERE, "repository.json"), {
        "stargazers_count": expected_stars,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
    })
    log(f"repository metadata loaded: expected stars={expected_stars}")

    logins = []
    page = 1
    while True:
        batch = api(
            f"https://api.github.com/repos/{REPO}/stargazers?per_page=100&page={page}",
            token,
        )
        if not isinstance(batch, list):
            raise RuntimeError(f"unexpected stargazers response on page {page}")
        if not batch:
            if page == 1 and expected_stars:
                raise RuntimeError(
                    f"stargazers endpoint returned an empty list for a repository with "
                    f"{expected_stars} stars; refusing to overwrite cached data"
                )
            break
        logins += [u["login"] for u in batch]
        log(f"stargazer page {page}: total {len(logins)}")
        if len(batch) < 100:
            break
        page += 1
    log(f"all logins fetched: {len(logins)}")

    done = {}
    if os.path.exists(OUT):
        try:
            done = {u["login"]: u for u in json.load(open(OUT, encoding="utf-8"))}
        except Exception:
            done = {}
    # Keep only fields needed for the aggregate when importing an older cache.
    done = {login: {field: entry.get(field) for field in ("login", "location", "company", "checked")}
            for login, entry in done.items()}
    logins = list(dict.fromkeys(logins))
    remaining = api("https://api.github.com/rate_limit", token)["resources"]["core"]["remaining"]
    budget = min(400, max(0, remaining - 45))
    now = int(time.time())
    missing = [login for login in logins if login not in done]
    stale = sorted((login for login in logins if login in done and
                    now - (done[login]["checked"] or 0) >= 30 * 86400),
                   key=lambda login: done[login]["checked"] or 0)
    todo = (missing + stale)[:budget]
    log(f"profiles to fetch: {len(todo)} (cached {len(done)})")

    def fetch_user(login):
        u = api(f"https://api.github.com/users/{login}", token, allow_404=True)
        if u is None:
            return {"login": login, "location": None, "company": None, "checked": now}
        return {
            "login": login,
            "location": u.get("location"),
            "company": u.get("company"),
            "checked": now,
        }

    count = len(done)
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(fetch_user, l): l for l in todo}
        for fut in as_completed(futs):
            r = fut.result()
            done[r["login"]] = r
            count += 1
            if count % 100 == 0:
                write_json_atomic(OUT, list(done.values()))
                log(f"profiles fetched: {count}/{len(logins)}")

    ordered = [done[l] for l in logins if l in done]
    if not ordered and expected_stars:
        raise RuntimeError("no stargazer profiles were fetched; refusing to overwrite cached data")
    write_json_atomic(OUT, ordered, indent=1)
    write_json_atomic(os.path.join(HERE, "coverage.json"), {"sampled": len(ordered), "listed": len(logins)})
    log(f"DONE: {len(ordered)} users saved")

if __name__ == "__main__":
    main()
