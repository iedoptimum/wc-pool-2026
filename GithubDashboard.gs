// ============================================================
// World Cup 2026 Pool — Leaderboard API
// Paste this into Extensions → Apps Script in your Google Sheet
// Deploy as Web App: Execute as Me, Access Anyone
// ============================================================

// ─────────────────────────────────────────────────────────────
// Country name (exactly as in L148) → flagcdn.com 2-letter code
// All 48 WC2026 teams + UEFA path placeholders
// ─────────────────────────────────────────────────────────────
const COUNTRY_FLAGS = {
  // Group A
  "Mexico":           "mx",
  "South Korea":      "kr",
  "South Africa":     "za",
  "Czechia":          "cz",

  // Group B
  "Canada":           "ca",
  "Qatar":            "qa",
  "Switzerland":      "ch",
  "Bosnia & Hrzgvna": "ba",
  "Bosnia":           "ba",

  // Group C
  "Brazil":           "br",
  "Haiti":            "ht",
  "Scotland":         "gb-sct",
  "Morocco":          "ma",

  // Group D
  "USA":              "us",
  "United States":    "us",
  "Australia":        "au",
  "Paraguay":         "py",
  "Turkiye":          "tr",
  "Turkey":           "tr",

  // Group E
  "Germany":          "de",
  "Ivory Coast":      "ci",
  "Ecuador":          "ec",
  "Curacao":          "cw",

  // Group F
  "Netherlands":      "nl",
  "Japan":            "jp",
  "Sweden":           "se",
  "Tunisia":          "tn",

  // Group G
  "Belgium":          "be",
  "Egypt":            "eg",
  "Iran":             "ir",
  "New Zealand":      "nz",

  // Group H
  "Spain":            "es",
  "Saudi Arabia":     "sa",
  "Uruguay":          "uy",
  "Cape Verde":       "cv",

  // Group I
  "France":           "fr",
  "Senegal":          "sn",
  "Iraq":             "iq",
  "Norway":           "no",

  // Group J
  "Argentina":        "ar",
  "Algeria":          "dz",
  "Austria":          "at",
  "Jordan":           "jo",

  // Group K
  "Portugal":         "pt",
  "Colombia":         "co",
  "Columbia":         "co",
  "Uzbekistan":       "uz",
  "DR Congo":         "cd",

  // Group L
  "England":          "gb-eng",
  "Croatia":          "hr",
  "Ghana":            "gh",
  "Panama":           "pa",

  // Other qualified / path teams
  "Serbia":           "rs",
  "Denmark":          "dk",
  "Poland":           "pl",
  "Ukraine":          "ua",
  "Cameroon":         "cm",
  "Nigeria":          "ng",
  "Mali":             "ml",
  "Kenya":            "ke",
  "Honduras":         "hn",
  "Costa Rica":       "cr",
  "Jamaica":          "jm",
  "Venezuela":        "ve",
  "Chile":            "cl",
  "Peru":             "pe",
  "Bolivia":          "bo",
  "China":            "cn",
  "Indonesia":        "id",
  "Bahrain":          "bh",
  "Kuwait":           "kw",
  "Oman":             "om",
};

