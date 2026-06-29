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
| R32 (Jun 28 – Jul 3) | `W_M73..W_M88` → R16 (M89–96) | ⚽ In progress |
| R16 (Jul 4–5) | `W_M89..W_M96` → QF (M97–100) | — |
| QF (Jul 9–11) | `W_M97..W_M100` → SF (M101–102) | — |
| SF (Jul 14–15) | `W_M101/W_M102` (Final), `L_M101/L_M102` (3rd place) | — |

## R32 bracket (M73–M88) — fill `W_M##` as results come in

| Match | Date (ET) | Home | Away | Venue |
|-------|-----------|------|------|-------|
| M73 | Jun 28 15:00 | South Africa (RU_A) | Canada (RU_B) | SoFi Stadium, Inglewood |
| M74 | Jun 29 16:30 | Germany (W_E) | Paraguay (T3) | Gillette Stadium, Foxborough |
| M75 | Jun 29 21:00 | Netherlands (W_F) | Morocco (RU_C) | Estadio BBVA, Monterrey |
| M76 | Jun 29 13:00 | Brazil (W_C) | Japan (RU_F) | NRG Stadium, Houston |
| M77 | Jun 30 17:00 | France (W_I) | Sweden (T3) | MetLife Stadium, East Rutherford |
| M78 | Jun 30 13:00 | Ivory Coast (RU_E) | Norway (RU_I) | AT&T Stadium, Arlington |
| M79 | Jun 30 21:00 | Mexico (W_A) | Ecuador (T3) | Estadio Azteca, Mexico City |
| M80 | Jul 1 12:00 | England (W_L) | DR Congo (T3) | Mercedes-Benz Stadium, Atlanta |
| M81 | Jul 1 20:00 | USA (W_D) | Bosnia & Herzegovina (T3) | Levi's Stadium, Santa Clara |
| M82 | Jul 1 16:00 | Belgium (W_G) | Senegal (T3) | Lumen Field, Seattle |
| M83 | Jul 2 19:00 | Portugal (RU_K) | Croatia (RU_L) | BMO Field, Toronto |
| M84 | Jul 2 15:00 | Spain (W_H) | Austria (RU_J) | SoFi Stadium, Inglewood |
| M85 | Jul 2 23:00 | Switzerland (W_B) | Algeria (T3) | BC Place, Vancouver |
| M86 | Jul 3 18:00 | Argentina (W_J) | Cape Verde (RU_H) | Hard Rock Stadium, Miami Gardens |
| M87 | Jul 3 21:30 | Colombia (W_K) | Ghana (T3) | Arrowhead Stadium, Kansas City |
| M88 | Jul 3 14:00 | Australia (RU_D) | Egypt (RU_G) | AT&T Stadium, Arlington |
