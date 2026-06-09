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
**A) Subscribe by URL (auto-refresh) — recommended.** Commit the `.ics` to this
repo (GitHub Pages), then in Google Calendar: Other calendars → From URL →
`https://<user>.github.io/<repo>/World_Cup_2026.ics`. Google re-polls on its own
(minutes up to ~24h). Each round: edit `results.json`, regenerate, push.
```bash
python generate_wc_ics.py
git add World_Cup_2026.ics results.json
git commit -m "Resolve <round> teams"
git push
```
**B) Re-import file (instant, manual).** Regenerate and import the `.ics` again;
stable UIDs update the existing events.

## Resolution timeline
| After | Fill |
|-------|------|
| Group stage (Jun 27) | `W_*`, `RU_*`, all `T3_*` → resolves R32 (M73–88) |
| R32 | `W_M73..W_M88` → R16 (M89–96) |
| R16 | `W_M89..W_M96` → QF (M97–100) |
| QF | `W_M97..W_M100` → SF (M101–102) |
| SF | `W_M101/W_M102` (Final), `L_M101/L_M102` (3rd place) |

## Optional next step
Auto-populate `results.json` from the **World Cup 2026 Results** sheet (match #s
align with FIFA's official numbering used here) instead of hand-editing — via CSV
export or an Apps Script endpoint.

## Continuing in VS Code
1. Save these files into the repo folder; open in VS Code (`code .` from Git Bash).
2. Edit `results.json`, run the generator, push per the workflow above.
3. If using an AI coding assistant in VS Code (e.g. Claude Code), point it at this
   file for context — it captures every decision. Claude Code docs:
   https://docs.claude.com/en/docs/claude-code/overview
