#!/usr/bin/env python3
"""
World Cup 2026 -> .ics generator (re-runnable as the bracket fills in).

HOW IT WORKS
------------
- The full 104-match schedule (dates, ET kickoff times, venues, match numbers)
  is baked in below and never changes.
- Group-stage teams (M1-M72) are fixed and already named.
- Every knockout slot (M73-M104) is a TOKEN, e.g. "W_A" (winner of Group A),
  "RU_B" (runner-up B), "T3_74" (best-3rd feeding match 74), "W_M73" (winner of
  match 73), "L_M101" (loser of match 101).
- results.json maps those tokens to real team names. Anything still blank ("")
  stays as a human-readable placeholder in the calendar.
- UIDs are stable (wc2026-m{N}). Re-importing the regenerated .ics UPDATES the
  existing events in place instead of creating duplicates.

USAGE
-----
    python generate_wc_ics.py                 # uses ./results.json
    python generate_wc_ics.py path/to.json    # custom input

Fill in results.json round by round (group winners/runners/thirds first, then
match winners as each round completes), re-run, then push to GitHub Pages
(subscribed calendar) or re-import the file. One command per update.
"""

import json
import sys
import datetime

OUT_PATH = "World_Cup_2026.ics"

# ---- Group stage: fixed, fully named (date, ET 24h time, "Group: A vs B", venue) ----
GROUP = [
 ("2026-06-11","15:00","A: Mexico vs South Africa","Estadio Azteca, Mexico City"),
 ("2026-06-11","22:00","A: South Korea vs Czechia","Estadio Akron, Zapopan"),
 ("2026-06-12","15:00","B: Canada vs Bosnia & Herzegovina","BMO Field, Toronto"),
 ("2026-06-12","21:00","D: USA vs Paraguay","SoFi Stadium, Inglewood"),
 ("2026-06-13","15:00","B: Qatar vs Switzerland","Levi's Stadium, Santa Clara"),
 ("2026-06-13","18:00","C: Brazil vs Morocco","MetLife Stadium, East Rutherford"),
 ("2026-06-13","21:00","C: Haiti vs Scotland","Gillette Stadium, Foxborough"),
 ("2026-06-14","00:00","D: Australia vs Turkiye","BC Place, Vancouver"),
 ("2026-06-14","13:00","E: Germany vs Curacao","NRG Stadium, Houston"),
 ("2026-06-14","16:00","F: Netherlands vs Japan","AT&T Stadium, Arlington"),
 ("2026-06-14","19:00","E: Ivory Coast vs Ecuador","Lincoln Financial Field, Philadelphia"),
 ("2026-06-14","22:00","F: Sweden vs Tunisia","Estadio BBVA, Monterrey"),
 ("2026-06-15","12:00","H: Spain vs Cape Verde","Mercedes-Benz Stadium, Atlanta"),
 ("2026-06-15","15:00","G: Belgium vs Egypt","Lumen Field, Seattle"),
 ("2026-06-15","18:00","H: Saudi Arabia vs Uruguay","Hard Rock Stadium, Miami Gardens"),
 ("2026-06-15","21:00","G: Iran vs New Zealand","SoFi Stadium, Inglewood"),
 ("2026-06-16","15:00","I: France vs Senegal","MetLife Stadium, East Rutherford"),
 ("2026-06-16","18:00","I: Iraq vs Norway","Gillette Stadium, Foxborough"),
 ("2026-06-16","21:00","J: Argentina vs Algeria","Arrowhead Stadium, Kansas City"),
 ("2026-06-17","00:00","J: Austria vs Jordan","Levi's Stadium, Santa Clara"),
 ("2026-06-17","13:00","K: Portugal vs DR Congo","NRG Stadium, Houston"),
 ("2026-06-17","16:00","L: England vs Croatia","AT&T Stadium, Arlington"),
 ("2026-06-17","19:00","L: Ghana vs Panama","BMO Field, Toronto"),
 ("2026-06-17","22:00","K: Uzbekistan vs Colombia","Estadio Azteca, Mexico City"),
 ("2026-06-18","12:00","A: Czechia vs South Africa","Mercedes-Benz Stadium, Atlanta"),
 ("2026-06-18","15:00","B: Switzerland vs Bosnia & Herzegovina","SoFi Stadium, Inglewood"),
 ("2026-06-18","18:00","B: Canada vs Qatar","BC Place, Vancouver"),
 ("2026-06-18","21:00","A: Mexico vs South Korea","Estadio Akron, Zapopan"),
 ("2026-06-19","15:00","D: USA vs Australia","Lumen Field, Seattle"),
 ("2026-06-19","18:00","C: Scotland vs Morocco","Gillette Stadium, Foxborough"),
 ("2026-06-19","20:30","C: Brazil vs Haiti","Lincoln Financial Field, Philadelphia"),
 ("2026-06-19","23:00","D: Turkiye vs Paraguay","Levi's Stadium, Santa Clara"),
 ("2026-06-20","13:00","F: Netherlands vs Sweden","NRG Stadium, Houston"),
 ("2026-06-20","16:00","E: Germany vs Ivory Coast","BMO Field, Toronto"),
 ("2026-06-20","20:00","E: Ecuador vs Curacao","Arrowhead Stadium, Kansas City"),
 ("2026-06-21","00:00","F: Tunisia vs Japan","Estadio BBVA, Monterrey"),
 ("2026-06-21","12:00","H: Spain vs Saudi Arabia","Mercedes-Benz Stadium, Atlanta"),
 ("2026-06-21","15:00","G: Belgium vs Iran","SoFi Stadium, Inglewood"),
 ("2026-06-21","18:00","H: Uruguay vs Cape Verde","Hard Rock Stadium, Miami Gardens"),
 ("2026-06-21","21:00","G: New Zealand vs Egypt","BC Place, Vancouver"),
 ("2026-06-22","13:00","J: Argentina vs Austria","AT&T Stadium, Arlington"),
 ("2026-06-22","17:00","I: France vs Iraq","Lincoln Financial Field, Philadelphia"),
 ("2026-06-22","20:00","I: Norway vs Senegal","MetLife Stadium, East Rutherford"),
 ("2026-06-22","23:00","J: Jordan vs Algeria","Levi's Stadium, Santa Clara"),
 ("2026-06-23","13:00","K: Portugal vs Uzbekistan","NRG Stadium, Houston"),
 ("2026-06-23","16:00","L: England vs Ghana","Gillette Stadium, Foxborough"),
 ("2026-06-23","19:00","L: Panama vs Croatia","BMO Field, Toronto"),
 ("2026-06-23","22:00","K: Colombia vs DR Congo","Estadio Akron, Zapopan"),
 ("2026-06-24","15:00","B: Switzerland vs Canada","BC Place, Vancouver"),
 ("2026-06-24","15:00","B: Bosnia & Herzegovina vs Qatar","Lumen Field, Seattle"),
 ("2026-06-24","18:00","C: Scotland vs Brazil","Hard Rock Stadium, Miami Gardens"),
 ("2026-06-24","18:00","C: Morocco vs Haiti","Mercedes-Benz Stadium, Atlanta"),
 ("2026-06-24","21:00","A: Czechia vs Mexico","Estadio Azteca, Mexico City"),
 ("2026-06-24","21:00","A: South Africa vs South Korea","Estadio BBVA, Monterrey"),
 ("2026-06-25","16:00","E: Curacao vs Ivory Coast","Lincoln Financial Field, Philadelphia"),
 ("2026-06-25","16:00","E: Ecuador vs Germany","MetLife Stadium, East Rutherford"),
 ("2026-06-25","19:00","F: Japan vs Sweden","AT&T Stadium, Arlington"),
 ("2026-06-25","19:00","F: Tunisia vs Netherlands","Arrowhead Stadium, Kansas City"),
 ("2026-06-25","22:00","D: Turkiye vs USA","SoFi Stadium, Inglewood"),
 ("2026-06-25","22:00","D: Paraguay vs Australia","Levi's Stadium, Santa Clara"),
 ("2026-06-26","15:00","I: Norway vs France","Gillette Stadium, Foxborough"),
 ("2026-06-26","15:00","I: Senegal vs Iraq","BMO Field, Toronto"),
 ("2026-06-26","20:00","H: Cape Verde vs Saudi Arabia","NRG Stadium, Houston"),
 ("2026-06-26","20:00","H: Uruguay vs Spain","Estadio Akron, Zapopan"),
 ("2026-06-26","23:00","G: Egypt vs Iran","Lumen Field, Seattle"),
 ("2026-06-26","23:00","G: New Zealand vs Belgium","BC Place, Vancouver"),
 ("2026-06-27","17:00","L: Panama vs England","MetLife Stadium, East Rutherford"),
 ("2026-06-27","17:00","L: Croatia vs Ghana","Lincoln Financial Field, Philadelphia"),
 ("2026-06-27","19:30","K: Colombia vs Portugal","Hard Rock Stadium, Miami Gardens"),
 ("2026-06-27","19:30","K: DR Congo vs Uzbekistan","Mercedes-Benz Stadium, Atlanta"),
 ("2026-06-27","22:00","J: Algeria vs Austria","Arrowhead Stadium, Kansas City"),
 ("2026-06-27","22:00","J: Jordan vs Argentina","AT&T Stadium, Arlington"),
]

