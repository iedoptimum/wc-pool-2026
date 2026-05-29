# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A mobile-first FIFA World Cup 2026 pool leaderboard dashboard. Players predict match results in a Google Sheet; scores are served via a Google Apps Script Web App and displayed in a single-page HTML dashboard.

## Repository Structure

- **`index.html`** — the entire frontend: HTML, CSS, and JavaScript in one file. No build step, no dependencies to install.
- **`GithubDashboard.gs`** — Google Apps Script (backend API). Lives locally for version control but must be manually copied into the Apps Script editor (`Extensions → Apps Script`) and redeployed as a new Web App version after every change.

## Key Architecture

### Data Flow
```
Google Sheet (Leaderboard tab, cols F–M, row 4+)
    → GithubDashboard.gs doGet() Web App
        → JSON payload fetched by index.html on load
            → renderAll(data) → renderLeaderboard / renderStages / renderChart / renderAllPlayers
```

### Google Sheet Structure (File ID: `14KZgWp-H8g7LXgUQxgAi9E5CHUGo7WFlqsB7Splzj1o`)
- **Leaderboard sheet** (data starts row 4):
  - F=Name, G=TotalPoints, H=FlagUrl (written back by script), I=GroupPts, J=KnockoutPts, K=MidTourneyPts, L=3rdPlacePts, M=GoldenAwardsPts
- **Per-player sheets** (tab named by player): `L148` = their champion country pick
- **World Cup 2026 Results sheet** — sentinel cells that drive stage completion and awards:

| Cell | Drives |
|------|--------|
| F90  | Group Stage done |
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
    "groupPts", "knockoutPts", "midPts", "thirdPlacePts", "goldenAwardsPts"
  }],
  "stageLeaders": {
    "groupStage", "knockout", "midTourney",
    "overall", "secondPlace", "thirdPlace", "goldenAwards"
  },
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

### Stage Status Logic (index.html)
`STAGES` array (7 entries, indices 0–6) has statuses overridden in `renderAll()` from API flags:

| Index | Stage | Yellow trigger | Green trigger |
|-------|-------|---------------|---------------|
| 0 | Group Stage 👑 | default | `groupStageDone` |
| 1 | Knockout Buster | default | `knockoutBusterDone` |
| 2 | Mid-Tournament | default | `midTourneyDone` |
| 3 | Grand Champion 🏆 | default | `grandChampionDone` |
| 4 | 2nd Place - Almost Champion | default | `grandChampionDone` |
| 5 | 3rd Place Pick | upcoming → skips yellow | `thirdPlaceDone` |
| 6 | Golden Awards | upcoming → skips yellow | `grandChampionDone` |

Dot colours: green = `done`, gold = `active`, grey = `upcoming`.

### Special Winner Logic (GithubDashboard.gs)
- **`topPlayer(players, field)`** — only considers players with `field > 0`; prevents false leaders when a category hasn't started.
- **3rd Place Pick** — winner = any player with `thirdPlacePts === 5`; tiebreak = lowest total points.
- **Golden Awards** — winner = most `goldenAwardsPts`; tiebreak = lowest total points.
- **`stageLeaders.secondPlace`** — always `players[1]` (second in total points sort).

### Display Rules
- Players with 0 **total** points are filtered out entirely (intentional — `Number(r[1]) > 0`).
- Standings and Points tabs show **top 7** only (`players.slice(0, 7)`).
- All Players tab shows **all players** in leaderboard sort order with point breakdowns (no champion flag column).
- Tournament champion banner appears above the leaderboard only when `tournamentChampion.team` is non-empty.
- Flag images use `flagcdn.com/w40/{code}.png` (w80 for champion banner). Country → code mapping is `COUNTRY_FLAGS` in the `.gs`.

### Tabs
- **Standings** — top 7 leaderboard + special awards + champion banner
- **Stages** — payout structure + tournament stage progress
- **Points** — bar chart + points gap (top 7)
- **All Players** — full compact table, all players, all point columns

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
