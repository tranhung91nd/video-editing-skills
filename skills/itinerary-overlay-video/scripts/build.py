#!/usr/bin/env python3
"""Write <job>/hyperframes/index.html from <job>/job.json + <job>/plan/words.json.

The source footage and its voice play unchanged; this only adds graphics:
hook, title card, Vietnam route map, N-day progress bar, day cards,
"planning" question, inclusions checklist, captions and end card.
Usage: python3 build.py <job_dir>
"""
import json
import re
import sys
from html import escape
from pathlib import Path

JOB = Path(sys.argv[1]).resolve()
HF = JOB / "hyperframes"
CFG = json.loads((JOB / "job.json").read_text(encoding="utf-8"))
SK = Path(__file__).resolve().parent.parent

END = CFG["duration"]
HOOK, TITLE, PLAN, INCL, ENDC = CFG["hook"], CFG["title"], CFG["plan"], CFG["inclusions"], CFG["end_card"]
HOOK_END, TITLE_END = HOOK["end"], TITLE["end"]
PLAN_START, INCL_START, END_CARD = PLAN["start"], INCL["start"], ENDC["start"]
LEGS, STOPS = CFG["legs"], CFG["stops"]
TOTAL = CFG["total_days"]
BRAND = CFG["brand"]

# ---------- Vietnam map (mainland outline, islands, Hoang Sa, Truong Sa) ----------
OUTLINE = [(102.15, 22.4), (102.5, 22.75), (103.0, 22.6), (103.5, 22.7), (104.0, 22.8), (104.7, 22.85), (105.3, 23.3),
           (105.9, 22.95), (106.7, 22.8), (106.6, 22.3), (107.4, 21.65), (108.0, 21.5), (107.4, 21.2), (106.7, 20.7),
           (106.1, 19.9), (105.8, 19.2), (105.7, 18.7), (106.5, 18.0), (106.6, 17.4), (107.3, 16.7), (108.2, 16.1),
           (108.8, 15.4), (109.1, 14.5), (109.3, 13.4), (109.2, 12.5), (109.2, 11.7), (108.8, 11.3), (108.0, 10.7),
           (107.2, 10.4), (106.8, 10.4), (106.6, 9.6), (105.8, 8.8), (105.0, 8.6), (104.8, 9.3), (104.9, 10.0),
           (104.5, 10.4), (105.1, 10.9), (105.9, 11.0), (106.4, 11.7), (107.5, 12.3), (107.6, 13.5), (107.4, 14.5),
           (107.6, 15.4), (107.2, 16.0), (106.6, 16.5), (106.0, 17.3), (105.6, 17.9), (104.9, 18.3), (104.0, 19.2),
           (104.6, 19.7), (104.0, 20.0), (103.0, 20.7), (102.2, 21.4)]
# Phu Quoc, Con Dao, Cat Ba, Bach Long Vi, Ly Son, Phu Quy
ISLANDS = [(103.96, 10.23, 4, 7), (106.6, 8.69, 2.5, 2.5), (107.05, 20.8, 3, 2.5), (107.72, 20.13, 2, 2),
           (109.12, 15.38, 2, 2), (108.94, 10.52, 2, 2)]
HOANG_SA = [(111.61, 16.53), (112.34, 16.83), (112.73, 16.67), (111.78, 16.05), (111.2, 15.78), (112.26, 16.98)]
TRUONG_SA = [(114.33, 11.43), (114.28, 11.05), (114.42, 10.68), (114.36, 10.38), (114.36, 10.18), (114.33, 9.88),
             (113.7, 8.97), (112.2, 8.85), (111.92, 8.64), (112.91, 7.89)]
MAP_W, MAP_H, PAD = 349, 450, 14
LON0, LON1, LAT0, LAT1 = 102.1, 114.8, 7.6, 23.4