# ---- Knockouts: (date, time, match#, stage, home_token, home_label, away_token, away_label, venue) ----
KO = [
 ("2026-06-28","15:00",73,"R32","RU_A","Runner-up A","RU_B","Runner-up B","SoFi Stadium, Inglewood"),
 ("2026-06-29","13:00",76,"R32","W_C","Winner C","RU_F","Runner-up F","NRG Stadium, Houston"),
 ("2026-06-29","16:30",74,"R32","W_E","Winner E","T3_74","Best 3rd (A/B/C/D/F)","Gillette Stadium, Foxborough"),
 ("2026-06-29","21:00",75,"R32","W_F","Winner F","RU_C","Runner-up C","Estadio BBVA, Monterrey"),
 ("2026-06-30","13:00",78,"R32","RU_E","Runner-up E","RU_I","Runner-up I","AT&T Stadium, Arlington"),
 ("2026-06-30","17:00",77,"R32","W_I","Winner I","T3_77","Best 3rd (C/D/F/G/H)","MetLife Stadium, East Rutherford"),
 ("2026-06-30","21:00",79,"R32","W_A","Winner A","T3_79","Best 3rd (C/E/F/H/I)","Estadio Azteca, Mexico City"),
 ("2026-07-01","12:00",80,"R32","W_L","Winner L","T3_80","Best 3rd (E/H/I/J/K)","Mercedes-Benz Stadium, Atlanta"),
 ("2026-07-01","16:00",82,"R32","W_G","Winner G","T3_82","Best 3rd (A/E/H/I/J)","Lumen Field, Seattle"),
 ("2026-07-01","20:00",81,"R32","W_D","Winner D","T3_81","Best 3rd (B/E/F/I/J)","Levi's Stadium, Santa Clara"),
 ("2026-07-02","15:00",84,"R32","W_H","Winner H","RU_J","Runner-up J","SoFi Stadium, Inglewood"),
 ("2026-07-02","19:00",83,"R32","RU_K","Runner-up K","RU_L","Runner-up L","BMO Field, Toronto"),
 ("2026-07-02","23:00",85,"R32","W_B","Winner B","T3_85","Best 3rd (E/F/G/I/J)","BC Place, Vancouver"),
 ("2026-07-03","14:00",88,"R32","RU_D","Runner-up D","RU_G","Runner-up G","AT&T Stadium, Arlington"),
 ("2026-07-03","18:00",86,"R32","W_J","Winner J","RU_H","Runner-up H","Hard Rock Stadium, Miami Gardens"),
 ("2026-07-03","21:30",87,"R32","W_K","Winner K","T3_87","Best 3rd (D/E/I/J/L)","Arrowhead Stadium, Kansas City"),

 ("2026-07-04","13:00",90,"R16","W_M73","Winner M73","W_M75","Winner M75","NRG Stadium, Houston"),
 ("2026-07-04","17:00",89,"R16","W_M74","Winner M74","W_M77","Winner M77","Lincoln Financial Field, Philadelphia"),
 ("2026-07-05","16:00",91,"R16","W_M76","Winner M76","W_M78","Winner M78","MetLife Stadium, East Rutherford"),
 ("2026-07-05","20:00",92,"R16","W_M79","Winner M79","W_M80","Winner M80","Estadio Azteca, Mexico City"),
 ("2026-07-06","15:00",93,"R16","W_M83","Winner M83","W_M84","Winner M84","AT&T Stadium, Arlington"),
 ("2026-07-06","20:00",94,"R16","W_M81","Winner M81","W_M82","Winner M82","Lumen Field, Seattle"),
 ("2026-07-07","12:00",95,"R16","W_M86","Winner M86","W_M88","Winner M88","Mercedes-Benz Stadium, Atlanta"),
 ("2026-07-07","16:00",96,"R16","W_M85","Winner M85","W_M87","Winner M87","BC Place, Vancouver"),

 ("2026-07-09","16:00",97,"Quarterfinal","W_M89","Winner M89","W_M90","Winner M90","Gillette Stadium, Foxborough"),
 ("2026-07-10","15:00",98,"Quarterfinal","W_M93","Winner M93","W_M94","Winner M94","SoFi Stadium, Inglewood"),
 ("2026-07-11","17:00",99,"Quarterfinal","W_M91","Winner M91","W_M92","Winner M92","Hard Rock Stadium, Miami Gardens"),
 ("2026-07-11","21:00",100,"Quarterfinal","W_M95","Winner M95","W_M96","Winner M96","Arrowhead Stadium, Kansas City"),

 ("2026-07-14","15:00",101,"Semifinal","W_M97","Winner M97","W_M98","Winner M98","AT&T Stadium, Arlington"),
 ("2026-07-15","15:00",102,"Semifinal","W_M99","Winner M99","W_M100","Winner M100","Mercedes-Benz Stadium, Atlanta"),

 ("2026-07-18","17:00",103,"Third-Place Match","L_M101","Loser M101","L_M102","Loser M102","Hard Rock Stadium, Miami Gardens"),
 ("2026-07-19","15:00",104,"FINAL","W_M101","Winner M101","W_M102","Winner M102","MetLife Stadium, East Rutherford"),
]


