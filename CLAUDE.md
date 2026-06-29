# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Calendar generator
@calendar-games/calendar-wc26-games.md

## Project Overview

A mobile-first FIFA World Cup 2026 pool leaderboard dashboard. Players predict match results in a Google Sheet; scores are served via a Google Apps Script Web App and displayed in a single-page HTML dashboard.

## Repository Structure

- **`index.html`** — the entire frontend: HTML, CSS, and JavaScript in one file. No build step, no dependencies to install.
- **`GithubDashboard.gs`** — Google Apps Script (backend API). Lives locally for version control but must be manually copied into the Apps Script editor (`Extensions → Apps Script`) and redeployed as a new Web App version after every change.

## Key Architecture

### Data Flow
```
Google Sheet (Leaderboard tab, cols F–O, row 4+)
    → GithubDashboard.gs doGet() Web App
        → JSON payload fetched by index.html on load
            → renderAll(data) → renderLeaderboard / renderStages / renderChart / renderAllPlayers / renderSignedUp
```

### Google Sheet Structure (File ID: `14KZgWp-H8g7LXgUQxgAi9E5CHUGo7WFlqsB7Splzj1o`)
- **Leaderboard sheet** — player data read as fixed range **F4:O41**:
  - F=Name, G=TotalPoints, H=FlagUrl (**must be pre-filled manually**; script reads it, no longer writes it), I=GroupPts, J=KnockoutPts, K=MidTourneyPts, L=3rdPlacePts, M=GoldenAwardsPts, N=BracketURL, O=GroupBonusPts
  - Misc cells batched in one read of **P3:S13**: Q3=pool total, P7=update date, Q7=update time, P10=Master Key URL, P13=Audit PDF URL, S4=temp player sentinel
  - S4:U41 = pre-tournament temp player list: S=Name, T=FlagUrl (flagcdn URL), U=Status
- **Per-player sheets are NOT read at runtime.** Champion country name is derived from col H flag URL via `FLAG_TO_COUNTRY` reverse map (code → name), not from individual player sheet tabs.
- **World Cup 2026 Results sheet** — sentinel cells that drive stage completion and awards:

| Cell | Drives |
|------|--------|
| F108 | Group Stage done |
| K141 | Knockout Buster done |
| R129 | Mid-Tournament done |
| B175 | Grand Champion / 2nd Place / Golden Awards done |
| P158 | 3rd Place team name (award card) |
| R158 | 3rd Place team flag URL (award card) |
| B169 | Golden Boot winner name |
| B172 | Golden Ball winner name |
| B175 | Golden Glove winner name |
| L148 | Tournament champion team name (champion banner) |

### API Payload Shape
```json
{
  "players": [{
    "name", "points", "champion", "flagUrl",
    "groupPts", "groupBonusPts", "groupCombinedPts",
    "knockoutPts", "midPts", "thirdPlacePts", "goldenAwardsPts", "bracketUrl"
  }],
  "stageLeaders": {
    "groupStage", "knockout", "midTourney",
    "overall", "secondPlace", "thirdPlace", "goldenAwards"
  },
  "poolTotal": 0,
  "masterKeyUrl": "",
  "auditUrl": "",
  "dataUpdatedAt": "M/d/yyyy h:mm a",
  "hasTempPlayers": false,
  "tempPlayers": [{ "name", "flagUrl", "status" }],
  "groupStageDone": false,
  "knockoutBusterDone": false,
  "midTourneyDone": false,
  "grandChampionDone": false,
  "thirdPlaceDone": false,
  "thirdPlaceTeam": "",
  "thirdPlaceTeamFlag": "",
  "goldenBoot": "", "goldenBall": "", "goldenGlove": "",
  "tournamentChampion": { "team": "", "flagUrl": "" },
  "lastUpdated": "ISO string"
}
```

### Pre-Tournament Mode (Signed tab)
- **Trigger**: `S4` in Leaderboard sheet has a value → `hasTempPlayers = true`
- **Signed tab** appears as the first tab and becomes the default active tab on first render
- Shows players from S:U with rank #, champion flag (or ❓ if T is blank), name, and status badge
- Player count pill shows temp list size instead of regular players
- When S4 is cleared (tournament starts), tab disappears and Standings becomes the default again
- `defaultTabSet` flag (JS module-level) prevents auto-tab-switching after first render; user's manual tab selection is preserved across background refreshes