ICON = {
    "boat": '<path d="M3 15l2 5h14l2-5zM12 3v10M12 4l6 8h-6M12 6l-5 6h5"/>',
    "car": '<path d="M4 16v-4l2-5h12l2 5v4zM4 16v2M20 16v2"/><circle cx="7.5" cy="13.5" r="1"/><circle cx="16.5" cy="13.5" r="1"/>',
    "train": '<rect x="6" y="3" width="12" height="13" rx="3"/><path d="M6 10h12M9 20l-2 2M15 20l2 2M9 16l-1 4M15 16l1 4"/>',
    "plane": '<path d="M2 13l8-2 4-8h2l-1 8 6 1 1-2h1v6h-1l-1-2-6 1 1 8h-2l-4-8-8-2z"/>',
}
WA = ('<svg viewBox="0 0 24 24"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.2'
      'l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.6.8-.8 1-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9'
      'c-.2-.4.2-.4.7-1.3a.4.4 0 0 0 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.8'
      'c.1.2 1.9 2.9 4.6 4 1.7.7 2.4.8 3.2.7a2.8 2.8 0 0 0 1.8-1.3 2.3 2.3 0 0 0 .2-1.3c-.1-.1-.3-.2-.5-.3z"/></svg>')
TICK = '<svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'


def r(x):
    return round(x, 3)


def proj(lon, lat):
    x = PAD + (lon - LON0) / (LON1 - LON0) * (MAP_W - 2 * PAD)
    y = PAD + (LAT1 - lat) / (LAT1 - LAT0) * (MAP_H - 2 * PAD)
    return round(x, 1), round(y, 1)


def mark(text):
    """Escape, then turn [words] into a yellow highlight."""
    return re.sub(r"\[(.+?)\]", r'<span class="y">\1</span>', escape(text))


def norm(s):
    return "".join(ch for ch in s.lower() if ch.isalnum())


def load_words():
    fixes = CFG.get("word_fixes", {})
    out = []
    for w in json.loads((JOB / "plan/words.json").read_text()):
        t = fixes.get(w["w"], w["w"])
        if t.startswith("-") and out:          # Whisper splits "first-timers" into "first" + "-timers"
            out[-1]["w"] += t
            out[-1]["e"] = w["e"]
        else:
            out.append({"w": t, "s": w["s"], "e": w["e"]})
    return out


html, js = [], []

# footage (muted) + its own sound on a separate track
html.append(f'<video id="footage" class="clip shot" src="assets/footage.mp4" muted playsinline '
            f'data-start="0" data-duration="{END}" data-track-index="0"></video>')
html.append(f'<audio id="vo" src="assets/audio.wav" data-start="0" data-duration="{END}" data-track-index="1" data-volume="1"></audio>')
html.append(f'<div id="shade" class="clip overlay" data-start="0" data-duration="{END_CARD}" data-track-index="2">'
            '<div class="top-shade" id="topshade"></div><div class="bot-shade"></div></div>')
js.append(f'tl.fromTo("#topshade", {{opacity: 0.55}}, {{opacity: 1, duration: 0.4, ease: "none"}}, {r(max(0, TITLE_END - 9.2))});')

# ---------- hook ----------
subs = HOOK.get("subs", [])
sub_html = "".join(f'<div class="h-sub{" alt" if s.get("alt") else ""}" id="hs{k}">{mark(s["text"])}</div>' for k, s in enumerate(subs))
html.append(
    f'<div id="hook" class="clip overlay" data-start="0" data-duration="{HOOK_END}" data-track-index="3"><div class="mid-shade"></div><div class="hook">'
    f'<div class="h-kicker soft" id="hk">{mark(HOOK["kicker"])}</div>'
    f'<div class="h-big soft" id="hb1">{mark(HOOK["big"])}</div>{sub_html}</div></div>')
js += [
    'tl.fromTo("#hk", {opacity: 0, y: 20}, {opacity: 1, y: 0, duration: 0.4, ease: "power3.out"}, 0.1);',
    f'tl.fromTo("#hb1", {{opacity: 0, y: 30}}, {{opacity: 1, y: 0, duration: 0.45, ease: "power3.out"}}, {HOOK.get("big_at", 0.9)});',
]
for k, s in enumerate(subs):
    js.append(f'tl.fromTo("#hs{k}", {{opacity: 0, y: 20}}, {{opacity: 1, y: 0, duration: 0.4, ease: "power3.out"}}, {s["at"]});')
    if k + 1 < len(subs):
        js.append(f'tl.to("#hs{k}", {{opacity: 0, y: -10, duration: 0.25, ease: "power2.in"}}, {r(subs[k + 1]["at"] - 0.3)});')
