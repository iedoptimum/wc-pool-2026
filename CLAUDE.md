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
Google Sheet (Leaderboard tab, cols F–K row 4+)
    → GithubDashboard.gs doGet() Web App
        → JSON payload fetched by index.html on load
            → renderAll(data) → renderLeaderboard / renderStages / renderChart
```

### Google Sheet Structure (File ID: `14KZgWp-H8g7LXgUQxgAi9E5CHUGo7WFlqsB7Splzj1o`)
- **Leaderboard sheet**: F=Name, G=TotalPoints, H=FlagUrl, I=GroupPts, J=KnockoutPts, K=MidTourneyPts (data starts row 4)
- **Per-player sheets** (named by player): `L148` holds their champion country pick
- **World Cup 2026 Results sheet**: stage-completion sentinel cells — `F90` (Group Stage done), `K141` (Knockout Buster done)

### API Payload Shape
```json
{
  "players": [{ "name", "points", "champion", "flagUrl", "groupPts", "knockoutPts", "midPts" }],
  "stageLeaders": { "groupStage", "knockout", "midTourney", "overall" },
  "groupStageDone": true,
  "knockoutBusterDone": false,
  "lastUpdated": "ISO string"
}
```

### Stage Status Logic (index.html)
`STAGES` array is defined with default `"active"` statuses. `renderAll()` overrides them from the API flags before calling `renderStages()`:
- `STAGES[0]` (Group Stage) → `"done"` when `groupStageDone === true`
- `STAGES[1]` (Knockout Buster) → `"done"` when `knockoutBusterDone === true`
- Dot colours: green = done, gold/yellow = active, grey = upcoming

### Key Rules
- Players with 0 **total** points are filtered out of the leaderboard entirely (intentional).
- `topPlayer()` only considers players with > 0 in the specific field — prevents false leaders when a category hasn't started.
- Flag images use `flagcdn.com/w40/{code}.png`. Country → code mapping is in `COUNTRY_FLAGS` in the `.gs` file.

## Workflow

**After editing `index.html`:** commit and push — no other steps needed.

**After editing `GithubDashboard.gs`:**
1. Commit and push the `.gs` file to GitHub.
2. Copy the full file contents into the Apps Script editor in the Google Sheet.
3. Deploy → Manage deployments → New version.

**Git discipline:** commit and push after every meaningful change so the repo always has a working rollback point.

## Apps Script Deployment Settings
- Execute as: **Me**
- Who has access: **Anyone**
