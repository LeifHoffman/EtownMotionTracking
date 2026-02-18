// =============================================================
//  data.js  –  Temporary stub data (replace with MariaDB fetch)
// =============================================================

// ── ATHLETES ──────────────────────────────────────────────────
const DB_ATHLETES = [
  {
    id: 1,
    name: "Evan Swanson",
    email: "evansj@etown.edu",
    jersey: 24,
    team: "Baseball",
    year: "Senior",
    height: "6-3",
    weight: 180,
    major: "Engineering",
    prJump: 19.9,
    prJumpRank: "#2 All Time",
    prDash: 4.77,
    prDashRank: "#15 All Time",
    // monthly averages Jul–May
    jumpHistory: [14.5, 14.8, 15.2, 15.1, 15.6, 15.9, 16.3, 16.8, 17.1, 18.4, 19.9],
    dashHistory: [4.45, 4.42, 4.38, 4.40, 4.35, 4.37, 4.42, 4.38, 4.35, 4.30, 4.33],
    recentTests: [
      { date: "10/23/25", type: "Jump",   change: "up" },
      { date: "10/21/25", type: "Sprint", change: "down" },
      { date: "10/18/25", type: "Sprint", change: "up" },
      { date: "10/15/25", type: "Jump",   change: "up" },
      { date: "10/15/25", type: "Sprint", change: "down" },
      { date: "10/10/25", type: "Jump",   change: "up" },
      { date: "10/08/25", type: "Jump",   change: "up" }
    ]
  },
  {
    id: 2,
    name: "Vincent Hispan",
    email: "hispanv@etown.edu",
    jersey: 11,
    team: "Basketball",
    year: "Junior",
    height: "6-5",
    weight: 195,
    major: "Business",
    prJump: 21.2,
    prJumpRank: "#1 All Time",
    prDash: 4.68,
    prDashRank: "#8 All Time",
    jumpHistory: [16.0, 16.4, 17.0, 17.2, 17.8, 18.3, 18.9, 19.5, 20.0, 20.7, 21.2],
    dashHistory: [4.80, 4.76, 4.72, 4.70, 4.68, 4.71, 4.69, 4.68, 4.67, 4.68, 4.68],
    recentTests: [
      { date: "10/22/25", type: "Jump",   change: "up" },
      { date: "10/20/25", type: "Sprint", change: "up" },
      { date: "10/16/25", type: "Jump",   change: "up" },
      { date: "10/14/25", type: "Sprint", change: "down" }
    ]
  },
  {
    id: 3,
    name: "Leif Hoffman",
    email: "carlsonj@etown.edu",
    jersey: 8,
    team: "Swim",
    year: "Sophomore",
    height: "6-1",
    weight: 175,
    major: "Biology",
    prJump: 17.7,
    prJumpRank: "#4 All Time",
    prDash: 4.82,
    prDashRank: "#22 All Time",
    jumpHistory: [13.0, 13.3, 13.8, 14.1, 14.6, 15.0, 15.5, 16.0, 16.5, 17.2, 17.7],
    dashHistory: [4.95, 4.92, 4.90, 4.88, 4.87, 4.85, 4.84, 4.83, 4.83, 4.82, 4.82],
    recentTests: [
      { date: "10/23/25", type: "Jump",   change: "up" },
      { date: "10/21/25", type: "Sprint", change: "up" },
      { date: "10/18/25", type: "Jump",   change: "down" }
    ]
  },
  {
    id: 4,
    name: "James Jackson",
    email: "jacksonj@etown.edu",
    jersey: 32,
    team: "Lacrosse",
    year: "Senior",
    height: "6-2",
    weight: 185,
    major: "Kinesiology",
    prJump: 18.4,
    prJumpRank: "#3 All Time",
    prDash: 4.71,
    prDashRank: "#11 All Time",
    jumpHistory: [14.0, 14.5, 15.0, 15.5, 16.0, 16.4, 16.9, 17.3, 17.8, 18.1, 18.4],
    dashHistory: [4.85, 4.82, 4.79, 4.77, 4.75, 4.74, 4.73, 4.72, 4.72, 4.71, 4.71],
    recentTests: [
      { date: "10/20/25", type: "Jump",   change: "up" },
      { date: "10/18/25", type: "Sprint", change: "down" },
      { date: "10/15/25", type: "Jump",   change: "up" }
    ]
  },
  {
    id: 5,
    name: "David Cronberg",
    email: "cronbergm@etown.edu",
    jersey: 15,
    team: "M Soccer",
    year: "Junior",
    height: "5-11",
    weight: 170,
    major: "Sports Management",
    prJump: 17.1,
    prJumpRank: "#5 All Time",
    prDash: 4.79,
    prDashRank: "#18 All Time",
    jumpHistory: [13.5, 13.9, 14.3, 14.7, 15.1, 15.5, 15.9, 16.3, 16.7, 17.0, 17.1],
    dashHistory: [4.90, 4.88, 4.87, 4.85, 4.84, 4.83, 4.82, 4.81, 4.80, 4.79, 4.79],
    recentTests: [
      { date: "10/21/25", type: "Sprint", change: "up" },
      { date: "10/19/25", type: "Jump",   change: "up" },
      { date: "10/16/25", type: "Sprint", change: "up" }
    ]
  }
];