js.append(f'tl.to("#hook .hook", {{opacity: 0, duration: 0.3, ease: "none"}}, {r(HOOK_END - 0.3)});')

# ---------- title card ----------
route_txt = " &#8594; ".join(escape(x) for x in TITLE["route"])
html.append(
    f'<div id="title" class="clip overlay" data-start="{HOOK_END}" data-duration="{r(TITLE_END - HOOK_END)}" data-track-index="4">'
    f'<div class="mid-shade"></div><div class="title"><div class="t-logo" id="tlogo"><img src="assets/logo-white.png" alt="{escape(BRAND["name"])}"/></div>'
    f'<div class="t-num soft" id="tnum">{mark(TITLE["big"])}</div><div class="t-in soft" id="tin">{mark(TITLE["line2"])}</div>'
    f'<div class="t-sub soft" id="tsub">{mark(TITLE["sub"])}</div>'
    f'<div class="t-route" id="troute">{route_txt}</div></div></div>')
H = HOOK_END
js += [
    f'tl.fromTo("#tlogo", {{opacity: 0, y: -16}}, {{opacity: 1, y: 0, duration: 0.5, ease: "power3.out"}}, {r(H + 0.1)});',
    f'tl.fromTo("#tnum", {{opacity: 0, scale: 0.8}}, {{opacity: 1, scale: 1, duration: 0.55, ease: "back.out(1.6)"}}, {r(H + 1.9)});',
    f'tl.fromTo("#tin", {{opacity: 0, y: 20}}, {{opacity: 1, y: 0, duration: 0.4, ease: "power3.out"}}, {r(H + 2.3)});',
    f'tl.fromTo("#tsub", {{opacity: 0, y: 20}}, {{opacity: 1, y: 0, duration: 0.4, ease: "power3.out"}}, {r(H + 3.0)});',
    f'tl.fromTo("#troute", {{opacity: 0, y: 20}}, {{opacity: 1, y: 0, duration: 0.45, ease: "power3.out"}}, {r(H + 4.0)});',
    f'tl.to("#title .title", {{opacity: 0, duration: 0.3, ease: "none"}}, {r(TITLE_END - 0.3)});',
]

# ---------- route map ----------
MAP_START = H + 4.0
outline = "M" + " L".join(f"{x},{y}" for x, y in (proj(*p) for p in OUTLINE)) + " Z"
pts = [proj(s["lon"], s["lat"]) for s in STOPS]
route = [leg["stop"] for leg in LEGS]
segs = []
for i in range(1, len(route)):
    (x1, y1), (x2, y2) = pts[route[i - 1]], pts[route[i]]
    if (x1, y1) == (x2, y2):
        continue
    a_, b_ = STOPS[route[i - 1]], STOPS[route[i]]
    bend = LEGS[i].get("bend", 18 if b_["lat"] >= a_["lat"] - 0.2 else -24)   # px sideways; + bows east
    segs.append((i, f"M{x1},{y1} Q{r((x1 + x2) / 2 + bend)},{r((y1 + y2) / 2)} {x2},{y2}"))
