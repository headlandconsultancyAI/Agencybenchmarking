"""Peer agency LinkedIn board.

Pulls LinkedIn company-page posts (Apify "LinkedIn Posts Scraper Pro" exports),
merges them into an accumulating history, tags topics and new media, and writes
a single self-contained HTML dashboard.

  python build_board.py --file scrape.json                 # from a file on disk
  python build_board.py --task <apify-task-id>             # last successful run of a saved task
  python build_board.py --dataset <apify-dataset-id>       # a specific dataset
  python build_board.py                                    # just rebuild from history

Standard library only.
"""
import argparse, datetime as dt, json, os, re, statistics, sys, urllib.request, urllib.error
from pathlib import Path

import topics, match

HERE = Path(__file__).parent
FIRMS = topics.CORPORATE + topics.CONSUMER
SNIPPET = 480


def pid(url):
    m = re.search(r"activity[-:](\d{15,})", url or "")
    return m.group(1) if m else (url or "")


def apify_get(path, token):
    url = f"https://api.apify.com/v2/{path}{'&' if '?' in path else '?'}token={token}&clean=true&format=json"
    try:
        with urllib.request.urlopen(url, timeout=120) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")[:300]
        hint = ""
        if e.code == 404:
            hint = ("\n  A 404 here usually means the task has never finished a run, or the ID is an actor "
                    "rather than a saved task. Run the task once in Apify, then retry.")
        if e.code == 401:
            hint = "\n  Check APIFY_TOKEN is set and current."
        sys.exit(f"Apify returned {e.code} for {path.split('?')[0]}.{hint}\n  {body}")


def load_source(args):
    if args.file:
        rows = []
        for f in args.file:
            rows += json.load(open(f, encoding="utf-8"))
        return rows
    token = os.environ.get("APIFY_TOKEN", "").strip()
    if (args.task or args.dataset) and not token:
        sys.exit("APIFY_TOKEN isn't set. In GitHub, add it under Settings, Secrets and variables, Actions.")
    if args.task:
        return apify_get(f"actor-tasks/{args.task}/runs/last/dataset/items?status=SUCCEEDED", token)
    if args.dataset:
        return apify_get(f"datasets/{args.dataset}/items", token)
    return []


def normalise(raw):
    out = {}
    for r in raw:
        if r.get("is_repost") or r.get("author_name") not in FIRMS or not r.get("content"):
            continue
        e = r.get("engagement") or {}
        k = pid(r.get("post_url"))
        out[k] = {"id": k, "firm": r["author_name"], "posted_at": r.get("posted_at") or "",
                  "text": r["content"], "url": r.get("post_url") or "",
                  "reactions": e.get("total_reactions") or 0, "comments": e.get("comments") or 0,
                  "shares": e.get("shares") or 0,
                  "seen": dt.date.today().isoformat()}
    return out


def merge(history, fresh):
    added = 0
    for k, r in fresh.items():
        if k in history:
            # engagement keeps climbing after publication, so take the newer numbers
            for f in ("reactions", "comments", "shares", "text", "seen"):
                history[k][f] = r[f]
        else:
            history[k] = r
            added += 1
    return added


