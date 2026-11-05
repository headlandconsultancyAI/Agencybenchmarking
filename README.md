# Peer agency LinkedIn board

A dashboard of what 34 comms firms post on their LinkedIn company pages. Two views
that matter:

- **Trending**: every post in the period, ranked by how well it did against that
  firm's usual post, with a theme panel showing what firms are talking about and
  how that's moved on the previous period.
- **New media**: only posts where the channel itself is the subject (creators,
  social platforms, podcasts, newsletters, Reddit, Substack), plus a ranking of
  which firms write about it most.

There's also a firms table and a how-it-works page. Standard library Python, one
self-contained HTML file out the other end. Same setup as the signal board.

## Files

| File | What it does |
|---|---|
| `build_board.py` | Pulls the scrape, merges it into history, writes `out/index.html`. |
| `topics.py` | The firm list and both keyword models. **Edit this to change themes or firms.** |
| `match.py` | Turns the term lists into regexes. You shouldn't need to touch it. |
| `curate.py` | Logs your new media review decisions. |
| `template.html` | The dashboard. Layout, copy and colours live here. |
| `data/history.json` | Every post seen so far. The workflow commits it after each run. |
| `data/curation.json` | Your new media decisions. Seeded with the August and October reviews. |

## Running it locally

```powershell
python build_board.py --file dataset_linkedin-posts-scraper-pro.json
```

or straight from Apify:

```powershell
$env:APIFY_TOKEN = "apify_api_xxxxxxxx"
python build_board.py --task YOUR_TASK_ID
```

Run it with no source at all to rebuild from history, for example after editing
`topics.py` or the template. Output lands in `out/index.html`, plus a dated copy.

## Reviewing new media posts

New posts that hit a new media keyword show up as **Unreviewed** (tick the box on
the New media tab to see them). They don't count in any figure until you file them.

```powershell
git pull                                   # get the latest history first
python curate.py list                      # what's waiting
python curate.py subject 7383123456789012345 --themes Reddit "Social media marketing"
python curate.py subject 7383123456789012345 --themes Podcasts --own   # cites their own research
python curate.py reject 7383123456789012345                            # not about new media
python curate.py adjacent 7383123456789012345 --note "Disinformation"
```

Each post card has a **Copy ID** button, and a LinkedIn URL works in place of the ID.
Commit `data/curation.json` and push. The next build picks it up.

## Hosting

1. New repo, push this folder. The workflow file must sit at `.github/workflows/build.yml`.
2. Settings, Secrets and variables, Actions:
   - Secret `APIFY_TOKEN`
   - Variable `APIFY_TASK_ID` (a saved task, not the actor, and it needs one successful run)
   - Variable `BOARD_TITLE` if you want a different title
3. Settings, Pages, Source: **GitHub Actions**.
4. Actions tab, Build peer board, Run workflow.

The Apify task should scrape the 34 company pages in `topics.py`, with reposts
included or not, as the build drops them either way. It runs monthly on the 1st and the
build follows on the 2nd. Set the task to about 80 posts per page: the busiest firms
(FTI, Edelman, SEC Newgate) post 55 to 65 times in a heavy month, and history removes
any overlap between runs.

Free Pages needs a public repo, which makes the URL world-readable. If that's a
problem, deploy `out/` to Cloudflare Pages behind Cloudflare Access instead.

## Things worth knowing

- The big number on each post is reactions over that firm's 12-month median, floored
  at 5. It's the fairest way to compare a page with 400 posts a year against one with 20.
- History starts at 29 July 2025. Busy pages (SEC Newgate, Edelman, FTI) are thin
  before the first scrapes, and FTI has nothing before February 2026.
- Theme tags are keyword matches, so read them as direction. If a theme looks wrong,
  the fix is a tighter term in `topics.py`.
- History drops posts older than 400 days. Change it with `--max-age-days`.
