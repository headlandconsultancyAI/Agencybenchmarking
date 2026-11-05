"""Record review decisions for the New media view.

  python curate.py list                                   # unreviewed keyword hits, newest first
  python curate.py subject <id or url> --themes Reddit "Social media marketing" [--own] [--purpose "..."]
  python curate.py reject  <id or url>                    # reviewed, not about new media
  python curate.py adjacent <id or url> --note "Disinformation"

Theme names must match topics.NEW_MEDIA exactly. Rebuild the board afterwards.
"""
import argparse, json, re, sys
from pathlib import Path
import topics, match

HERE = Path(__file__).parent
CUR = HERE / "data" / "curation.json"
HIST = HERE / "data" / "history.json"


def pid(s):
    m = re.search(r"activity[-:](\d{15,})", s)
    return m.group(1) if m else s.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["list", "subject", "reject", "adjacent"])
    ap.add_argument("post", nargs="?")
    ap.add_argument("--themes", nargs="*", default=[])
    ap.add_argument("--purpose", default="Commentary / opinion")
    ap.add_argument("--own", action="store_true", help="post cites the firm's own research")
    ap.add_argument("--note", default="")
    a = ap.parse_args()

    cur = json.load(open(CUR, encoding="utf-8"))
    dec, reviewed = cur.setdefault("decisions", {}), set(cur.get("reviewed_ids", []))

    if a.action == "list":
        N = match.compile_model(topics.NEW_MEDIA)
        hist = json.load(open(HIST, encoding="utf-8"))
        todo = [r for r in hist if r["id"] not in reviewed and r["id"] not in dec and match.tag(r["text"], N)]
        for r in sorted(todo, key=lambda r: r["posted_at"], reverse=True):
            print(f"{r['id']}  {r['posted_at'][:10]}  {r['firm'][:18]:18s}  "
                  f"[{', '.join(match.tag(r['text'], N))}]  {r['text'][:90].replace(chr(10), ' ')}")
        print(f"\n{len(todo)} unreviewed")
        return

    if not a.post:
        sys.exit("Give a post id or LinkedIn URL.")
    k = pid(a.post)
    if a.action == "subject":
        bad = [t for t in a.themes if t not in topics.NEW_MEDIA]
        if bad or not a.themes:
            sys.exit(f"--themes needs one or more of: {', '.join(topics.NEW_MEDIA)}")
        dec[k] = {"status": "subject", "themes": a.themes, "purpose": a.purpose,
                  "own_research": a.own, "reviewed_by": "manual"}
    elif a.action == "adjacent":
        dec[k] = {"status": "adjacent", "note": a.note or "Adjacent", "reviewed_by": "manual"}
    else:
        dec.pop(k, None)
    reviewed.add(k)
    cur["reviewed_ids"] = sorted(reviewed)
    json.dump(cur, open(CUR, "w", encoding="utf-8"), indent=1)
    print(f"{a.action}: {k}")


if __name__ == "__main__":
    main()
