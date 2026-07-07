# World Cup 2026 — Calendar Generator (Handoff)

Self-updating FIFA World Cup 2026 calendar for the fantasy pool. Generates a
single `.ics` (all 104 matches) that fills in real knockout teams as the bracket
resolves. Companion to the Google Sheets pool + GitHub Pages dashboard.

## Files
| File | Role |
|------|------|
| `generate_wc_ics.py` | Generator. Schedule (dates/times/venues/match #s) is baked in. Reads `results.json`, writes `World_Cup_2026.ics`. |
| `results.json` | Input. Maps knockout slot tokens → team names. Blank = placeholder. |
| `World_Cup_2026.ics` | Output. Import or subscribe in Google Calendar. |

## Run
```bash
python generate_wc_ics.py            # uses ./results.json
python generate_wc_ics.py other.json # custom input
```

## How updates work
- All times Eastern Time, encoded with a `VTIMEZONE` block (displays correctly in any tz).
- UIDs are stable (`wc2026-m{N}`) → re-importing **updates events in place**, no duplicates.
- Group stage (M1–M72) is fixed and fully named. Only knockout slots need resolving.
- Tokens: `W_x`=Group x winner, `RU_x`=runner-up, `T3_##`=best-3rd feeding match ##,
  `W_M##`=winner of match ##, `L_M##`=loser of match ##.
- You set only **leaf facts** (group results + each match's winner). Matches that
  reference them update automatically — e.g. setting `W_M73` updates R16 match M90.

## Delivery: pick ONE
**A) Subscribe by URL (auto-refresh) — recommended.** Google Calendar → Other calendars → From URL:
```
https://iedoptimum.github.io/wc-pool-2026/calendar-games/World_Cup_2026.ics
```
Google re-polls on its own (up to ~24h). Each round: edit `results.json`, regenerate, push.
```bash
python generate_wc_ics.py
git add World_Cup_2026.ics results.json
git commit -m "Resolve <round> teams"
git push
```
> **Google Calendar cache stuck?** Unsubscribe, then re-subscribe with `?v=2` (or `?v=3`, etc.) appended to the URL — Google treats it as a new URL and forces a fresh fetch. iPhone calendar fetches directly and always shows current data.

**B) Re-import file (instant, manual).** Regenerate and import the `.ics` again;
stable UIDs update the existing events.

## Resolution timeline
| After | Fill | Status |
|-------|------|--------|
| Group stage (Jun 27) | `W_*`, `RU_*`, all `T3_*` → resolves R32 (M73–88) | ✅ Done |
| R32 (Jun 28 – Jul 3) | `W_M73..W_M88` → R16 (M89–96) | ✅ Done |
| R16 (Jul 4–7) | `W_M89..W_M96` → QF (M97–100) | ⚽ In progress — M89–94 done, M95/M96 (Jul 7) pending |
| QF (Jul 9–11) | `W_M97..W_M100` → SF (M101–102) | — |
| SF (Jul 14–15) | `W_M101/W_M102` (Final), `L_M101/L_M102` (3rd place) | — |

## R32 results (M73–M88) — all resolved

| Match | Date (ET) | Home | Away | Winner | Venue |
|-------|-----------|------|------|--------|-------|
| M73 | Jun 28 15:00 | South Africa | Canada | **Canada** (1-0) | SoFi Stadium, Inglewood |
| M74 | Jun 29 16:30 | Germany | Paraguay | **Paraguay** (1-1, 4-3 pens) | Gillette Stadium, Foxborough |
| M75 | Jun 29 21:00 | Netherlands | Morocco | **Morocco** (1-1, 3-2 pens) | Estadio BBVA, Monterrey |
| M76 | Jun 29 13:00 | Brazil | Japan | **Brazil** (2-1) | NRG Stadium, Houston |
| M77 | Jun 30 17:00 | France | Sweden | **France** (3-0) | MetLife Stadium, East Rutherford |
| M78 | Jun 30 13:00 | Ivory Coast | Norway | **Norway** (2-1) | AT&T Stadium, Arlington |
| M79 | Jun 30 21:00 | Mexico | Ecuador | **Mexico** | Estadio Azteca, Mexico City |
| M80 | Jul 1 12:00 | England | DR Congo | **England** | Mercedes-Benz Stadium, Atlanta |
| M81 | Jul 1 20:00 | USA | Bosnia & Herzegovina | **USA** (2-0) | Levi's Stadium, Santa Clara |
| M82 | Jul 1 16:00 | Belgium | Senegal | **Belgium** (3-2 AET) | Lumen Field, Seattle |
| M83 | Jul 2 19:00 | Portugal | Croatia | **Portugal** | BMO Field, Toronto |
| M84 | Jul 2 15:00 | Spain | Austria | **Spain** | SoFi Stadium, Inglewood |
| M85 | Jul 2 23:00 | Switzerland | Algeria | **Switzerland** (2-0) | BC Place, Vancouver |
| M86 | Jul 3 18:00 | Argentina | Cape Verde | **Argentina** (3-2 AET) | Hard Rock Stadium, Miami Gardens |
| M87 | Jul 3 21:30 | Colombia | Ghana | **Colombia** (1-0) | Arrowhead Stadium, Kansas City |
| M88 | Jul 3 14:00 | Australia | Egypt | **Egypt** (pens) | AT&T Stadium, Arlington |

## R16 bracket (M89–M96)

| Match | Date (ET) | Home | Away | Winner | Venue |
|-------|-----------|------|------|--------|-------|
| M89 | Jul 4 13:00 | Canada (W_M73) | Morocco (W_M75) | **Morocco** (3-0) | NRG Stadium, Houston |
| M90 | Jul 4 17:00 | Paraguay (W_M74) | France (W_M77) | **France** (1-0) | Lincoln Financial Field, Philadelphia |
| M91 | Jul 5 16:00 | Brazil (W_M76) | Norway (W_M78) | **Norway** (2-1) | MetLife Stadium, East Rutherford |
| M92 | Jul 5 20:00 | Mexico (W_M79) | England (W_M80) | **England** (3-2) | Estadio Azteca, Mexico City |
| M93 | Jul 6 15:00 | Portugal (W_M83) | Spain (W_M84) | **Spain** (1-0) | AT&T Stadium, Arlington |
| M94 | Jul 6 20:00 | USA (W_M81) | Belgium (W_M82) | **Belgium** (4-1) | Lumen Field, Seattle |
| M95 | Jul 7 12:00 | Argentina (W_M86) | Egypt (W_M88) | pending | Mercedes-Benz Stadium, Atlanta |
| M96 | Jul 7 16:00 | Switzerland (W_M85) | Colombia (W_M87) | pending | BC Place, Vancouver |

## Quarterfinals (M97–M100) — set so far

| Match | Date (ET) | Matchup | Venue |
|-------|-----------|---------|-------|
| M97 | Jul 9 16:00 | Morocco vs France | Gillette Stadium, Foxborough |
| M98 | Jul 10 15:00 | Spain vs Belgium | SoFi Stadium, Inglewood |
| M99 | Jul 11 17:00 | Norway vs England | Hard Rock Stadium, Miami Gardens |
| M100 | Jul 11 21:00 | Winner M95 vs Winner M96 | Arrowhead Stadium, Kansas City |