def esc(t):
    return t.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;")


def resolve(token, label, results):
    """Return the real team if known in results.json, else the placeholder label."""
    name = results.get(token, "")
    return name.strip() if name and name.strip() else label


def vevent(dt, t, summary, venue, dur_min, uid):
    hh, mm = t.split(":")
    s = datetime.datetime(int(dt[:4]), int(dt[5:7]), int(dt[8:10]), int(hh), int(mm))
    e = s + datetime.timedelta(minutes=dur_min)
    return [
        "BEGIN:VEVENT",
        f"UID:{uid}@wc2026.techy",
        "DTSTAMP:20260609T000000Z",
        f"DTSTART;TZID=America/New_York:{dt.replace('-','')}T{hh}{mm}00",
        f"DTEND;TZID=America/New_York:{e.strftime('%Y%m%dT%H%M%S')}",
        f"SUMMARY:{esc(summary)}",
        f"LOCATION:{esc(venue)}",
        "BEGIN:VALARM", "TRIGGER:-PT30M", "ACTION:DISPLAY",
        "DESCRIPTION:Kickoff soon", "END:VALARM",
        "END:VEVENT",
    ]


def build(results):
    lines = [
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Techy//WorldCup2026//EN",
        "CALSCALE:GREGORIAN", "METHOD:PUBLISH", "X-WR-CALNAME:FIFA World Cup 2026",
        "X-WR-TIMEZONE:America/New_York",
        "BEGIN:VTIMEZONE", "TZID:America/New_York",
        "BEGIN:DAYLIGHT", "TZOFFSETFROM:-0500", "TZOFFSETTO:-0400", "TZNAME:EDT",
        "DTSTART:19700308T020000", "RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU", "END:DAYLIGHT",
        "BEGIN:STANDARD", "TZOFFSETFROM:-0400", "TZOFFSETTO:-0500", "TZNAME:EST",
        "DTSTART:19701101T020000", "RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU", "END:STANDARD",
        "END:VTIMEZONE",
    ]

    m = 1
    for dt, t, title, venue in GROUP:
        lines += vevent(dt, t, f"\u26bd {title}  (M{m})", venue, 120, f"wc2026-m{m}")
        m += 1

    for dt, t, num, stage, ht, hl, at_, al, venue in KO:
        home = resolve(ht, hl, results)
        away = resolve(at_, al, results)
        emoji = "\U0001F3C6" if stage == "FINAL" else "\u26bd"
        lines += vevent(dt, t, f"{emoji} {stage} (M{num}): {home} vs {away}", venue, 165, f"wc2026-m{num}")

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "results.json"
    try:
        with open(path, encoding="utf-8") as f:
            results = json.load(f)
    except FileNotFoundError:
        print(f"No {path} found — generating with placeholders only.")
        results = {}

    ics = build(results)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(ics)

    total = ics.count("BEGIN:VEVENT")
    filled = sum(1 for k, v in results.items() if not k.startswith("_") and str(v).strip())
    print(f"Wrote {OUT_PATH}  |  {total} matches  |  {filled} knockout slots resolved")


if __name__ == "__main__":
    main()