// ── DASHBOARD METRICS ─────────────────────────────────────────
const DB_DASHBOARD_METRICS = [
  { label: "Men's Vertical Jump Avg (in)",    value: "17.8", change: "+1.2% month over month",  negative: false },
  { label: "Women's Vertical Jump Avg (in)",  value: "15.7", change: "+1.7% month over month",  negative: false },
  { label: "Men's 40-Yard Dash avg (s)",      value: "4.73", change: "-1.08% month over month", negative: true  },
  { label: "Women's 40-Yard Dash avg (s)",    value: "4.95", change: "+0.8% month over month",  negative: false }
];

// All-athlete monthly averages (Jul–May)
const DB_MONTHLY_LABELS = ["Jul","Aug","Sep","Oct","Nov","Dec","Jan","Feb","Mar","Apr","May"];
const DB_AVG_JUMP_HISTORY = [14.5, 14.8, 15.2, 15.1, 15.6, 15.9, 16.3, 16.8, 17.1, 17.5, 18.2];
const DB_AVG_DASH_HISTORY = [4.45, 4.42, 4.38, 4.40, 4.35, 4.37, 4.42, 4.38, 4.35, 4.30, 4.33];

// ── TEAM TABLES ───────────────────────────────────────────────
const DB_JUMP_TOTALS = [
  { team: "Basketball",   sessions: 26, change: "+14%" },
  { team: "Lacrosse",     sessions: 27, change: "+10%" },
  { team: "M Soccer",     sessions: 35, change: "+22%" },
  { team: "Softball",     sessions: 22, change: "+2%"  },
  { team: "W Soccer",     sessions: 27, change: "+12%" },
  { team: "W Basketball", sessions: 33, change: "+5%"  },
  { team: "Field Hockey", sessions: 16, change: "-3%"  }
];

const DB_DASH_TOTALS = [
  { team: "Basketball",   sessions: 15, change: "-7%"  },
  { team: "Lacrosse",     sessions: 12, change: "-3%"  },
  { team: "M Soccer",     sessions: 20, change: "-4%"  },
  { team: "Softball",     sessions: 14, change: "-10%" },
  { team: "W Soccer",     sessions: 18, change: "-7%"  },
  { team: "W Basketball", sessions: 22, change: "-6%"  },
  { team: "Field Hockey", sessions:  8, change: "-3%"  }
];

// ── SESSION LOG ───────────────────────────────────────────────
const DB_SESSION_LOG = [
  { source: "Evan Swanson",  team: "Baseball", type: "Jump"   },
  { source: "Leif Hoffman",  team: "Swim",     type: "Sprint" },
  { source: "Evan Swanson",  team: "Baseball", type: "Sprint" },
  { source: "Leif Hoffman",  team: "Swim",     type: "Jump"   },
  { source: "Leif Hoffman",  team: "Swim",     type: "Sprint" },
  { source: "Evan Swanson",  team: "Baseball", type: "Sprint" },
  { source: "Leif Hoffman",  team: "Swim",     type: "Jump"   }
];

// Session bar chart heights (inches per rep, current session)
const DB_SESSION_REPS = [
  { rep: "R1", height: 17.2 },
  { rep: "R2", height: 18.0 },
  { rep: "R3", height: 19.9 },
  { rep: "R4", height: 17.8 },
  { rep: "R5", height: 18.5 },
  { rep: "R6", height: 19.1 },
  { rep: "R7", height: 16.9 }
];