// ─────────────────────────────────────────────────────────────
// Main API endpoint
// ─────────────────────────────────────────────────────────────
function doGet() {

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const lb = ss.getSheetByName("Leaderboard");

  // Player List: F=Name, G=TotalPoints, H=CountryFlag,
  //              I=GroupStgPts, J=KnockoutPts, K=MidTourneyPts, L=3rdPlacePts, M=GoldenAwardsPts
  const lastRow   = lb.getLastRow();
  const dataRange = lb.getRange(4, 6, lastRow - 3, 8); // F4:M(lastRow)
  const rows      = dataRange.getValues();

  const players = rows
    .filter(r => r[0] !== "" && Number(r[1]) > 0)  // skip blanks and zeros
    .map(r => {
      const playerName   = String(r[0]);
      const championName = getChampionName(ss, playerName);  // L148 of player sheet
      const countryCode  = getCountryCode(championName);     // flagcdn.com code
      const flagUrl      = countryCode
        ? "https://flagcdn.com/w40/" + countryCode + ".png"
        : "";

      // Write flag URL back to Leaderboard col H so sheet stays in sync
      writeToLeaderboard(lb, rows, playerName, flagUrl);

      return {
        name:          playerName,
        points:        Number(r[1]),
        champion:      championName,
        countryCode:   countryCode,
        flagUrl:       flagUrl,
        groupPts:        Number(r[3]),
        knockoutPts:     Number(r[4]),
        midPts:          Number(r[5]),
        thirdPlacePts:   Number(r[6]),
        goldenAwardsPts: Number(r[7]),
      };
    })
    .sort((a, b) => b.points - a.points);

  // Stage leaders
  // 3rd Place Pick winner: any player with thirdPlacePts === 5;
  // tiebreak = lowest total points
  const thirdPlaceCandidates = players.filter(p => p.thirdPlacePts === 5);
  const thirdPlaceWinner = thirdPlaceCandidates.length > 0
    ? thirdPlaceCandidates.reduce((a, b) => a.points <= b.points ? a : b).name
    : null;

  // Golden Awards winner: most points in col M; tiebreak = lowest total points
  const goldenCandidates = players.filter(p => p.goldenAwardsPts > 0);
  const goldenAwardsWinner = goldenCandidates.length > 0
    ? goldenCandidates.reduce((a, b) => {
        if (a.goldenAwardsPts !== b.goldenAwardsPts) return a.goldenAwardsPts > b.goldenAwardsPts ? a : b;
        return a.points <= b.points ? a : b;
      }).name
    : null;

  const stageLeaders = players.length > 0 ? {
    groupStage:  topPlayer(players, "groupPts"),
    knockout:    topPlayer(players, "knockoutPts"),
    midTourney:  topPlayer(players, "midPts"),
    overall:     players[0].name,
    secondPlace: players.length > 1 ? players[1].name : null,
    thirdPlace:   thirdPlaceWinner,
    goldenAwards: goldenAwardsWinner,
  } : {};

  // Stage completion flags driven by Results sheet
  const resultsSheet    = ss.getSheetByName("World Cup 2026 Results");
  const groupStageDone  = resultsSheet
    ? String(resultsSheet.getRange("F90").getValue()).trim() !== ""
    : false;
  const knockoutBusterDone = resultsSheet
    ? String(resultsSheet.getRange("K141").getValue()).trim() !== ""
    : false;
  const midTourneyDone = resultsSheet
    ? String(resultsSheet.getRange("R129").getValue()).trim() !== ""
    : false;
  const grandChampionDone = resultsSheet
    ? String(resultsSheet.getRange("B175").getValue()).trim() !== ""
    : false;

  const payload = {
    players,
    stageLeaders,
    groupStageDone,
    knockoutBusterDone,
    midTourneyDone,
    grandChampionDone,
    thirdPlaceDone: thirdPlaceWinner !== null,
    thirdPlaceTeam:     resultsSheet ? String(resultsSheet.getRange("P158").getValue()).trim() : "",
    thirdPlaceTeamFlag: resultsSheet ? String(resultsSheet.getRange("R158").getValue()).trim() : "",
    lastUpdated: new Date().toISOString(),
  };

  return ContentService
    .createTextOutput(JSON.stringify(payload))
    .setMimeType(ContentService.MimeType.JSON);
}

// ─────────────────────────────────────────────────────────────
// Read champion country name from L148 of the player's sheet
// ─────────────────────────────────────────────────────────────
function getChampionName(ss, playerName) {
  try {
    const sheet = ss.getSheetByName(playerName);
    if (!sheet) return "";
    return String(sheet.getRange("L148").getValue()).trim();
  } catch(e) {
    return "";
  }
}

// ─────────────────────────────────────────────────────────────
// Look up flagcdn.com country code from country name
// Falls back to empty string if not found
// ─────────────────────────────────────────────────────────────
function getCountryCode(countryName) {
  if (!countryName) return "";
  // Exact match first
  if (COUNTRY_FLAGS[countryName]) return COUNTRY_FLAGS[countryName];
  // Case-insensitive fallback
  const lower = countryName.toLowerCase();
  const match = Object.keys(COUNTRY_FLAGS).find(k => k.toLowerCase() === lower);
  return match ? COUNTRY_FLAGS[match] : "";
}

// ─────────────────────────────────────────────────────────────
// Write flag URL back to Leaderboard col H to keep sheet in sync
// ─────────────────────────────────────────────────────────────
function writeToLeaderboard(lb, rows, playerName, flagUrl) {
  try {
    const rowIndex = rows.findIndex(r => String(r[0]) === playerName);
    if (rowIndex === -1) return;
    lb.getRange(rowIndex + 4, 8).setValue(flagUrl);
  } catch(e) {
    // Non-critical — silently skip
  }
}

// ─────────────────────────────────────────────────────────────
// Return the name of the player with the highest value in a field
// ─────────────────────────────────────────────────────────────
function topPlayer(players, field) {
  const eligible = players.filter(p => p[field] > 0);
  if (eligible.length === 0) return null;
  return eligible.reduce((a, b) => a[field] >= b[field] ? a : b).name;
}
