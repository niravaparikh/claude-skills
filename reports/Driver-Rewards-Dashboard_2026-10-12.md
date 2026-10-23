# UI comparison: Driver Rewards Dashboard (2026-10-12)

- Prototype: `C:\Users\NIRAVA\Documents\GitHub\AI-Boilerplate\Portfolio\service\logistics-supply-chain\fleet-management\dash-linen\driver-reward-dashboard\prototype\hi-fi\index.html` (runnable HTML/CSS/JS, single file) - never copied into the repo. Served read-only from its own folder because `file://` is blocked; the server was stopped afterwards.
- Live site: https://d38gw103adeh1z.cloudfront.net/login (pages under `/admin`, logged in as Super-Admin by the user)
- Breakpoints: **1536 x 864 CSS px only** (the user's laptop: 1920x1080 panel at 125% scaling). Other widths were not tested.
- Pages compared: 8 (7 admin screens plus Floor Display in its unpaired state) / not comparable: Driver PWA, Driver detail / live-only pages: 6.
- Rules applied: this version applies the static-vs-dynamic rules in the skill's `references/dynamic-content.md`. Names, money, counts, dates, periods, empty/disabled/unselected states and prototype-only devices are **not** reported as deviations. They are listed under "Excluded", and anything that might be conditional is under "Needs confirmation" with no severity.
- Method note: the classification was done on the evidence already captured. The first pass truncated element text to 60 characters, so wording findings were re-checked against full text from the prototype source and the live page. Style extraction was capped at 400 elements per page.
- Route discovery: the live site answers HTTP 200 for every path (SPA fallback), so the route table was read from its JS bundle. Routes: `/login`, `/verify-otp`, `/set-password`, `/forgot-password`, `/display`, `/display/scroll`, `/display/vertical`, `/dashboard`, `/dashboard/league`, `/dashboard/profile`, `/admin`, `/admin/drivers/:id`, `/admin/drivers/:id/coaching`, `/admin/daily-input`, `/admin/reports`, `/admin/users`, `/admin/audit`, `/admin/manager-bonus`, `/admin/settings`, `/admin/settings/regions`, `/admin/queues`, `/management`, `/management/rankings`, `/management/insights/:id`.

**Data parity:** the live site has almost no data (0 drivers, 0 incidents, 1 admin, 1 audit entry) and the prototype is seeded with 12 drivers. Data-driven UI could not be compared and is under "Not verified". No test records were created, so nothing needed cleanup.

## Summary
Confirmed findings only (static content or tokens, same state, measured on both sides).

| Severity | Count |
|---|---|
| Critical | 7 |
| Major | 11 |
| Minor | 13 |

Also: 10 items under Needs confirmation, 19 differences excluded as dynamic or state-dependent, 5 observations. None of those are counted above.

## Screen mapping
| Prototype screen | Live page | Match basis | Confirmed by user |
|---|---|---|---|
| Scoreboard (`mgmt-sc`) | `/admin` | nav label + h1 "Driver Scoreboard" | No (exact title match) |
| Daily Input (`mgmt-input`) | `/admin/daily-input` | nav label + h1 "Daily Driver Input" | No |
| Quarterly Payout (`mgmt-rep`) | `/admin/reports` | nav label + h1 | No |
| Audit Log (`mgmt-audit`) | `/admin/audit` | nav label + h1 | No |
| Manager Bonus (`mgmt-manager`) | `/admin/manager-bonus` | nav label (live page crashes) | No |
| User Management (`mgmt-users`) | `/admin/users` | nav label + h1 | No |
| Scoring Parameters (`mgmt-settings`) | `/admin/settings` | nav label + h1 | No |
| Floor Display (`shell-floor`) | `/display` | route in live bundle + same title "Driver Performance League" | No |
| Driver PWA (`shell-pwa`) | `/dashboard`, `/dashboard/league`, `/dashboard/profile` | route names match Score / League / Profile; **not reachable as Super-Admin** (redirects to `/login`) | - |
| Driver detail (`mgmt-det`) | `/admin/drivers/:id` | route in bundle; needs a driver id and there are 0 drivers | - |
| Incidents <- Prolius (`nav-log`) | none | a placeholder link in the prototype (`onclick="return false"`), not a screen | - |

## Findings (confirmed)
Raw computed-style dumps and diffs are in `Driver-Rewards-Dashboard_2026-10-12_evidence/raw/`. Screenshots: `proto-<screen>.png` vs `live-<screen>.png`. Font family matched on all other compared text, so none is reported.

### Shell (every page) @ 1536px
| # | Severity | Category | Element | Prototype | Live | Evidence |
|---|---|---|---|---|---|---|
| 1 | Critical | Missing element | Notification bell (static button in the prototype header) | present with unread dot | absent | [proto](Driver-Rewards-Dashboard_2026-10-12_evidence/proto-scoreboard.png) / [live](Driver-Rewards-Dashboard_2026-10-12_evidence/live-scoreboard.png) |
| 2 | Major | Layout | Sidebar width / nav item box | items 209px wide at x=12 (sidebar ~233px) | items 235px wide at x=10 (sidebar 256px) | [raw diff](Driver-Rewards-Dashboard_2026-10-12_evidence/raw/scoreboard-diff.txt) |
| 3 | Major | Style | Active nav item | solid `rgb(56,130,246)` fill, shadow `rgba(56,130,246,.4) 0 4px 12px`, chevron | transparent fill with 3px left inset bar `rgb(47,123,255)`, no chevron | [proto](Driver-Rewards-Dashboard_2026-10-12_evidence/proto-scoreboard.png) / [live](Driver-Rewards-Dashboard_2026-10-12_evidence/live-scoreboard.png) |
| 4 | Minor | Typography/spacing | Nav items (inactive) | 13.5px / line-height 20.25px / colour `rgba(255,255,255,.62)` / radius 8px / padding 11px 13px / margin-bottom 0 | 13px / 19.5px / `rgba(255,255,255,.5)` / 9px / 10px 12px / 3px | [raw diff](Driver-Rewards-Dashboard_2026-10-12_evidence/raw/scoreboard-diff.txt) |
| 5 | Major | Branding | Sidebar logo icon and brand block styling (estimated from screenshots) | blue rounded-square icon, brand name in mixed case | monitor outline icon, brand name in capitals | [proto](Driver-Rewards-Dashboard_2026-10-12_evidence/proto-scoreboard.png) / [live](Driver-Rewards-Dashboard_2026-10-12_evidence/live-scoreboard.png) |
| 6 | Major | Typography | Page `h1` (all admin pages) | 20px / line-height 30px | 26px / 31.2px | [scoreboard](Driver-Rewards-Dashboard_2026-10-12_evidence/raw/scoreboard-diff.txt), [users](Driver-Rewards-Dashboard_2026-10-12_evidence/raw/users-diff.txt) |
| 7 | Minor | Colour | Primary blue | `rgb(56,130,246)` #3882F6 | `rgb(59,130,246)` #3B82F6 | [users diff](Driver-Rewards-Dashboard_2026-10-12_evidence/raw/users-diff.txt) |
| 8 | Minor | Style | Buttons | radius 7px, padding 10px, 0.8px border, transition `0.1s` | radius 8px, padding 8px, 0px border, `opacity 0.15s cubic-bezier(.4,0,.2,1)` | [users diff](Driver-Rewards-Dashboard_2026-10-12_evidence/raw/users-diff.txt) |
| 9 | Minor | Content | Sidebar "Quick stats" row set | Avg Tele %, Avg Deductions, Green, Amber, Red | Avg Tele %, Green, Amber, Red, No Data (labels only; values are data) | [proto](Driver-Rewards-Dashboard_2026-10-12_evidence/proto-scoreboard.png) / [live](Driver-Rewards-Dashboard_2026-10-12_evidence/live-scoreboard.png) |

### Scoreboard (`/admin`) @ 1536px
| # | Severity | Category | Element | Prototype | Live | Evidence |
|---|---|---|---|---|---|---|
| 10 | Critical | Missing element | "Floor Display" button beside the view toggle (static markup in the prototype) | present | absent | [proto](Driver-Rewards-Dashboard_2026-10-12_evidence/proto-scoreboard.png) / [live](Driver-Rewards-Dashboard_2026-10-12_evidence/live-scoreboard.png) |
| 11 | Minor | Layout | View toggle | text button "List View" with icon | icon-only grid/list toggle | same as #10 |
| 12 | Major | Style | Period pills (Q2 2026, Q1 2026, ...) | radius 20px, font 11px, weight 600, padding 0 12px | pill radius (2.68e7px), 12px, weight 500, padding 0 16px | [raw diff](Driver-Rewards-Dashboard_2026-10-12_evidence/raw/scoreboard-diff.txt) |
| 13 | Major | Style | Business segmented control | active label `rgb(56,130,246)`, radius 6px; inactive text `rgb(95,107,122)` | active label `rgb(15,23,42)`, pill radius; inactive text `rgb(71,85,105)` | same as #12 |

### Daily Input (`/admin/daily-input`) @ 1536px
| # | Severity | Category | Element | Prototype | Live | Evidence |
|---|---|---|---|---|---|---|
| 14 | Minor | Copy | Subtitle wording (date excluded as data) | "... all drivers default to All good. Incidents come from Prolius automatically - see Incidents tab. Manual entry below is for fallback only (customer phoned before Prolius record landed)." | "... Every driver defaults to All good. Log sickness, absences and complaints below. Incidents will sync from Prolius - add one manually only as a fallback." | [proto](Driver-Rewards-Dashboard_2026-10-12_evidence/proto-daily-input.png) / [live](Driver-Rewards-Dashboard_2026-10-12_evidence/live-daily-input.png) |
| 15 | Major | Colour | "Log incident (manual override)" button | white background, red text `rgb(220,38,38)` | red background `rgb(220,38,38)`, white text; radius 8px vs 7px | [raw diff](Driver-Rewards-Dashboard_2026-10-12_evidence/raw/daily-input-diff.txt) |

### Quarterly Payout (`/admin/reports`) @ 1536px
| # | Severity | Category | Element | Prototype | Live | Evidence |
|---|---|---|---|---|---|---|
| 16 | Critical | Content | Table column header | "BONUS REMAINING" | "BASE POT" | [proto](Driver-Rewards-Dashboard_2026-10-12_evidence/proto-payout.png) / [live](Driver-Rewards-Dashboard_2026-10-12_evidence/live-payout.png) |
| 17 | Major | Content | Summary card labels (cards 3 and 4; the values are data) | "Incidents (from Prolius)", "Nil Defect Compliance" | "Drivers with a score", "Ready to export" | same as #16 |
| 18 | Minor | Style | Table header cells (also Audit, Users) | background `rgb(248,250,252)`, colour `rgb(107,114,128)`, cursor pointer | transparent, `rgb(100,116,139)`, cursor auto | [payout diff](Driver-Rewards-Dashboard_2026-10-12_evidence/raw/payout-diff.txt) |
| 19 | Minor | Style | Export button | text only | download icon before the text | same as #16 |

### Manager Bonus (`/admin/manager-bonus`) @ 1536px
| # | Severity | Category | Element | Prototype | Live | Evidence |
|---|---|---|---|---|---|---|
| 20 | Critical | Broken page | Whole page | "Manager Incentive Scorecard" renders | "Unexpected Application Error! TypeError: Cannot read properties of undefined (reading 'find')" from `ManagerBonusPage-BzAtYXFe.js:1:647`. It may be triggered by the empty dataset, but crashing on empty data is itself a defect | [proto](Driver-Rewards-Dashboard_2026-10-12_evidence/proto-manager.png) / [live](Driver-Rewards-Dashboard_2026-10-12_evidence/live-manager.png) |

### User Management (`/admin/users`) @ 1536px
| # | Severity | Category | Element | Prototype | Live | Evidence |
|---|---|---|---|---|---|---|
| 21 | Major | Missing element | "Region" column (static `th` in the prototype) | present | absent (live columns: Name, Mobile, Role, Status, Last login, Actions) | [proto](Driver-Rewards-Dashboard_2026-10-12_evidence/proto-users.png) / [live](Driver-Rewards-Dashboard_2026-10-12_evidence/live-users.png) |
| 22 | Minor | Style | Table cells | text `rgb(50,55,60)`, padding 12px | `rgb(15,23,42)`, padding 13px | [raw diff](Driver-Rewards-Dashboard_2026-10-12_evidence/raw/users-diff.txt) |

### Scoring Parameters (`/admin/settings`) @ 1536px
| # | Severity | Category | Element | Prototype | Live | Evidence |
|---|---|---|---|---|---|---|
| 23 | Critical | Content | Subtitle | no version text | "... All changes are audit-logged - **version undefined**" (an unresolved variable shown to users) | [proto](Driver-Rewards-Dashboard_2026-10-12_evidence/proto-settings.png) / [live](Driver-Rewards-Dashboard_2026-10-12_evidence/live-settings.png) |
| 24 | Minor | Copy | Subtitle wording | "Changes apply to the next scoring cycle" | "Changes apply from now forward" | same as #23 |
| 25 | Critical | Missing element | Yellow notice "Effective from save-time forward. Changes apply to the next scoring run; deductions already applied ... are NOT retroactively recalculated ..." (static in the prototype) | present | absent (page text search found no "effective from") | same as #23 |
| 26 | Critical | Missing element | "Add custom deduction" section with Edit/Archive actions (static container and button in the prototype) | present | absent (page text search found no "custom deduction") | [settings diff](Driver-Rewards-Dashboard_2026-10-12_evidence/raw/settings-diff.txt) |
| 27 | Minor | Typography | Form field labels | letter-spacing 0.4px, colour `rgb(95,107,122)`, margin-bottom 6px | 0.3px, `rgb(71,85,105)`, 0px | [raw diff](Driver-Rewards-Dashboard_2026-10-12_evidence/raw/settings-diff.txt) |
| 28 | Minor | Typography | Native radio input | Arial 13.33px, `rgb(84,84,84)` | Roboto 14px, `rgb(15,23,42)` | same as #27 |
| 29 | Minor | Style | Save Changes button (colour and shape only; enabled/disabled state excluded) | `rgb(56,130,246)`, radius 7px | `rgb(59,130,246)`, radius 8px | same as #27 |

### Floor Display (`/display`) @ 1536px (live in its unpaired state)
The live display shows "Screen not set up" and needs a pairing token from Settings. Creating one would create data to track and revoke, so it was not done. Only static styling was compared.

| # | Severity | Category | Element | Prototype | Live | Evidence |
|---|---|---|---|---|---|---|
| 30 | Major | Typography | Title "DRIVER PERFORMANCE LEAGUE" font family | `Roboto, system-ui, sans-serif` (38px / 800 / 6px / `rgb(226,232,240)`) | `Catamaran, sans-serif` (size, weight, spacing and colour match) | [proto](Driver-Rewards-Dashboard_2026-10-12_evidence/proto-floor-display.png) / [live](Driver-Rewards-Dashboard_2026-10-12_evidence/live-floor-display.png) |
| 31 | Major | Colour | Page background | flat dark grey | navy radial gradient `rgb(13,26,56)` to `rgb(4,9,26)` with a star-field effect | same as #30 |

Matched with no difference: brand line (Roboto 14px / 400 / 4px / `rgb(148,163,184)` / uppercase).

## Needs confirmation (not counted)
No severity until the question is answered.

| # | Screen | Element | Prototype | Live | Why unconfirmed | Question |
|---|---|---|---|---|---|---|
| N1 | Shell | Header RAG counters ("8 Green / 3 Amber / 1 Red") | shown | absent | rendered by JS from driver data; may be hidden at zero | Should the counters show with zero drivers? |
| N2 | Shell, Settings | Role banner ("Super Admin - Full access - ...") and the "Super Admin" badge beside Save | shown | absent | driven by the prototype's persona table (`roleDesc`), a demo device; live is also Super-Admin | Is a role banner part of the product? |
| N3 | Shell | User chip styling (blue initials circle with outlined pill vs dark circle) | blue | dark | avatar colour may be per user or per role | Is the avatar colour fixed or per user? |
| N4 | Shell | Sidebar "Incidents <- Prolius" | placeholder link (`return false`) | absent; live has "Review Queue" | not a real screen in the prototype | Is Review Queue its replacement? |
| N5 | Users | Subtitle | "Super Admin only - ... auto-synced from **fleetmastr**" | "... auto-synced from **Prolius**" | the prototype says Prolius on every other screen | Which source name is right, and is "Super Admin only" still wanted? |
| N6 | Scoreboard | RAG filter | chips "All / Green / Amber / Red" | one "All Drivers" dropdown | the dropdown was not opened | Does the dropdown list the same options? |
| N7 | Scoreboard | Locked period pills (Q1, 6 months, 12 months) | opacity 1, cursor pointer | opacity 0.55, cursor default | live pills are disabled; may be state, not design | Should locked periods look disabled? |
| N8 | Users | "Suspend" row action | Edit + Suspend | Edit only | only the signed-in Super-Admin row exists; may be intentional for your own account | Is Suspend hidden for your own account? |
| N9 | Daily Input | "Save today's input" button | present | absent | live has no drivers; the button may need rows | Does the button appear once drivers exist? |
| N10 | Shell | Brand tagline | "PERFORMANCE-TO-ZERO" | "BESPOKE LAUNDRY SERVICE" | tenant branding may be configuration | Is the tagline configurable? |

## Excluded as dynamic or state-dependent
Not deviations. Class codes are in the skill's `references/dynamic-content.md`.

| Screen | Element | Prototype | Live | Class |
|---|---|---|---|---|
| Shell | user chip name | Helen Marsden | Super-Admin | I |
| Shell | "Fleet bonus remaining" | £343 | "Fleet avg: £0 remaining" | D |
| Shell, Payout | header and subtitle period ("Q2 2026 - Week 3 of 13") | shown | shown in header, absent in the Payout subtitle | T |
| Shell | Quick stats values (88%, 2.1, 8, 3, 1) | seeded | 0 / empty | D |
| Scoreboard | podium, driver cards, rank cards | 12 drivers | none | D |
| Scoreboard | RAG counts "(12) (8) (3) (1)" | seeded | "(0)" | D |
| Scoreboard | "No Employee-of-the-Month candidate ... October 2026" banner | none | shown | T/D |
| Daily Input | subtitle date | 18 Apr 2026 · Fri | Mon, 12 Oct 2026 | T |
| Payout | export button label | "Export Q2 2026 Payout" | "Export payout" | T |
| Payout | summary card values and captions (£1,080, 14, 86%, "across all 12 drivers") | seeded | £0.00, 0 of 0 | D |
| Payout | card 1 label "Total Deducted (Q2 to date)" | period named | "Total deducted this quarter" | T |
| Payout | export button disabled and 50% opacity | enabled | disabled | ST |
| Payout, Audit, Users | table rows | seeded | empty or one row | D |
| Audit | column widths | 222/191/268/270/288 | 162/343/94/101/530 | D (auto-sized to content) |
| Users | row values (names, phones, last login) | seeded | Super-Admin row | D |
| Settings | Save Changes disabled | enabled | disabled (nothing edited) | ST |
| Settings | no bonus-period option selected; "Locked for the current cycle (Q2 2026 - ends 30 Jun)" notice and highlighted card | calendar quarter selected, locked | none selected, no notice | ST |
| Settings | pilot-mode copy ("September pilot quarter ... January launch") | dated | generic | T |
| Floor Display | sub-heading ("Q2 2026 - Week 3 of 13 - Live ...") and missing podium/list | seeded | "Current quarter" and clock, unpaired | ST/T |

## Live-only pages (gaps, no prototype counterpart)
| Live page | What it shows (empty data) | Evidence |
|---|---|---|
| `/admin/queues` Review Queue | "Nothing waiting" badge; cards Unmapped drivers, Unattributed journeys, Unclassified incidents | [live](Driver-Rewards-Dashboard_2026-10-12_evidence/live-queues.png) |
| `/admin/settings/regions` Region mapping | table (Region, Prolius ID, Brand, Last changed), "No regions yet" | [live](Driver-Rewards-Dashboard_2026-10-12_evidence/live-regions.png) |
| `/management` Fleet Overview | read-only stat cards, Both / Dash Linen / Just 4 Linen filter, driver table | [live](Driver-Rewards-Dashboard_2026-10-12_evidence/live-management.png) |
| `/management/rankings` Fleet Rankings | period buttons, cross-company league table | [live](Driver-Rewards-Dashboard_2026-10-12_evidence/live-management-rankings.png) |
| `/display/scroll`, `/display/vertical` | floor-display variants, not opened (same pairing requirement) | - |
| `/admin/drivers/:id/coaching`, `/management/insights/:id` | need a driver id, not opened | - |

## Observations (not prototype deviations, not counted)
- **Font loading blocked by CSP:** every live page load logs 8 errors, `font-src 'self'` blocking `data:font/woff2` and `woff` fonts ([console log](Driver-Rewards-Dashboard_2026-10-12_evidence/raw/live-console-errors.txt)). The prototype loads no such fonts, so this is a live-environment issue.
- **Quarter label vs date:** `/management/rankings` is headed "Q2 2026" but its period line reads 2026-10-01 to 2026-12-31 (Q4), and the app header says "Q2 2026 - Week 3 of 13" on 12 Oct 2026. The labels may be hard-coded or the quarter logic may be off.
- **Audit Log row:** the actor cell renders "S( system (first super admin bootstrap)", which looks like a stray character in the avatar markup.
- **Live-only content on matched pages:** a Region selector and an "Incentive running for this region" toggle on Settings, "Scroll View" / "Vertical" links and a telematics legend on the Floor Display. These are additions, not omissions.
- **Prototype toolbar:** the prototype's top bar ("Hi-fi v2", Management / Floor Display / Driver PWA tabs, "Prolius (configure)", "Custom build") is a demo device and was ignored.

## Not verified
- **Driver PWA** (Score / League / Profile): the live driver routes redirect a Super-Admin to `/login`, so they need a driver-role session. No driver credentials were requested.
- **Floor Display populated state** (podium, ranked list, RAG bars) and the Scroll / Vertical variants: need a paired screen token.
- **Driver Detail and Coaching:** need at least one driver.
- **Data-dependent UI** (podium, driver cards, RAG values, table rows, deductions, payouts, charts): live has no drivers or incidents. Re-run on a populated environment or with marked test records.
- **Behaviour** (hover, focus, keyboard, form validation, modals, sorting, transitions): not exercised.
- **Responsive behaviour:** only 1536x864 was compared.
- **Accessibility:** contrast, heading order, landmarks and tab order were not computed.
- **Collapsed controls:** the live "All Drivers" dropdown was not opened (see N6).

## Test data created and cleaned up
None created, so nothing to delete. Local prototype servers I started were stopped. The Playwright browser and its tabs were left open.