svg = [f'<svg class="map-svg" viewBox="0 0 {MAP_W} {MAP_H}" width="{MAP_W}" height="{MAP_H}">', f'<path d="{outline}" class="land"/>']
for lon, lat, rx, ry in ISLANDS:
    x, y = proj(lon, lat)
    svg.append(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" class="isle"/>')
for lon, lat in HOANG_SA + TRUONG_SA:
    x, y = proj(lon, lat)
    svg.append(f'<circle cx="{x}" cy="{y}" r="2.8" class="isle"/>')
for i, d in segs:
    svg.append(f'<path d="{d}" class="route-ghost"/><path id="seg{i}" d="{d}" class="route" pathLength="1"/>')
for k, (s, (x, y)) in enumerate(zip(STOPS, pts)):
    side = s.get("side", "r")
    tx = x - 14 if side == "l" else (x - 6 if side == "bl" else x + 14)
    anchor = "start" if side == "r" else "end"
    svg.append(f'<circle cx="{x}" cy="{y}" r="7" class="dot"/><circle id="dot{k}" cx="{x}" cy="{y}" r="9" class="dot-on"/>'
               f'<text id="lab{k}" x="{tx}" y="{y + (30 if side == "bl" else 7)}" text-anchor="{anchor}" class="lab">{escape(s["name"])}</text>')
svg.append("</svg>")
html.append(f'<div id="map" class="clip overlay" data-start="{r(MAP_START)}" data-duration="{r(PLAN_START - MAP_START)}" data-track-index="5">'
            f'<div class="map" id="mapbox">{"".join(svg)}</div></div>')
js += [
    f'tl.fromTo("#mapbox", {{opacity: 0, x: 30}}, {{opacity: 1, x: 0, duration: 0.5, ease: "power3.out"}}, {r(MAP_START)});',
    'tl.set(".route", {strokeDashoffset: 1}, 0);',
    'tl.set(".dot-on", {scale: 0, transformOrigin: "50% 50%"}, 0);',
    'tl.set(".lab", {opacity: 0.55}, 0);',
]
for n, (i, _) in enumerate(segs):           # preview: the whole route draws once on the title card
    js.append(f'tl.to("#seg{i}", {{strokeDashoffset: 0, duration: 0.45, ease: "none"}}, {r(MAP_START + 0.4 + n * 0.45)});')
js.append(f'tl.to(".route", {{strokeDashoffset: 1, duration: 0.3, ease: "none"}}, {r(TITLE_END - 0.6)});')
seg_ids = {i for i, _ in segs}
for li, leg in enumerate(LEGS):
    a = leg["start"]
    if li in seg_ids:
        js.append(f'tl.to("#seg{li}", {{strokeDashoffset: 0, duration: 0.7, ease: "power2.inOut"}}, {a});')
    js.append(f'tl.to("#dot{leg["stop"]}", {{scale: 1, duration: 0.35, ease: "back.out(2.5)"}}, {r(a + 0.5)});')
    js.append(f'tl.to(".lab", {{opacity: 0.55, fill: "#ffffff", duration: 0.2}}, {r(a + 0.3)});')
    js.append(f'tl.to("#lab{leg["stop"]}", {{opacity: 1, fill: "#fec529", duration: 0.25}}, {r(a + 0.5)});')
js.append(f'tl.to("#mapbox", {{opacity: 0, duration: 0.3, ease: "none"}}, {r(PLAN_START - 0.3)});')

# ---------- progress bar ----------
cells = "".join(f'<div class="cell"><div class="fill" id="f{d}"></div></div>' for d in range(1, TOTAL + 1))
html.append(f'<div id="prog" class="clip overlay" data-start="{r(TITLE_END - 0.3)}" data-duration="{r(PLAN_START - TITLE_END + 0.3)}" data-track-index="6">'
            f'<div class="prog" id="progbox"><div class="prog-lab soft">{escape(CFG.get("progress_label", f"YOUR {TOTAL} DAYS"))}</div>'
            f'<div class="cells">{cells}</div></div></div>')
js += [f'tl.fromTo("#progbox", {{opacity: 0, y: -14}}, {{opacity: 1, y: 0, duration: 0.4, ease: "power3.out"}}, {r(TITLE_END - 0.3)});',
       'tl.set(".fill", {scaleX: 0, transformOrigin: "0% 50%"}, 0);']
done = 0
for leg in LEGS:
    for d in range(done + 1, leg["last_day"] + 1):
        js.append(f'tl.to("#f{d}", {{scaleX: 1, duration: 0.3, ease: "power2.out"}}, {r(leg["start"] + 0.2 + (d - done - 1) * 0.12)});')
    done = leg["last_day"]
js.append(f'tl.to("#progbox", {{opacity: 0, duration: 0.3, ease: "none"}}, {r(PLAN_START - 0.3)});')

# ---------- day cards ----------
for i, leg in enumerate(LEGS):
    a, b = leg["start"], leg["end"]
    tr = leg.get("transport")
    tr_html = (f'<div class="d-trans"><svg viewBox="0 0 24 24" class="ico">{ICON[tr[0]]}</svg><span>{escape(tr[1])}</span></div>' if tr else "")
    rows = "".join(f'<div class="d-act soft" id="da{i}_{k}"><span class="bul"></span>{escape(t)}</div>' for k, t in enumerate(leg["activities"]))
    html.append(f'<div id="day{i}" class="clip overlay" data-start="{a}" data-duration="{r(b - a)}" data-track-index="7">'
                f'<div class="dcard" id="dc{i}">{tr_html}<div class="d-pill">{escape(leg["day"])}</div>'
                f'<div class="d-place soft">{escape(leg["place"])}</div><div class="d-acts">{rows}</div></div></div>')
    js.append(f'tl.fromTo("#dc{i}", {{opacity: 0, x: -40}}, {{opacity: 1, x: 0, duration: 0.4, ease: "power3.out"}}, {r(a + 0.05)});')
    for k in range(len(leg["activities"])):
        js.append(f'tl.fromTo("#da{i}_{k}", {{opacity: 0, y: 14}}, {{opacity: 1, y: 0, duration: 0.3, ease: "power2.out"}}, {r(a + 0.6 + k * 0.35)});')
    js.append(f'tl.to("#dc{i}", {{opacity: 0, x: -20, duration: 0.25, ease: "power2.in"}}, {r(b - 0.25)});')

# ---------- planning question + inclusions ----------
rows = "".join(f'<div class="i-row" id="ir{k}"><span class="tick">{TICK}</span>{escape(t)}</div>' for k, (_, t) in enumerate(INCL["items"]))
html.append(f'<div id="plan" class="clip overlay" data-start="{PLAN_START}" data-duration="{r(END_CARD - PLAN_START)}" data-track-index="8">'
            f'<div class="mid-shade" id="pshade"></div><div class="plan" id="planq"><div class="p-q soft">{mark(PLAN["question"])}</div></div>'
            f'<div class="incl" id="incl"><div class="i-head">{escape(INCL["head"])}</div>{rows}</div></div>')
js += [
    f'tl.fromTo("#planq", {{opacity: 0, y: 24}}, {{opacity: 1, y: 0, duration: 0.45, ease: "power3.out"}}, {r(PLAN_START + 0.4)});',
    f'tl.to("#pshade", {{opacity: 0, duration: 0.3}}, {r(INCL_START - 0.4)});',
    f'tl.to("#planq", {{opacity: 0, y: -16, duration: 0.3, ease: "power2.in"}}, {r(INCL_START - 0.4)});',
    f'tl.fromTo("#incl", {{opacity: 0, y: 30}}, {{opacity: 1, y: 0, duration: 0.45, ease: "power3.out"}}, {INCL_START});',
    f'tl.to("#incl", {{opacity: 0, duration: 0.3, ease: "none"}}, {r(END_CARD - 0.3)});',
]
for k, (t, _) in enumerate(INCL["items"]):
    js.append(f'tl.fromTo("#ir{k}", {{opacity: 0.25}}, {{opacity: 1, duration: 0.3, ease: "power2.out"}}, {t});')
    js.append(f'tl.fromTo("#ir{k} .tick", {{scale: 0}}, {{scale: 1, duration: 0.35, ease: "back.out(2.2)"}}, {t});')

# ---------- captions: whole clauses, hidden when the frame already says it ----------
words = load_words()
wi, timed = 0, []
for text, show in CFG["captions"]["clauses"]:
    target, acc, j = norm(text), "", wi
    while len(acc) < len(target) and j < len(words):
        acc += norm(words[j]["w"])
        j += 1
    if acc != target:
        sys.exit(f"Clause does not match the transcript:\n  job.json: {text}\n  words:    {' '.join(w['w'] for w in words[wi:j])}")
    timed.append((text, show, words[wi]["s"], words[j - 1]["e"]))
    wi = j
if wi != len(words):
    sys.exit(f"{len(words) - wi} transcript words are not covered by captions.clauses (starting: {words[wi]['w']!r})")
shown = [c for c in timed if c[1]]
keys = CFG["captions"].get("highlight", [])
for gi, (text, _, a, e) in enumerate(shown):
    b = e + 0.35
    if gi + 1 < len(shown):
        b = min(b, shown[gi + 1][2] - 0.02)
    t = escape(text)
    for k in keys:                           # first match only; names never break across lines
        if k in t:
            t = t.replace(k, '<span class="y">' + k.replace(" ", "&nbsp;") + "</span>", 1)
            break
    html.append(f'<div id="cap{gi}" class="clip overlay" data-start="{r(a)}" data-duration="{r(b - a)}" data-track-index="9">'
                f'<div class="cap soft" id="cp{gi}">{t}</div></div>')
    js.append(f'tl.fromTo("#cp{gi}", {{opacity: 0, y: 12}}, {{opacity: 1, y: 0, duration: 0.2, ease: "power2.out"}}, {r(a)});')

# ---------- end card ----------
wa_html = f'<div class="end-wa" id="ewa">{WA}<span>{escape(BRAND["whatsapp"])}</span></div>' if BRAND.get("whatsapp") else ""
html.append(f'<div id="endcard" class="clip overlay" data-start="{END_CARD}" data-duration="{r(END - END_CARD)}" data-track-index="10">'
            '<div class="end-shade" id="eshade"></div><div class="end-inner">'
            f'<div class="end-logo" id="elogo"><img src="assets/logo-white.png" alt="{escape(BRAND["name"])}"/></div>'
            f'<div class="end-title" id="etitle">{mark(ENDC["title"])}</div>'
            f'<div class="end-web" id="eweb">{escape(BRAND["website"])}</div>{wa_html}'
            f'<div class="end-link" id="elink">{escape(ENDC.get("link_hint", "Link below"))} <span class="arrow">&#8595;</span></div></div></div>')
E = END_CARD
js += [
    f'tl.fromTo("#eshade", {{opacity: 0}}, {{opacity: 1, duration: 0.45, ease: "none"}}, {E});',
    f'tl.fromTo("#elogo", {{opacity: 0, scale: 0.9}}, {{opacity: 1, scale: 1, duration: 0.5, ease: "back.out(1.5)"}}, {r(E + 0.15)});',
    f'tl.fromTo("#elink", {{opacity: 0, y: -10}}, {{opacity: 1, y: 0, duration: 0.4, ease: "power3.out"}}, {r(E + 0.6)});',
    f'tl.fromTo("#elink .arrow", {{y: 0}}, {{y: 12, duration: 0.5, ease: "sine.inOut", repeat: 7, yoyo: true}}, {r(E + 1.0)});',
    f'tl.fromTo("#etitle", {{opacity: 0, y: 20}}, {{opacity: 1, y: 0, duration: 0.45, ease: "power3.out"}}, {r(E + 1.3)});',
    f'tl.fromTo("#eweb", {{opacity: 0, y: 20}}, {{opacity: 1, y: 0, duration: 0.45, ease: "power3.out"}}, {r(E + 1.8)});',
]
if wa_html:
    js.append(f'tl.fromTo("#ewa", {{opacity: 0, scale: 0.85}}, {{opacity: 1, scale: 1, duration: 0.45, ease: "back.out(1.7)"}}, {r(E + 2.3)});')

page = (SK / "assets/hyperframes/template.tpl").read_text(encoding="utf-8")
page = page.replace("%END%", str(END)).replace("%BODY%", "\n      ".join(html)).replace("%JS%", "\n      ".join(js))
(HF / "index.html").write_text(page, encoding="utf-8")
print(f"{len(LEGS)} legs, {len(shown)} of {len(timed)} clauses captioned -> {HF / 'index.html'}")
