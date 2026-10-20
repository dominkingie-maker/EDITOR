"""Shuffled shortlist of visuals for an episode, so choices don't drift to the same favourites.

Reads references/visual-ideas.md (the ideas bank, where `[T: name]` marks a ready-made
template) and optionally stickfigure_history.json, then prints a random selection of
templates and custom ideas for the requested themes, skipping templates used recently.

  python3 suggest.py --themes "fear, time"            # shortlist for those themes
  python3 suggest.py --themes all --n 15
  python3 suggest.py --themes focus --history out/stickfigure_history.json --recent 3
  python3 suggest.py --list-themes
"""
import argparse, json, os, random, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.join(HERE, "..", "references", "visual-ideas.md")
SKIP_SECTIONS = ("contents", "shot & motion", "already used")
BOLD = re.compile(r"^- \*\*(.+?)\*\*(?: `\[T: (\w+)\]`)? — (.+?) · \*(.+?)\*(?: · (.+))?$")
INLINE = re.compile(r"([^·`]+?) `\[T: (\w+)\]`")


def load_bank(path=BANK):
    entries, section = [], None
    for line in open(path, encoding="utf-8"):
        line = line.rstrip()
        if line.startswith("## "):
            section = line[3:].strip()
            continue
        if not section or any(s in section.lower() for s in SKIP_SECTIONS) or not line.startswith("- "):
            continue
        m = BOLD.match(line)
        if m:
            name, tpl, desc, motion, theme = m.groups()
            entries.append(dict(name=name, template=tpl, desc=desc, motion=motion,
                                theme=(theme or section).strip()))
            continue
        for desc, tpl in INLINE.findall(line[2:]):
            entries.append(dict(name=desc.strip(" ·"), template=tpl, desc=desc.strip(" ·"), motion="",
                                theme=section))
    return entries


def recent_templates(history, recent):
    try:
        hist = json.load(open(history))
    except (OSError, ValueError, TypeError):
        return set()
    used = set()
    for ep in hist[-recent:]:
        for sc in ep.get("scenes", []):
            used.add(sc.get("template", ""))
    return used


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--themes", default="all", help='comma-separated words matched against theme names, or "all"')
    ap.add_argument("--n", type=int, default=12, help="how many suggestions")
    ap.add_argument("--history", help="path to stickfigure_history.json")
    ap.add_argument("--recent", type=int, default=3, help="skip templates used in this many recent episodes")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--list-themes", action="store_true")
    a = ap.parse_args()
    bank = load_bank()
    themes = sorted({e["theme"] for e in bank})
    if a.list_themes:
        print("\n".join(themes)); return
    rng = random.Random(a.seed)
    wanted = [w.strip().lower() for w in a.themes.split(",") if w.strip()]
    if "all" in wanted:
        pool = bank
    else:
        pool = [e for e in bank if any(w in e["theme"].lower() for w in wanted)]
        if not pool:
            sys.exit(f"No theme matches {wanted}. Themes: {', '.join(themes)}")
    used = recent_templates(a.history, a.recent) if a.history else set()
    skipped = sorted({e["template"] for e in pool if e["template"] in used})
    pool = [e for e in pool if e["template"] not in used]
    seen, uniq = set(), []
    for e in pool:  # a template can appear under several themes; keep one copy
        k = e["template"] or e["name"]
        if k not in seen:
            seen.add(k); uniq.append(e)
    rng.shuffle(uniq)
    customs = [e for e in uniq if not e["template"]]
    templates = [e for e in uniq if e["template"]]
    n_custom = max(1, round(a.n * 0.6))   # bias toward custom scenes: they make episodes original
    pick = customs[:n_custom] + templates[:a.n - n_custom]
    rng.shuffle(pick)
    others = [e for e in bank if e not in pool and not e["template"]]
    rng.shuffle(others)
    print(f"Shortlist ({len(pick)} of {len(uniq)} options; themes: {a.themes})")
    for e in pick:
        kind = f"TEMPLATE {e['template']}" if e["template"] else "CUSTOM"
        motion = f" · {e['motion']}" if e["motion"] else ""
        print(f"- [{kind}] {e['name']} — {e['desc']}{motion}  ({e['theme']})")
    if others and "all" not in wanted:
        print("\nWildcards from other themes (for a surprising angle):")
        for e in others[:3]:
            print(f"- [CUSTOM] {e['name']} — {e['desc']}  ({e['theme']})")
    if skipped:
        print(f"\nSkipped (used in the last {a.recent} episodes): {', '.join(skipped)}")


if __name__ == "__main__":
    main()