### Auto-Refresh Logic (index.html `loadData`)
1. Render from `localStorage` cache immediately (key: `wc26_pool_cache`)
2. Fetch fresh data in background with `?_cb=Date.now()` to bust HTTP cache; **`cache:"no-store"` is intentionally absent** — it breaks iOS Safari's redirect handling for Apps Script URLs (302 → `script.googleusercontent.com`). A 15-second `AbortController` timeout is used instead.
3. Compare `newData.dataUpdatedAt` against cached value — only re-render if different
4. `dataUpdatedAt` is formatted server-side by Apps Script using `Utilities.formatDate` + sheet timezone (avoids UTC shift from `toISOString()`)

### Stage Status Logic (index.html)
`STAGES` array (7 entries, indices 0–6) — statuses overridden in `renderAll()` from API flags:

| Index | Stage | Green trigger |
|-------|-------|--------------|
| 0 | Group Stage 👑 | `groupStageDone` |
| 1 | Knockout Buster | `knockoutBusterDone` |
| 2 | Mid-Tournament | `midTourneyDone` |
| 3 | Grand Champion 🏆 | `grandChampionDone` |
| 4 | 2nd Place - Almost Champion | `grandChampionDone` |
| 5 | 3rd Place Pick | `thirdPlaceDone` (skips yellow, goes upcoming→done) |
| 6 | Golden Awards | `grandChampionDone` (skips yellow) |

Dot colours: green = `done`, gold = `active`, grey = `upcoming`.

### Special Winner Logic (GithubDashboard.gs)
- **`topPlayer(players, field)`** — only considers players with `field > 0`; prevents false leaders when a category hasn't started.
- **Group Stage King/Queen** — winner = highest `groupCombinedPts` (col I + col O); tiebreak = first in total-points sort.
- **3rd Place Pick** — winner = any player with `thirdPlacePts === 5`; tiebreak = lowest total points.
- **Golden Awards** — winner = most `goldenAwardsPts`; tiebreak = lowest total points.
- **`stageLeaders.secondPlace`** — always `players[1]` (second in total points sort).

### Display Rules
- Players with 0 **total** points are included in All Players tab; blank rows are still skipped (`r[0] !== ""`). Standings/Points tabs show top 7 only so 0-point players won't appear there naturally.
- Standings and Points tabs show **top 7** only (`players.slice(0, 7)`).
- All Players tab shows **all players** in leaderboard sort order with point breakdowns.
- Grand Champion badge (`.gc-badge`) renders inline on rank-1 leaderboard row when `grandChampionDone`.
- Tournament champion banner appears above the leaderboard only when `tournamentChampion.team` is non-empty.
- Pool total card in Stages tab shown only when `poolTotal > 0`; payout amounts per card calculated from it.
- Master Tournament Key card in All Players tab shown only when `masterKeyUrl` is non-empty.
- Audit footnote link (`#audit-link-row`) in All Players tab shown only when `auditUrl` is non-empty; very low-opacity, opens in new tab, links to a PDF of pre-tournament bracket printouts.
- Flag images use `flagcdn.com/w40/{code}.png` (w80 for champion banner). Country → code mapping is `COUNTRY_FLAGS` in the `.gs`; `FLAG_TO_COUNTRY` is the reverse (code → country name), built at load time from the same object.
- **If a player's col H flag URL is blank, their champion will show as `"—"`.** Populate col H manually when adding new players.

### Tabs
- **Signed** — pre-tournament only; players from S:U temp list; hidden once S4 is cleared
- **Standings** — top 7 leaderboard + special awards + champion banner
- **Stages** — pool total card + payout structure + tournament stage progress
- **Points** — bar chart + points gap (top 7)
- **All Players** — master key card + full compact table with bracket links + audit footnote link

### Tab Switching
Tab buttons use `data-tab` attributes; `switchTab(name)` / `activateTab(name)` match by attribute (not index). `activateTab` is the internal function used by both user clicks and auto-switching.

## Workflow

**After editing `index.html`:** commit and push — no other steps needed.

**After editing `GithubDashboard.gs`:**
1. Commit and push the `.gs` file to GitHub.
2. Copy the full file contents into the Apps Script editor in the Google Sheet (`Extensions → Apps Script`).
3. Click Deploy → Manage deployments → create a New version.

**Git discipline:** commit and push after every meaningful change so the repo always has a working rollback point.

## Apps Script Deployment Settings
- Execute as: **Me**
- Who has access: **Anyone**