def build_payload(history, curation, title):
    T = match.compile_model(topics.THEMES)
    N = match.compile_model(topics.NEW_MEDIA)
    theme_names, nm_names = list(topics.THEMES), list(topics.NEW_MEDIA)
    decisions = curation.get("decisions", {})
    reviewed = set(curation.get("reviewed_ids", []))
    posts = sorted(history.values(), key=lambda r: r["posted_at"], reverse=True)
    as_of = posts[0]["posted_at"][:10] if posts else dt.date.today().isoformat()
    cutoff = (dt.date.fromisoformat(as_of) - dt.timedelta(days=365)).isoformat()

    firm_idx = {f: i for i, f in enumerate(FIRMS)}
    medians = {}
    for f in FIRMS:
        vals = [p["reactions"] for p in posts if p["firm"] == f and p["posted_at"][:10] > cutoff]
        medians[f] = statistics.median(vals) if vals else 0

    rows, counts = [], {"subject": 0, "candidate": 0, "adjacent": 0}
    for p in posts:
        if p["posted_at"][:10] <= cutoff:
            continue
        text = p["text"]
        themes = [theme_names.index(t) for t in match.tag(text, T)]
        kw = match.tag(text, N)
        d = decisions.get(p["id"], {})
        status, nm, purpose, own = 0, [], "", False
        if d.get("status") == "subject":
            status, purpose, own = 1, d.get("purpose", ""), bool(d.get("own_research"))
            nm = [nm_names.index(t) for t in d.get("themes", []) if t in nm_names] or [nm_names.index(t) for t in kw]
            counts["subject"] += 1
        elif d.get("status") == "adjacent":
            status, nm, purpose = 3, [nm_names.index(t) for t in kw], d.get("note", "")
            counts["adjacent"] += 1
        elif d.get("status") == "excluded" or p["id"] in reviewed:
            pass
        elif kw:
            status, nm = 2, [nm_names.index(t) for t in kw]
            counts["candidate"] += 1
        cut = len(text) > SNIPPET
        snippet = text[:SNIPPET].rsplit(" ", 1)[0] + "\u2026" if cut else text
        rows.append({"id": p["id"], "f": firm_idx[p["firm"]], "d": p["posted_at"][:10],
                     "r": p["reactions"], "c": p["comments"], "s": p["shares"],
                     "t": themes, "n": status, "m": nm, "p": purpose, "o": int(own),
                     "x": snippet, "u": p["url"]})

    firms = [{"name": f, "group": "Consumer" if f in topics.CONSUMER else "Corporate",
              "median": medians[f], "home": f == topics.HOME_FIRM} for f in FIRMS]
    meta = {"title": title, "as_of": as_of,
            "built": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "firms": firms, "themes": theme_names, "nm_themes": nm_names,
            "counts": counts, "total": len(rows)}
    return {"meta": meta, "posts": rows}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", nargs="*", help="Apify JSON export(s) on disk")
    ap.add_argument("--task", help="Apify saved task ID")
    ap.add_argument("--dataset", help="Apify dataset ID")
    ap.add_argument("--history", default=str(HERE / "data" / "history.json"))
    ap.add_argument("--curation", default=str(HERE / "data" / "curation.json"))
    ap.add_argument("--max-age-days", type=int, default=400, help="drop posts older than this from history")
    ap.add_argument("--title", default="Peer agency LinkedIn board")
    ap.add_argument("--out", default=str(HERE / "out"))
    args = ap.parse_args()

    hist_path = Path(args.history)
    history = {r["id"]: r for r in json.load(open(hist_path, encoding="utf-8"))} if hist_path.exists() else {}
    fresh = normalise(load_source(args))
    added = merge(history, fresh)
    keep_after = (dt.date.today() - dt.timedelta(days=args.max_age_days)).isoformat()
    history = {k: r for k, r in history.items() if r["posted_at"][:10] >= keep_after}
    hist_path.parent.mkdir(parents=True, exist_ok=True)
    json.dump(sorted(history.values(), key=lambda r: r["posted_at"]), open(hist_path, "w", encoding="utf-8"),
              ensure_ascii=False)

    cur_path = Path(args.curation)
    curation = json.load(open(cur_path, encoding="utf-8")) if cur_path.exists() else {}
    payload = build_payload(history, curation, args.title)

    tpl = (HERE / "template.html").read_text(encoding="utf-8")
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = tpl.replace("/*__DATA__*/null", data).replace("__TITLE__", args.title)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(html, encoding="utf-8")
    (out / f"peer-board-{payload['meta']['as_of']}.html").write_text(html, encoding="utf-8")

    c = payload["meta"]["counts"]
    print(f"Pulled {len(fresh)} posts ({added} new). History holds {len(history)}.")
    print(f"Board covers {payload['meta']['total']} posts to {payload['meta']['as_of']}: "
          f"{c['subject']} new media, {c['candidate']} unreviewed, {c['adjacent']} adjacent.")
    print(f"Wrote {out / 'index.html'}")


if __name__ == "__main__":
    main()
