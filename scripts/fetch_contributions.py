"""Scrape the public contribution calendar (no token needed) -> data/contributions.json"""
import json, re, datetime as dt
import requests
from bs4 import BeautifulSoup
from common import ROOT, load_config

def main():
    user = load_config()["username"]
    r = requests.get(f"https://github.com/users/{user}/contributions",
                     headers={"User-Agent": "Mozilla/5.0 profile-art-bot"}, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    counts = {}
    for tip in soup.find_all("tool-tip"):
        m = re.match(r"\s*(No|\d[\d,]*)\s+contribution", tip.get_text())
        if m and tip.get("for"):
            counts[tip["for"]] = 0 if m.group(1) == "No" else int(m.group(1).replace(",", ""))
    days = [{"date": td["data-date"], "level": int(td.get("data-level", 0)), "count": counts.get(td.get("id"), 0)}
            for td in soup.select("td[data-date]")]
    if not days:
        raise SystemExit("no contribution cells found - GitHub markup may have changed")
    days.sort(key=lambda d: d["date"])

    total = sum(d["count"] for d in days)
    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] > 0 else 0
        longest = max(longest, run)
    cur = 0
    for i, d in enumerate(reversed(days)):
        if d["count"] > 0: cur += 1
        elif i == 0: continue          # today may not have contributions yet
        else: break
    best = max(days, key=lambda d: d["count"])
    months = {}
    for d in days:
        months[d["date"][:7]] = months.get(d["date"][:7], 0) + d["count"]
    out = {"username": user, "generated": dt.date.today().isoformat(), "total": total,
           "current_streak": cur, "longest_streak": longest,
           "best_day": {"date": best["date"], "count": best["count"]},
           "monthly": months, "days": days}
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data" / "contributions.json").write_text(json.dumps(out, indent=1))
    print(f"{user}: {total} contributions, {len(days)} days, streak {cur}/{longest}")

if __name__ == "__main__":
    main()
