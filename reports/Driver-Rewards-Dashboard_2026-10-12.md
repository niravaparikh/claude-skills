# UI comparison: Driver Rewards Dashboard (2026-10-12)

- Prototype: `C:\Users\NIRAVA\Documents\GitHub\AI-Boilerplate\Portfolio\service\logistics-supply-chain\fleet-management\dash-linen\driver-reward-dashboard\prototype\hi-fi\index.html` (runnable HTML/CSS/JS, single file) - never copied into the repo. Served read-only from its own folder on `127.0.0.1:8765` because `file://` is blocked; server stopped afterwards.
- Live site: https://d38gw103adeh1z.cloudfront.net/login (compared pages under `/admin`, logged in as Super-Admin by the user)
- Breakpoints: **1536 x 864 CSS px only** (user asked for the laptop's own size: 1920x1080 panel at 125% scaling). Other widths were not tested, so responsive behaviour is not covered.
- Pages compared: 7 matched (6 full comparisons + Floor Display, compared in its unpaired state only) / crashed live page: 1 (Manager Bonus) / prototype screens with no comparable live page: 3 (Driver PWA - role-gated, Driver Detail - needs a driver, Incidents <- Prolius - not a screen in the prototype) / live pages with no prototype counterpart: 6 (see "Live-only pages")
- Route discovery (added in the second pass): the live site answers HTTP 200 for every path (SPA fallback), so I read the route table from its own JS bundle (`/assets/index-BEOP8szt.js`). Live routes: `/login`, `/verify-otp`, `/set-password`, `/forgot-password`, `/display`, `/display/scroll`, `/display/vertical`, `/dashboard`, `/dashboard/league`, `/dashboard/profile`, `/admin`, `/admin/drivers/:id`, `/admin/drivers/:id/coaching`, `/admin/daily-input`, `/admin/reports`, `/admin/users`, `/admin/audit`, `/admin/manager-bonus`, `/admin/settings`, `/admin/settings/regions`, `/admin/queues`, `/management`, `/management/rankings`, `/management/insights/:id`.

**Important limitation: the live site has almost no data** (0 drivers, 0 incidents, 1 admin, 1 audit entry), while the prototype is seeded with 12 drivers. Anything that only renders with data (podium, driver cards, table rows, RAG counts) could not be compared and is listed under "Not verified". No test records were created, so nothing needed cleanup.

## Summary
| Severity | Count |
|---|---|
| Critical | 12 |
| Major | 19 |
| Minor | 14 |

## Screen mapping
| Prototype screen | Live page | Match basis | Confirmed by user |
|---|---|---|---|
| Scoreboard (`mgmt-sc`) | `/admin` | nav label + h1 "Driver Scoreboard" | No (exact title match, not asked) |
| Daily Input (`mgmt-input`) | `/admin/daily-input` | nav label + h1 "Daily Driver Input" | No |
| Quarterly Payout (`mgmt-rep`) | `/admin/reports` | nav label + h1 | No |
| Audit Log (`mgmt-audit`) | `/admin/audit` | nav label + h1 | No |
| Manager Bonus (`mgmt-manager`) | `/admin/manager-bonus` | nav label (live crashes) | No |
| User Management (`mgmt-users`) | `/admin/users` | nav label + h1 | No |
| Scoring Parameters (`mgmt-settings`) | `/admin/settings` | nav label + h1 | No |
| Floor Display shell (`shell-floor`) | `/display` | route in live bundle + same title "Driver Performance League" | No |
| Driver PWA shell (`shell-pwa`) | `/dashboard`, `/dashboard/league`, `/dashboard/profile` | route names match prototype tabs Score / League / Profile; **not reachable as Super-Admin** (redirects to `/login`) | - |
| Driver detail (`mgmt-det`, opened via `showDet`) | `/admin/drivers/:id` | route in bundle; needs a real driver id and there are 0 drivers | - |
| Incidents <- Prolius (`nav-log`) | none | in the prototype this link is a placeholder (`onclick="return false"`), not a screen, so there is nothing to compare | - |

## Findings
Raw computed-style dumps and diffs are in `Driver-Rewards-Dashboard_2026-10-12_evidence/raw/` (`proto-*.json`, `live-*.json`, `*-diff.txt`). Screenshots: `proto-<screen>.png` vs `live-<screen>.png` in the evidence folder. Font family matched on all compared text elements, so none is reported.

### Shell (every page) @ 1536px
| # | Severity | Category | Element | Prototype | Live | Evidence |
|---|---|---|---|---|---|---|
| 1 | Critical | Missing element | Header RAG counters | "8 Green / 3 Amber / 1 Red" in the top bar | absent | [proto](Driver-Rewards-Dashboard_2026-10-12_evidence/proto-scoreboard.png) / [live](Driver-Rewards-Dashboard_2026-10-12_evidence/live-scoreboard.png) |
| 2 | Critical | Missing element | Notification bell | present with unread dot | absent | same as #1 |
| 3 | Critical | Missing element | Role banner "Super Admin - Full access - user management..." | yellow strip under header | absent | same as #1 |
| 4 | Major | Missing element | Sidebar "Incidents <- Prolius" link | present, but a non-navigating placeholder in the prototype (`onclick="return false"`) | absent (live has "Review Queue" instead, see Live-only pages) | same as #1 |
| 5 | Major | Layout | Sidebar width / nav item box | items 209px wide at x=12 (sidebar ~233px) | items 235px wide at x=10 (sidebar 256px) | [raw diff](Driver-Rewards-Dashboard_2026-10-12_evidence/raw/scoreboard-diff.txt) |
| 6 | Major | Style | Active nav item | solid `rgb(56,130,246)` fill, shadow `rgba(56,130,246,.4) 0 4px 12px`, chevron | transparent fill with 3px left inset bar `rgb(47,123,255)`, no chevron | [proto](Driver-Rewards-Dashboard_2026-10-12_evidence/proto-scoreboard.png) / [live](Driver-Rewards-Dashboard_2026-10-12_evidence/live-scoreboard.png) |
| 7 | Minor | Typography/spacing | Nav items | 13.5px / line-height 20.25px / weight 500 / colour `rgba(255,255,255,.62)` / radius 8px / padding 11px 13px / margin-bottom 0 | 13px / 19.5px / weight 600 (active) / `rgba(255,255,255,.5)` / 9px / 10px 12px / 3px | [raw diff](Driver-Rewards-Dashboard_2026-10-12_evidence/raw/scoreboard-diff.txt) |
| 8 | Major | Branding | Sidebar logo / brand block | blue square icon, "Dash Linen Hire UK" + "PERFORMANCE-TO-ZERO" | monitor outline icon, "DASH LINEN HIRE UK" + "BESPOKE LAUNDRY SERVICE" | [proto](Driver-Rewards-Dashboard_2026-10-12_evidence/proto-scoreboard.png) / [live](Driver-Rewards-Dashboard_2026-10-12_evidence/live-scoreboard.png) |
| 9 | Major | Layout | Header content | "Fleet bonus remaining £343" plus user chip "Helen Marsden" with initials in blue | "Fleet avg: £0 remaining" and chip "Super-Admin" with dark circle | same as #1 |
| 10 | Major | Typography | Page `h1` (all 6 pages) | 20px / line-height 30px | 26px / 31.2px | [scoreboard](Driver-Rewards-Dashboard_2026-10-12_evidence/raw/scoreboard-diff.txt), [users](Driver-Rewards-Dashboard_2026-10-12_evidence/raw/users-diff.txt) |
| 11 | Minor | Colour | Primary blue | `rgb(56,130,246)` #3882F6 | `rgb(59,130,246)` #3B82F6 | [users diff](Driver-Rewards-Dashboard_2026-10-12_evidence/raw/users-diff.txt) |
| 12 | Minor | Style | Primary/secondary buttons | radius 7px, padding 10px, 0.8px border, transition `0.1s` | radius 8px, padding 8px, 0px border, `opacity 0.15s cubic-bezier(.4,0,.2,1)` | [users diff](Driver-Rewards-Dashboard_2026-10-12_evidence/raw/users-diff.txt) |
| 13 | Major | Console | CSP blocks inline fonts | none seen on prototype besides 1 unrelated entry | 8 errors on every page load: `font-src 'self'` blocks `data:font/woff2`/`woff` fonts | [console](Driver-Rewards-Dashboard_2026-10-12_evidence/raw/live-console-errors.txt) |

### Scoreboard (`/admin`) @ 1536px
| # | Severity | Category | Element | Prototype | Live | Evidence |
|---|---|---|---|---|---|---|
| 14 | Critical | Missing element | "Floor Display" button next to the view toggle | present | absent; live has an icon-only grid/list toggle instead of "List View" text button | [proto](Driver-Rewards-Dashboard_2026-10-12_evidence/proto-scoreboard.png) / [live](Driver-Rewards-Dashboard_2026-10-12_evidence/live-scoreboard.png) |
| 15 | Major | Layout | RAG filter chips | "All Drivers (12)", "Green (8)", "Amber (3)", "Red (1)" as buttons | single "All Drivers (0)" dropdown at far right | same as #14 |
| 16 | Major | Style | Period pills | radius 20px, 11px, weight 600, padding 12px; locked pills opacity 1, cursor pointer | pill radius (2.68e7px), 12px, weight 500, padding 16px; locked pills opacity 0.55, cursor default | [raw diff](Driver-Rewards-Dashboard_2026-10-12_evidence/raw/scoreboard-diff.txt) |
| 17 | Major | Style | Business segmented control | active label colour `rgb(56,130,246)`, radius 6px | active label `rgb(15,23,42)`, pill radius; inactive text `rgb(71,85,105)` vs `rgb(95,107,122)` | same as #16 |
| 18 | Minor | Content | Extra banner | none | "No Employee-of-the-Month candidate available for October 2026 yet." | [live](Driver-Rewards-Dashboard_2026-10-12_evidence/live-scoreboard.png) |
| 19 | Minor | Content | Quick stats panel | Avg Tele % 88%, Avg Deductions 2.1, Green 8... (seeded) | has "No Data" row instead of "Avg Deductions"; values empty (no data) | [proto](Driver-Rewards-Dashboard_2026-10-12_evidence/proto-scoreboard.png) / [live](Driver-Rewards-Dashboard_2026-10-12_evidence/live-scoreboard.png) |

### Daily Input (`/admin/daily-input`) @ 1536px
| # | Severity | Category | Element | Prototype | Live | Evidence |
|---|---|---|---|---|---|---|
| 20 | Critical | Content | Subtitle | "18 Apr 2026 - Fri - Sickness + complaints - all drivers default to All good. Incidents come from Prolius automatically - see Incidents tab. Manual entry below is for fallback only..." | "Mon, 12 Oct 2026 - every driver defaults to All good. Log..." (different wording; the pointer to the Incidents tab is gone; the prototype date is sample data) | [proto](Driver-Rewards-Dashboard_2026-10-12_evidence/proto-daily-input.png) / [live](Driver-Rewards-Dashboard_2026-10-12_evidence/live-daily-input.png) |
| 21 | Critical | Missing element | "Save today's input" button | present | absent | same as #20 |
| 22 | Major | Colour | "Log incident (manual override)" button | white background, red text `rgb(220,38,38)` | red background `rgb(220,38,38)`, white text; radius 8px vs 7px | [raw diff](Driver-Rewards-Dashboard_2026-10-12_evidence/raw/daily-input-diff.txt) |

### Quarterly Payout (`/admin/reports`) @ 1536px
| # | Severity | Category | Element | Prototype | Live | Evidence |
|---|---|---|---|---|---|---|
| 23 | Critical | Content | Table column header | "BONUS REMAINING" | "BASE POT" | [proto](Driver-Rewards-Dashboard_2026-10-12_evidence/proto-payout.png) / [live](Driver-Rewards-Dashboard_2026-10-12_evidence/live-payout.png) |
| 24 | Major | Layout | Summary cards | none | 4 stat cards (Total deducted, Average bonus remaining, Drivers with a score, Ready to export) plus "No closed quarters yet" section | same as #23 |
| 25 | Minor | Content | Export button / subtitle | "Export Q2 2026 Payout"; subtitle "Q2 2026 - Week 3 of 13 - End-of-quarter bonus settlement" | "Export Payout"; subtitle "End-of-quarter bonus settlement" | [raw diff](Driver-Rewards-Dashboard_2026-10-12_evidence/raw/payout-diff.txt) |
| 26 | Minor | Style | Table header cells (here and Audit, Users) | background `rgb(248,250,252)`, colour `rgb(107,114,128)`, cursor pointer | transparent, `rgb(100,116,139)`, cursor auto (prototype implies sortable; live sort not tested) | [payout diff](Driver-Rewards-Dashboard_2026-10-12_evidence/raw/payout-diff.txt) |

### Audit Log (`/admin/audit`) @ 1536px
| # | Severity | Category | Element | Prototype | Live | Evidence |
|---|---|---|---|---|---|---|
| 27 | Minor | Layout | Column widths | Timestamp 222, Actor 191, Action 268, Target 270, Before/after 288 | 162, 343, 94, 101, 530 | [proto](Driver-Rewards-Dashboard_2026-10-12_evidence/proto-audit.png) / [live](Driver-Rewards-Dashboard_2026-10-12_evidence/live-audit.png) |
| 28 | Minor | Content | Subtitle | prototype subtitle is injected by JS (`—` in source) | "Full cross-admin change log - for dispute resolution" | [live](Driver-Rewards-Dashboard_2026-10-12_evidence/live-audit.png) |

### Manager Bonus (`/admin/manager-bonus`) @ 1536px
| # | Severity | Category | Element | Prototype | Live | Evidence |
|---|---|---|---|---|---|---|
| 29 | Critical | Broken page | Whole page | "Manager Incentive Scorecard" with region select, bonus tiers (90%+ £600 ...) | "Unexpected Application Error! TypeError: Cannot read properties of undefined (reading 'find')" from `ManagerBonusPage-BzAtYXFe.js:1:647`. Possibly caused by the empty dataset, so re-test with data, but a crash on empty data is still a defect | [proto](Driver-Rewards-Dashboard_2026-10-12_evidence/proto-manager.png) / [live](Driver-Rewards-Dashboard_2026-10-12_evidence/live-manager.png) |

### User Management (`/admin/users`) @ 1536px
| # | Severity | Category | Element | Prototype | Live | Evidence |
|---|---|---|---|---|---|---|
| 30 | Critical | Content | Subtitle | "Super Admin only - Admins manually invited - Drivers auto-synced from **fleetmastr**" | "Admins manually invited - Drivers auto-synced from **Prolius**" (and "Super Admin only" dropped) | [proto](Driver-Rewards-Dashboard_2026-10-12_evidence/proto-users.png) / [live](Driver-Rewards-Dashboard_2026-10-12_evidence/live-users.png) |
| 31 | Major | Missing element | "Region" column | present | absent (columns: Name, Mobile, Role, Status, Last login, Actions) | same as #30 |
| 32 | Major | Missing element | "Suspend" action | Edit + Suspend per row | Edit only (on the single Super-Admin row; may be intentional for own account, re-test with a second admin) | same as #30 |
| 33 | Minor | Style | Table cells | text `rgb(50,55,60)`, padding 12px; "Last login" same colour | `rgb(15,23,42)`, 13px; "Last login" `rgb(100,116,139)` | [raw diff](Driver-Rewards-Dashboard_2026-10-12_evidence/raw/users-diff.txt) |

### Scoring Parameters (`/admin/settings`) @ 1536px
| # | Severity | Category | Element | Prototype | Live | Evidence |
|---|---|---|---|---|---|---|
| 34 | Critical | Content | Subtitle | "...Changes apply to the next scoring cycle - All changes are audit-logged" | "...Changes apply from now forward - All changes are audit-logged - **version undefined**" (unresolved variable shown to users) | [proto](Driver-Rewards-Dashboard_2026-10-12_evidence/proto-settings.png) / [live](Driver-Rewards-Dashboard_2026-10-12_evidence/live-settings.png) |
| 35 | Critical | Missing element | "Super Admin" badge beside Save button; yellow "Effective from save-time forward..." notice; blue "Locked for the current cycle (Q2 2026 - ends 30 Jun)" notice | all present | none present (text search of the page confirmed no "effective from") | same as #34 |
| 36 | Critical | Missing element | "Add custom deduction" section with Edit/Archive actions | present | absent (text search for "custom deduction" returned false) | raw: [settings diff](Driver-Rewards-Dashboard_2026-10-12_evidence/raw/settings-diff.txt) |
| 37 | Major | Content | Pilot-mode copy | "For the September pilot quarter... Turn off at the January launch" and "driver PWA" | "For the pilot quarter... Turn off at launch" and "driver app" | [proto](Driver-Rewards-Dashboard_2026-10-12_evidence/proto-settings.png) / [live](Driver-Rewards-Dashboard_2026-10-12_evidence/live-settings.png) |
| 38 | Major | Layout | Bonus period radios | selected "Calendar quarter" card highlighted, others unselected; period locked | no option selected; options are plain radios | same as #37 |
| 39 | Minor | Typography | Form field labels | letter-spacing 0.4px, colour `rgb(95,107,122)`, margin-bottom 6px | 0.3px, `rgb(71,85,105)`, 0px | [raw diff](Driver-Rewards-Dashboard_2026-10-12_evidence/raw/settings-diff.txt) |
| 40 | Minor | Typography | Native radio input | Arial 13.33px, `rgb(84,84,84)` | Roboto 14px, `rgb(15,23,42)` | same as #39 |
| 41 | Minor | Style | Save Changes button | enabled, `rgb(56,130,246)`, radius 7px | disabled (opacity 0.5; expected when no edits), `rgb(59,130,246)`, radius 8px | same as #39 |
| 42 | Minor | Layout | Live-only content | none | Region selector ("Combined (shared default) / Dash Linen / Just 4 Linen") and "Incentive running for this region" toggle | [live](Driver-Rewards-Dashboard_2026-10-12_evidence/live-settings.png) |

### Floor Display (`/display`) @ 1536px - live compared in its unpaired state
The live display shows "Screen not set up - Open this display once with its screen token to pair it". Pairing needs a token issued from Settings; creating one would be creating data I would have to track and revoke, so I did not. The prototype is shown with seeded data, so the podium and ranked list have nothing to compare against.

| # | Severity | Category | Element | Prototype | Live | Evidence |
|---|---|---|---|---|---|---|
| 43 | Major | Typography | Title "DRIVER PERFORMANCE LEAGUE" font family | `Roboto, system-ui, sans-serif`, 38px / 800 / letter-spacing 6px | `Catamaran, sans-serif`, 38px / 800 / 6px (size, weight, spacing, colour `rgb(226,232,240)` all match) | [proto](Driver-Rewards-Dashboard_2026-10-12_evidence/proto-floor-display.png) / [live](Driver-Rewards-Dashboard_2026-10-12_evidence/live-floor-display.png) |
| 44 | Major | Colour | Page background | flat dark grey (no gradient) | navy radial gradient `rgb(13,26,56)` -> `rgb(4,9,26)` with a star-field effect | same as #43 |
| 45 | Major | Content | Sub-heading line | "Q2 2026 - WEEK 3 OF 13 - LIVE - UPDATES EVERY 15 MIN" | "CURRENT QUARTER 13:27" (a clock) | same as #43 |
| 46 | Minor | Layout | Extra controls | none | "Scroll View" and "Vertical" links bottom right, telematics legend ("Green >= 85%, Amber 75-84%, Red < 75%") in the footer bar | [live](Driver-Rewards-Dashboard_2026-10-12_evidence/live-floor-display.png) |

Matched with no difference: brand line "DASH LINEN HIRE UK - BESPOKE LAUNDRY SERVICE" (Roboto 14px / 400 / 4px / `rgb(148,163,184)` / uppercase).

### Live-only pages (gaps: no prototype counterpart, so no severity)
| Live page | What it shows (empty data) | Evidence |
|---|---|---|
| `/admin/queues` Review Queue | "Nothing waiting" badge; three cards: Unmapped drivers, Unattributed journeys, Unclassified incidents, each 0 | [live](Driver-Rewards-Dashboard_2026-10-12_evidence/live-queues.png) |
| `/admin/settings/regions` Region mapping | table (Region, Prolius ID, Brand, Last changed), "No regions yet", Save button disabled | [live](Driver-Rewards-Dashboard_2026-10-12_evidence/live-regions.png) |
| `/management` Fleet Overview | read-only stat cards (Total/Green/Amber/Red), Both / Dash Linen / Just 4 Linen filter, driver table | [live](Driver-Rewards-Dashboard_2026-10-12_evidence/live-management.png) |
| `/management/rankings` Fleet Rankings | period buttons (Today ... This year), cross-company league table | [live](Driver-Rewards-Dashboard_2026-10-12_evidence/live-management-rankings.png) |
| `/display/scroll`, `/display/vertical` | floor-display variants, not opened (same pairing requirement) | - |
| `/admin/drivers/:id/coaching`, `/management/insights/:id` | need a driver id, not opened | - |

### Observations that are not prototype deviations
- **Quarter label vs date on live:** `/management/rankings` is headed "Q2 2026" but its own period line reads "2026-10-01 to 2026-12-31" (that is Q4), and the app header says "Q2 2026 - Week 3 of 13" on 12 Oct 2026. Either the labels are hard-coded or the quarter logic is off. Not scored because the prototype's "Q2 2026 - Week 3" is sample data.
- **Audit Log live row:** actor cell renders as "S( system (first super admin bootstrap)", which looks like a stray character in the avatar/initial markup. Not scored (one sample row).

## Not verified
- **Driver PWA** (prototype: Score / League / Profile in a phone frame): the live driver routes redirect a Super-Admin to `/login`, so they need a driver-role account. I did not log in as a driver and did not ask for driver credentials. Needs a driver session from you.
- **Floor Display populated state** (podium, ranked list, RAG bars) and the Scroll / Vertical variants: need a paired screen token.
- **Driver Detail and Coaching**: need at least one driver.
- **Data-dependent UI** (podium, driver cards/rank, RAG colours on real values, table rows, deductions, payouts, charts): live has no drivers or incidents, and I did not create any. Re-run after seeding or on a populated environment.
- **Hover, focus, active, disabled and keyboard behaviour, form validation, modals, sorting, transitions:** not exercised. Only static computed styles and screenshots were compared. Prototype interactions (`navM`, modals "Log incident", "Invite Admin", etc.) were not driven on either side.
- **Responsive behaviour:** only 1536x864 was compared (user choice). Other widths untested.
- **Accessibility:** contrast ratios, heading order, landmarks and tab order were not computed.
- Style extraction caps at 400 elements per page. Long pages (Settings) may have been truncated; #36 was confirmed with a separate full-text search.

## Test data created and cleaned up
None created, so nothing to delete. Cleanup: the prototype server (`python -m http.server 8765`) was started twice and stopped after the first pass; the second instance is stopped at the end of this pass (see chat). The Playwright browser and its tabs (opened by the session) were left open.
