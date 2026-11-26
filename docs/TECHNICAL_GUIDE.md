# OUTBREAK — Technical Guide

This document specifies the simulation engine, every mechanic and constant, the event system, forecasting, scoring and the application architecture. All of it is taken from `index.html`. Line references are to that file at the time of writing. For gameplay guidance, see the [User Guide](USER_GUIDE.md) (participants) and the [Facilitator Guide](FACILITATOR_GUIDE.md) (instructors). Terms that are not plain English are defined in the [Glossary](#16-glossary).

---

## Contents

1. [Architecture](#1-architecture)
2. [Constants and parameter tables](#2-constants-and-parameter-tables)
3. [State model](#3-state-model)
4. [The weekly step: `computeStep`](#4-the-weekly-step-computestep)
5. [Decisions and costing](#5-decisions-and-costing)
6. [Forecasting engine](#6-forecasting-engine)
7. [Event system](#7-event-system)
8. [Week lifecycle](#8-week-lifecycle)
9. [Debrief scoring and reference strategies](#9-debrief-scoring-and-reference-strategies)
10. [Lobby scoring (Class Scorecard)](#10-lobby-scoring-class-scorecard)
11. [Exports](#11-exports)
12. [Rendering and display modes](#12-rendering-and-display-modes)
13. [Determinism and reproducibility](#13-determinism-and-reproducibility)
14. [Resolved discrepancies and remaining simplifications](#14-resolved-discrepancies-and-remaining-simplifications)
15. [Extending the simulation](#15-extending-the-simulation)
16. [Glossary](#16-glossary)

---

## 1. Architecture

- **One file**: `index.html`, containing the CSS (lines 9–550), the markup for all screens (552–930) and the script (932–2521). It has no dependencies, build step or server. The only external resource is Google Fonts, which have system fallbacks.
- **Screens** are `div.screen`s. Exactly one has `.active` at a time (`showScreen`, line 2467): `screen-briefing`, `screen-command`, `screen-event`, `screen-report`, `screen-debrief`, `screen-scorecard`.
- **Global state**: `G` (the current game, built by `init()`), `SETUP` (scenario, difficulty and lobby count chosen on the briefing), plus the display flags `CLASSMODE`, `DEBATEVIEW` and `SHOWSCORES`.
- **Pure core**: `computeStep(comp, econ, sat, week, d, sc, mods)` (line 1295) has no side effects and does not touch the DOM. Gameplay (`advanceWeek`), forecasting (`updateForecast`) and the reference strategies (`runStrategy`) all call it, so all three use exactly the same dynamics.
- **The DOM holds the decision state**: slider and toggle values are read back from the DOM by `getDecisions()` every time they are needed. Tiered policies and vaccine priority are kept in `G` (`G.lock`, `G.shield`, `G.finance`, `G.vaxPriority`). Neither is reset between weeks, so the plan persists.
- **Persistence**: only `localStorage['outbreak-mode']` (`solo` | `class`). Game state is not saved.

### Module map

| Section (code banner) | Key functions |
|---|---|
| CONSTANTS | `POP`, `SIGMA`, `GAMMA`, cost and effect arrays, `SCENARIOS`, `DIFFICULTIES`, `GRADE_THRESHOLDS` |
| CLASSROOM LOBBY SCORING | `LOBBY_CAL`, `LOBBIES`, `logIndex`, `gradeOf`, `computeLobbyScores` |
| SEEDED RNG | `makeRng` (mulberry32) |
| EVENT LIBRARY | `baseMods`, `EVENTS` |
| STATE | `scenarioParams`, `freshComp`, `totals`, `buildEventSchedule`, `init` |
| CORE MODEL | `computeStep` |
| DECISIONS | `getDecisions` |
| BUDGET + FORECAST | `onSlide`, `updateForecast` |
| ADVANCE WEEK / REPORT / EVENTS | `advanceWeek`, `buildReport`, `afterReport`, `pickEvent`, `enterWeek`, `showEventModal`, `chooseEventOption` |
| PANELS | `showCommand`, `updateStatsPanel`, `updateTicker`, `ADVISORS` |
| CHARTS | `setupCanvas`, `drawEpiChart`, `drawReffChart`, `drawEconSatChart`, `drawSeirChart`, `drawCompareChart` |
| DEBRIEF / SCORECARD / EXPORTS | `runStrategy`, `REF_STRATS`, `buildDebrief`, `buildScorecard`, `runRecord`, `exportCSV`, `exportJSON`, `copyScorecard` |
| DISPLAY MODE | `setMode`, `setDebate`, `applyViewState`, `updateProposalBar`, `updateLobbyBar` |

---

## 2. Constants and parameter tables

### Global (lines 936–946)

| Constant | Value | Meaning |
|---|---|---|
| `POP` | 500,000 | Total population |
| `VULN_FRAC` | 0.18 | Vulnerable share (90,000 people) |
| `SIGMA` | 1.2 /wk | E→I rate; mean latent period 1/σ ≈ 0.83 wk ≈ 5.8 days |
| `GAMMA` | 0.9 /wk | I→removed rate; mean infectious period 1/γ ≈ 1.11 wk ≈ 7.8 days |
| `SUBSTEPS` | 7 | Euler sub-steps per week (daily) |
| `CAP_BASE` | 1,000 | Base hospital beds |
| `HOSP_G` / `HOSP_V` | 0.05 / 0.22 | Fraction of currently infectious people needing a bed |
| `VAX_LEVEL` | 10,000 | Doses per vaccination level per week |
| `WEEKS` | 12 | Game length |
| `BASE_BUDGET` | $10M | Weekly budget before the difficulty multiplier |

### Resource unit costs (`RES_COST`, per level per week)

| perm | surge | staff | test | vax | epi | poe | comms |
|---|---|---|---|---|---|---|---|
| $1.5M | $0.6M | $1.0M | $0.6M | $1.0M | $0.5M | $0.5M | $0.5M |

### Policy arrays (indexed by tier)

| Array | Values | Use |
|---|---|---|
| `LOCK_COST` | 0, 1M, 2M, 4M | Weekly cost |
| `LOCK_FACTOR` | 1.00, 0.82, 0.65, 0.40 | Nominal transmission multiplier |
| `LOCK_ECON` | 0, 5, 9, 17 | Economy damage before relief |
| `LOCK_SAT` | 0, 3, 8, 13 | Satisfaction damage |
| `SHIELD_COST` | 0, 0.8M, 1.5M | |
| `SHIELD_EFF` | 0, 0.40, 0.68 | Cut in vulnerable susceptibility (× compliance) |
| `SHIELD_SAT` | 0, 1.0, 3.0 | |
| `SHIELD_ECON` | 0, 0.4, 0.9 | |
| `FIN_COST` | 0, 3M, 6M | |
| `FIN_RELIEF` | 0, 0.40, 0.72 | Fraction of restriction economic damage absorbed |
| `FIN_SAT` | 0, 1.5, 3.2 | Satisfaction gain |
| `FIN_COMPLY` | 0, 0.06, 0.11 | Added to compliance |

Toggles (hard-coded in `getDecisions` and `computeStep`):

| Toggle | Cost | Transmission | Economy | Satisfaction |
|---|---|---|---|---|
| Masks | $0.5M | ×(1 − 0.16·cf) | 0 | 0 |
| Schools | $1.0M | ×(1 − 0.11·cf) | −2 | −1.5 |
| Travel | $0.5M | ×0.94 | −1.5 | −0.5 |

### Scenarios (`SCENARIOS`)

| Key | R0 | ifrG | ifrV | waning (/wk) | vaxWeek | seed0 | extraVariant |
|---|---|---|---|---|---|---|---|
| `baseline` | 3.4 | 0.006 | 0.080 | 0.020 | 4 | 200 | — |
| `fast` | 4.5 | 0.012 | 0.140 | 0.012 | 5 | 280 | — |
| `slow` | 2.6 | 0.004 | 0.050 | 0.090 | 4 | 180 | — |
| `storm` | 3.2 | 0.007 | 0.090 | 0.030 | 4 | 200 | true |

### Difficulties (`DIFFICULTIES`)

| Key | budgetMult | r0Mult | sev | events |
|---|---|---|---|---|
| `standard` | 1.00 | 1.0 | 1.00 | 3 |
| `hard` | 0.80 | 1.1 | 1.25 | 4 |
| `nightmare` | 0.65 | 1.2 | 1.50 | 5 |

`scenarioParams()` returns a copy of the scenario with `R0 ← R0 × r0Mult`. `budgetMult` is applied in `init` (`G.budget`), and `sev` and `events` drive the event system.

---

## 3. State model

### Compartments (`G.comp`)
A two-group SEIRD-S model with the cumulative permanent bed count:

```
{ Sg, Eg, Ig, Rg, Dg,   // general group
  Sv, Ev, Iv, Rv, Dv,   // vulnerable group
  permBeds }            // cumulative permanent beds bought
```

These are **continuous** values (floats). Displays round them.

### Initial conditions (`freshComp`)
- Vulnerable = round(500,000 × 0.18) = 90,000; general = 410,000.
- Initial infectious = `seed0`, of which round(10%) are vulnerable. For example, the baseline has Ig = 180 and Iv = 20.
- E = R = D = 0, `permBeds` = 0.

### Game object (`G`, built in `init`)

| Field | Initial | Meaning |
|---|---|---|
| `sc`, `df`, `rng` | — | Scenario parameters (R0 already scaled), difficulty, seeded RNG |
| `week` | 1 | The week about to be played |
| `economy`, `satisfaction` | 100, 100 | Indices from 0 to 100, rounded to integers, used for every display and score |
| `econX`, `satX` | 100, 100 | The same indices unrounded. These are what is carried into the next step, so changes smaller than half a point accumulate |
| `vaxBank` | 0 | Event doses received before `vaxWeek`, held until vaccination opens |
| `vaxReleased` | 0 | Doses released from the bank this week (for the report) |
| `lock`, `shield`, `finance`, `vaxPriority` | 0, 0, 0, `'elderly'` | Tiered policy state |
| `budget` | `BASE_BUDGET × budgetMult` | Base weekly budget |
| `poeCum` | 0 | Sum of POE levels over completed weeks |
| `lastEpi` | 0 | Modelling level funded in the previous week |
| `lockStreak` | 0 | Consecutive completed weeks with lock ≥ 2 |
| `lastCondWeek` | −3 | Week of the last triggered event (for the cooldown) |
| `eventSchedule` | from `buildEventSchedule` | `{ week: eventId }` |
| `eventMods`, `eventCost`, `activeEvent` | `baseMods()`, 0, null | This week's event effects |
| `totalSpent` | 0 | Sum of weekly `d.total` |
| `forecast` | null | Array of projected points, or null |
| `history` | `[week 0 record]` | One record per completed week |

### History record
One record is pushed per week in `advanceWeek` (week 0 is a synthetic baseline):

```
{ week, S, E, I, R, D, newCases, newDeaths, hospLoad, hospCap, Reff, Rpolicy,
  economy, satisfaction, compliance,
  dec: { perm, surge, staff, test, vax, epi, poe, comms, lock, shield, finance,
         masks, schools, travel, vaxPriority, spend },
  event: { icon, title } | null }
```

The week-0 record sets `newCases = seed0`, `hospLoad = round(I × 0.1)`, `Reff = R0`, and `dec = null`. Because almost everyone is susceptible at the start, R0 is also the correct immunity-adjusted value for week 0.

---

## 4. The weekly step: `computeStep`

`computeStep(comp, econ, sat, week, d, sc, mods)` advances one week and returns new compartments, indices and diagnostics. `d` is a decisions object (§5) and `mods` holds event modifiers (§7).

### 4.1 Compliance

```
cf = clamp(0.55 + 0.09·comms + FIN_COMPLY[finance], 0.20, 1.00)
cf = clamp(cf · mods.complyMult, 0.15, 1.00)
```

Compliance before events:

| comms → | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| no support | 0.55 | 0.64 | 0.73 | 0.82 | 0.91 | 1.00 |
| partial | 0.61 | 0.70 | 0.79 | 0.88 | 0.97 | 1.00 |
| full | 0.66 | 0.75 | 0.84 | 0.93 | 1.00 | 1.00 |

### 4.2 Policy transmission multiplier and Rₑ

```
lockRed = (1 − LOCK_FACTOR[lock]) · cf · mods.lockEffMult
pf  = 1 − lockRed
pf ×= (1 − 0.16·cf)   if masks
pf ×= (1 − 0.11·cf)   if schools
pf ×= 0.94            if travel
pf ×= (1 − 0.055·test)
pf ×= (1 − 0.01·poe)
Reff = max(0.05, (R0 + mods.r0Delta) · pf)
```

Testing, travel restrictions and POE do not depend on compliance. Inside the step, this policy-adjusted `Reff` drives transmission (§4.5). It is returned as `Rpolicy`. The `Reff` the step **returns** and the interface shows also allows for immunity (§4.5, *susceptible share*). Both are rounded to 2 decimal places for output.

The best possible policy multiplier, at cf = 1 with every intervention at maximum, is 0.40 × 0.84 × 0.89 × 0.94 × 0.725 × 0.95 ≈ 0.19.

### 4.3 Capacity, shielding and fatality

```
cap       = max(1, (CAP_BASE + comp.permBeds + 250·perm + 300·surge) · mods.capMult)
shieldEff = SHIELD_EFF[shield] · cf
ifrBaseG  = sc.ifrG · (1 − 0.09·staff) · mods.ifrMult
ifrBaseV  = sc.ifrV · (1 − 0.07·staff) · mods.ifrMult
```

Beds ordered with `perm` this week count towards **this week's** capacity, as well as being added to `permBeds` for later weeks. Permanent capacity is a one-off order: after each week, `advanceWeek` resets the `r-perm` slider to 0, so beds are not bought again unless the player orders more (§5).

### 4.4 Super-spreader injection
If `mods.extraInf > 0`, before integration:

```
exG = min(Sg, extra · Sg/(Sg+Sv))
exV = min(Sv, extra · Sv/(Sg+Sv) · (1 − 0.5·shieldEff))
S → E by those amounts
```

### 4.5 SEIR integration (7 explicit-Euler sub-steps, dt = 1/7 wk)

For each sub-step:

```
N      = Sg+Eg+Ig+Rg + Sv+Ev+Iv+Rv                 (living population)
share += (Sg + Sv·(1 − shieldEff)) / N / 7          (susceptible share, averaged over the week)
λ      = Reff · γ · (Ig + Iv) / N · dt               (force of infection per sub-step)
newE_g = min(Sg, λ·Sg)
newE_v = min(Sv, λ·Sv·(1 − shieldEff))

demand = 0.05·Ig + 0.22·Iv                           (beds occupied)
capMet = min(1, cap / demand)
if capMet < 1:  om = 1 + 4·(1 − capMet)
                ifrG = min(0.10, ifrBaseG·om);  ifrV = min(0.30, ifrBaseV·om)

rem_x  = γ·dt·I_x          deaths_x = rem_x · ifr_x
inc_x  = σ·dt·E_x

S_x −= newE_x
E_x += newE_x − inc_x
I_x += inc_x − rem_x
R_x += rem_x − deaths_x
D_x += deaths_x
```

Notes:
- β = Reff·γ, so `Reff` acts as the basic reproduction number under the current policies. Mixing is **homogeneous**: both groups pool their infectiousness and face the same λ, except that shielding scales down the vulnerable group's susceptibility. Shielding does not reduce the vulnerable group's infectiousness.
- Fatality is applied **per removal**, so it is an infection fatality ratio taken at the end of the infectious period. The overflow multiplier is assessed separately in each sub-step.
- The overflow multiplier om rises from 1 (no overflow) through 3 (demand = 2 × capacity) towards 5 as capMet → 0. The caps apply **only during overflow**. The base IFR is never capped.
- `newCases` sums the S→E flows over the sub-steps. `newDeaths` sums the deaths.
- **Reported Rₑ** = policy `Reff` × the week's average susceptible share, where shielded vulnerable people count only in proportion to their remaining susceptibility. This is the average number of new infections each case actually causes that week, so a value above 1 means infections are growing. The relationship is approximate, because infections pass through E before I, and waning adds people back to S.
- `hospLoad` returned = **peak** sub-step demand. `capMet` returned = **worst** sub-step capMet.

### 4.6 Vaccination (once, after integration)

```
doses = week ≥ sc.vaxWeek ? vax·10,000 + mods.bonusVax : 0
elderly : V first (up to Sv), the rest to G
workers : G first (up to Sg), the rest to V
balanced: split in proportion to Sg : Sv
S → R
```

Unused doses (when the susceptible pool is exhausted) are lost. Vaccinated people join **R**, so they wane with the scenario's waning rate; the interface says so on the vaccination lever and in the model notes.

Event doses (`bonusVax`) arriving before `vaxWeek` are not given out early. `advanceWeek` adds them to `G.vaxBank`, and in the first week with `week ≥ vaxWeek`, `enterWeek` moves the bank into that week's `eventMods.bonusVax`. The event card and the weekly report say when doses are being held and when they are released.

### 4.7 Waning (once, after vaccination)

```
R_x → S_x at rate sc.waning (fraction per week)
```

All compartments are then clamped to ≥ 0. `permBeds ← comp.permBeds + 250·perm`.

### 4.8 Economy

```
restrictionEcon = LOCK_ECON[lock] + 2·schools + 1.5·travel + SHIELD_ECON[shield]
Δecon = −restrictionEcon · (1 − FIN_RELIEF[finance]) − newDeaths/90 − 0.25·poe
if lock = 0 and not schools and not travel and shield < 2:  Δecon += 1.2
economyX' = clamp(econ + Δecon, 0, 100)          economy' = round(economyX')
```

### 4.9 Satisfaction

```
restrictionSat = LOCK_SAT[lock] + 1.5·schools + 0.5·travel + SHIELD_SAT[shield]
Δsat = −restrictionSat + FIN_SAT[finance] + mods.satDelta
if lock > 0 or schools or travel or shield > 0:  Δsat += 0.5·comms
Δsat −= newDeaths/180
if capMet < 1:  Δsat −= 4
Δsat −= min(4, newCases/10,000)
satisfactionX' = clamp(sat + Δsat, 0, 100)       satisfaction' = round(satisfactionX')
```

Masks appear in neither the economy nor the satisfaction formula. The caller passes in the **unrounded** values from the previous step (`G.econX`, `G.satX`), so small weekly changes accumulate. The rounded values are used for display, history, scoring and the economic-collapse test (history economy = 0).

Across 4,000 random 12-week policies (4 scenarios × Standard/Hard × 500), changing from weekly rounding to carrying the unrounded value moved the Business and General Public lobby indices by a mean of −0.02 and +0.34 points (mean absolute change 0.53 and 0.61, largest ±3). Deaths were unchanged. That is too small to affect the calibrated grade bands (§10).

### 4.10 Return value

```
{ comp, economy, satisfaction (rounded), economyX, satisfactionX (unrounded), compliance: cf,
  S, E, I, R, D, newCases, newDeaths, hospLoad, hospCap: cap, capMet,
  Reff (immunity-adjusted, 2 dp), Rpolicy (policy-only, 2 dp), ifrEff: newDeaths / newCases }
```

---

## 5. Decisions and costing

`getDecisions()` (line 1406) reads:
- the sliders `r-perm … r-comms` (integers 0–5); `vax` is forced to 0 if `G.week < sc.vaxWeek`;
- the toggles `p-masks`, `p-schools`, `p-travel`;
- `G.lock`, `G.shield`, `G.finance`, `G.vaxPriority`.

From these it computes:

```
resCost = Σ level_k · RES_COST[k]
polCost = LOCK_COST[lock] + SHIELD_COST[shield] + FIN_COST[finance]
        + 0.5M·masks + 1.0M·schools + 0.5M·travel
total   = resCost + polCost + G.eventCost
```

Available budget = `G.budget + G.eventMods.bonusBudget`. After a week runs, the Permanent Capacity slider is reset to 0, so the order is not repeated by accident. The lever's label shows the number of beds already built (`G.comp.permBeds`). `advanceWeek` returns early if `total > budget`, and `onSlide` disables the button in that case. Budget does not roll over: `G.budget` is constant for the whole game.

`onSlide()` is the single re-render entry point for any control change. It runs: cost labels → budget box → header colour (amber below 20% remaining) → `updateForecast` → `updateStatsPanel` → `updateAdvisors` → `updateProposalBar`.

---

## 6. Forecasting engine

`updateForecast(d)` (line 1471).

### Gating
- `funded = G.lastEpi` (the level committed in the previous completed week). `pending = d.epi` (the live slider).
- If `funded < 1`, `G.forecast = null` and the strip shows a locked message.
- `G.lastEpi` is set in `advanceWeek` from the week just run. This one-week lag prevents a player from raising the slider, reading the projection and lowering it again at no cost.

### Projection

```
horizon = min(6, 2 + funded)          → 3, 4, 5, 6, 6
unc     = 0.30 / funded               → 0.30, 0.15, 0.10, 0.075, 0.06
for k = 1..horizon:
    r = k = 1 ? computeStep(comp, econ, sat, G.week, d,            G.sc, G.eventMods)
              : computeStep(comp, econ, sat, G.week−1+k, d with perm=0, G.sc, baseMods())
    econ, sat ← r.economyX, r.satisfactionX
    band_I  = r.I · unc · k
    band_ix = min(35, |proj − current|·unc·k + 4·unc·k)     (economy, satisfaction)
```

Point 0 is the current state with zero width. The first projected week is the week being planned, so it uses this week's event modifiers (the response already chosen). Later weeks assume no events, keep every other decision fixed, and do not repeat a one-off permanent-bed order.

### Properties
- The projection is **deterministic** and uses the same function as gameplay. If the plan is not changed, the next-week projection (k = 1) equals the actual outcome exactly, including weeks with events, because this week's event response is already known. This was checked by playing a full game in a headless browser, with and without events.
- Weeks beyond the first assume no further events, so projections further ahead are uncertain only because events may occur and the player may change the plan.
- The band is a **heuristic** width that grows with distance ahead. It is presented as "indicative", not as a statistical interval. The strip says the next-week figure is exact if no event fires and the plan is unchanged. Higher modelling levels buy a longer horizon and a narrower band; they do not change the central projection.
- `d.vax` is 0 before `vaxWeek`, so vaccination does not enter a projection made before vaccines unlock. Banked doses enter the first projected week once they are released.
- Outputs: `G.forecast[]` with `{week, I, lo, hi, economy, econLo, econHi, satisfaction, satLo, satHi, cumD, newDeaths, hospPct}`. These feed the strip, the hospital bar's "next wk" figure, the dashed lines and bands on the epidemic curve and the economy/satisfaction chart.

### Side effect: variant forewarning
`EVENTS.variant.build` checks `G.lastEpi ≥ 3` (§7.3).

---

## 7. Event system

### 7.1 Modifier object

```
baseMods() = { r0Delta:0, ifrMult:1, lockEffMult:1, complyMult:1, capMult:1,
               bonusVax:0, extraInf:0, satDelta:0, bonusBudget:0 }
```

`enterWeek` resets `G.eventMods` to `baseMods()` and `G.eventCost` to 0, then adds any banked vaccine doses (§4.6). An event response's `apply(m)` changes `G.eventMods`, and its `cost` sets `G.eventCost`. **All event effects last one week**, and the event text says so: the variant card describes a "one-week surge", and the burnout and misinformation cards state the effect "this week" and no longer claim that staffing or communications reduce them, since neither is modelled.

### 7.2 Scheduling (`buildEventSchedule`, line 1244)
Uses the seeded RNG:
1. A **variant** is placed in week `3 + floor(rng·3)`, which is week 3, 4 or 5.
2. Further events, up to `df.events` in total, are placed in distinct weeks chosen uniformly from `[3..11]`. Each event type is drawn uniformly from the pool `['variant','fatigue','misinfo','erosion','aid','vaxboost']`. For `storm`, a second `'variant'` entry is added at the front, giving 2/7 odds per draw. There is a guard of 100 iterations.
3. The same event type can occur more than once. Weeks 1, 2 and 12 never hold a scheduled event. (The code comment says "weeks 2..11"; the candidate list actually starts at 3.)

### 7.3 Triggered events (`pickEvent`, line 1644)
These are evaluated in `enterWeek` only if the week has no scheduled event and `G.week − G.lastCondWeek ≥ 2`. The conditions use `last = G.history[-1]` (the week just completed) and its `dec`. They are checked in this order, and the first match fires:

| Event | Condition |
|---|---|
| `protests` | `G.lockStreak ≥ 2` and `G.satisfaction < 55` |
| `superspreader` | `last.dec.test ≤ 1` and `last.I > previous I` and `last.I > 3000` |
| `strike` | `last.dec.staff ≤ 1` and `last.hospLoad / last.hospCap > 0.8` |

`G.lastCondWeek` is updated only for triggered events. Week 1 cannot trigger an event (its `last.dec` is null, so the comparisons are false).

### 7.4 Event definitions
Each event has `build(G, sev) → ctx` (body text and parameters) and `opts(ctx) → [{name, cost, note, apply(m)}]`. `sev = df.sev`.

| Event | `build` parameters | Options → modifier effect |
|---|---|---|
| **variant** | `poeMit = min(0.75, 0.06·poeCum)`; `base = (lastEpi ≥ 3 ? 1.1 : 1.4)·sev`; `eff = base·(1 − poeMit)` | $1.5M: r0Δ += 0.4·eff, sat −2 · $0.7M: r0Δ += 0.7·eff · free: r0Δ += eff |
| **fatigue** | `mult = 1 + 0.25·sev` | $1.2M: ifr ×1 · $0.5M: ifr ×(1 + (mult−1)/2) · free: ifr ×mult, sat −3 |
| **misinfo** | `drop = 0.28·sev` | $1.0M: comply ×(1 − 0.15·drop), sat −1 · $0.4M: comply ×(1 − 0.5·drop), sat −2 · free: comply ×(1 − drop), sat −6 |
| **erosion** | `drop = 0.26·sev` | $1.0M: lockEff ×(1 − 0.15·drop), sat +2 · $0.5M: lockEff ×(1 − 0.5·drop) · free: lockEff ×(1 − drop), sat −4 |
| **aid** | — | free: budget +$4M · free: budget +$3M, bonusVax +8,000 |
| **vaxboost** | — | $0.4M: bonusVax +22,000 · free: bonusVax +13,000 |
| **protests** | (sev unused) | free: sat −1, lockEff ×0.68 · free: sat −8, comply ×0.75 · $1.0M: sat −2 |
| **superspreader** | `extra = 9000·sev` | $1.2M: extraInf += 0.2·extra · $0.5M: extraInf += 0.5·extra, sat −2 · free: extraInf += extra |
| **strike** | `mult = 0.68` (not scaled by sev) | $1.2M: cap ×0.95 · $0.5M: cap ×0.85 · free: cap ×0.68, sat −4 |

`satDelta` from an event is added inside the satisfaction formula, so it is applied once, in the same week.

---

## 8. Week lifecycle

```
startGame()
  init(); reset the DOM controls; setLock/Shield/Finance(0); setVaxPriority('elderly')
  renderAdvisorShell(); enterWeek()

enterWeek()
  eventMods ← baseMods(); eventCost ← 0; activeEvent ← null
  if week ≥ vaxWeek and vaxBank > 0: eventMods.bonusVax += vaxBank; vaxBank ← 0
  if week ≥ vaxWeek: enable the vaccine slider
  ev ← pickEvent()
  ev ? showEventModal(ev) → chooseEventOption(opt) → showCommand()
     : showCommand()

showCommand()  → updateStatsPanel, updateTicker, applyViewState, onSlide, draw charts

advanceWeek()                                   (RUN WEEK)
  d ← getDecisions(); abort if over budget
  res ← computeStep(G.comp, G.econX, G.satX, G.week, d, G.sc, G.eventMods)
  if week < vaxWeek: vaxBank += eventMods.bonusVax
  poeCum += d.poe; lastEpi ← d.epi
  lockStreak ← (d.lock ≥ 2) ? lockStreak+1 : 0
  push the history record; totalSpent += d.total; commit comp, economy/satisfaction and econX/satX
  reset the Permanent Capacity slider to 0
  buildReport(); week++

afterReport()                                   (CONTINUE)
  week > 12 ? buildDebrief() : enterWeek()
```

`buildReport` compares against the previous history record. The "under-spent" note compares `d.total` with `0.5 × G.budget`, the base budget excluding any bonus.

---

## 9. Debrief scoring and reference strategies

### Composite (`buildDebrief`, line 2126)

```
deathScore = max(0, 100 − totalDeaths/100)
composite  = round(0.40·deathScore + 0.30·finalEconomy + 0.30·finalSatisfaction)
grade      = 'F — ECONOMIC COLLAPSE' if any history week had economy = 0
             else first GRADE_THRESHOLDS entry with composite ≥ min (87/72/55/36/18/0)
```

Other derived values: `overflows` = the number of history records with `hospLoad > hospCap` (week 0 is included, but it cannot overflow in practice); `peakWk` = the index of peak I in history, which equals the week number; `weakDim` = the first of deathScore, economy and satisfaction below 40, in that order.

### Reference strategies (`runStrategy`, `REF_STRATS`)
Each strategy runs `computeStep` for 12 weeks from `freshComp(scenarioParams())`, with `baseMods()` (**no events**) and **no budget check**.

| Strategy | Decisions |
|---|---|
| `nothing` | All zero |
| `strict` | lock 3, comms 1 |
| `balanced` | lock 2 (wk < 7) else 1; staff 2; test 2; comms 3; shield 1; poe 2 (wk ≤ 3) else 1; perm 1 (wk ≤ 3); surge 2 if bed demand at the start of the week > 1,200; epi 1; vax 3 from vaxWeek; masks; finance 1 (wk < 7) |

The `balanced` strategy costs **$14.0M in week 1**, more than any difficulty's budget. The debrief labels it "Balanced ref (no budget limit)", and the chart caption says the reference strategies exclude events and budget limits. Reference runs also carry unrounded economy and satisfaction between weeks (§4.9).

Reference outcomes (total deaths / final economy / final satisfaction), computed by running the engine headless:

| Scenario / difficulty | Do nothing | Strict-only | Balanced |
|---|---|---|---|
| baseline / standard | 26,948 / 0 / 0 | 990 / 0 / 0 | 65 / 29 / 47 |
| baseline / hard | 31,289 / 0 / 0 | 3,115 / 0 / 0 | 103 / 29 / 46 |
| baseline / nightmare | 33,823 / 0 / 0 | 6,892 / 0 / 0 | 163 / 28 / 44 |
| fast / standard | 46,075 / 0 / 0 | 20,774 / 0 / 0 | 893 / 20 / 32 |
| fast / hard | 46,828 / 0 / 0 | 29,375 / 0 / 0 | 1,432 / 14 / 23 |
| fast / nightmare | 47,244 / 0 / 0 | 35,948 / 0 / 0 | 2,206 / 5 / 7 |
| slow / standard | 5,395 / 47 / 35 | 95 / 0 / 0 | 15 / 30 / 49 |
| slow / hard | 10,053 / 0 / 1 | 162 / 0 / 0 | 21 / 30 / 48 |
| slow / nightmare | 14,952 / 0 / 0 | 270 / 0 / 0 | 30 / 30 / 48 |
| storm / standard | 24,665 / 0 / 0 | 619 / 0 / 0 | 59 / 29 / 48 |
| storm / hard | 30,465 / 0 / 0 | 1,751 / 0 / 0 | 91 / 29 / 47 |
| storm / nightmare | 34,135 / 0 / 0 | 4,543 / 0 / 0 | 141 / 28 / 45 |

In a "do nothing" run the economy reaches 0 because of deaths (−newDeaths/90), not restrictions. Storm differs from baseline only in its parameters here, because reference runs have no events.

---

## 10. Lobby scoring (Class Scorecard)

`computeLobbyScores()` (line 1038). Here `wk` is the set of history records with week > 0, and `cal = LOBBY_CAL[difficulty]`, falling back to `hard`.

### Calibration table

| Difficulty | `vd` (vulnerable deaths best/worst) | `util` (peak % best/worst) | `effK` | `bands` (A+, A, B, C, D) |
|---|---|---|---|---|
| standard | 30 / 12,000 | 25 / 800 | 0.85 | 90, 78, 62, 46, 30 |
| hard | 40 / 20,000 | 60 / 1,000 | 0.90 | 82, 70, 55, 40, 25 |
| nightmare | — (uses hard; `calIsExact()` = false) | | | |

According to the code comment, these anchors were calibrated empirically against about 60,000 simulated policies and named reference strategies over 8 seeds. The calibration harness is not part of the repository.

### Indices

```
logIndex(v, best, worst) = round(100 · (1 − (log10 v − log10 best)/(log10 worst − log10 best))),
                           with v clamped to [best, worst]

E = round(0.5·finalEconomy + 0.5·mean(economy over wk))
S = round(0.5·finalSatisfaction + 0.5·mean(satisfaction over wk))
P = logIndex(Dv, vd.best, vd.worst)
H = logIndex(max over wk of hospLoad/hospCap · 100, util.best, util.worst)
core = cbrt(E · S · P)
frac = clamp(totalSpent / (BASE_BUDGET · budgetMult · 12), 0, 1)
T = clamp(round(core · (2 − frac) · effK), 0, 100)
gov = round((Π active indices)^(1/n)),   n = 3 (E, S, P) or 5 (E, S, P, H, T)
spread = max − min of the active indices; "captured" if spread ≥ 45
```

Before week 1, the means fall back to the current values, and peak utilisation is 0, so H is 100.

`T` always uses the three core lobbies, even in 5-lobby mode. A zero in any active index makes `gov` 0.

### Grade (`gradeOf`)
Compares a value against `cal.bands`: ≥ b0 is A+, ≥ b1 A, ≥ b2 B, ≥ b3 C, ≥ b4 D, otherwise F. The same bands apply to every lobby and to the government.

### Decision-log "Served" heuristic (`buildScorecard`)

```
restrict = lock + schools + travel
served   = restrict ≥ 3 ? 'Vulnerable'
         : (shield > 0 and lock ≤ 1) ? 'Vuln·targeted'
         : restrict = 0 ? 'Business' : 'Mixed'
if finance > 0: served += '+Public'
```

Shielding is tested before the no-restriction case, so a week with shielding but no lockdown, school closure or travel restriction is labelled "Vuln·targeted".

---

## 11. Exports

`runRecord()` builds the canonical record:

```
{ exportedAt, scenario, difficulty, seed, weeks, population, lobbyCount,
  calibrated, gradeBands,
  scores: { <LobbyName>: { metric, index, grade } },
  government: { index, grade, captureSpread, strongest, weakest },
  raw: { finalEconomy, meanEconomy, finalSatisfaction, meanSatisfaction,
         totalDeaths, vulnerableDeaths, generalDeaths, peakHospitalUtilPct,
         totalSpent, budgetAvailable },
  weeks_detail: [ { week, event, decisions, economy, satisfaction, newCases,
                    newDeaths, cumulativeDeaths, infectious, Reff, hospitalUtilPct } ] }
```

- **JSON** — `JSON.stringify(runRecord(), null, 2)`.
- **CSV** — four blocks separated by blank lines: `SUMMARY`, `LOBBY SCORES` (with a Government row), `RAW OUTCOMES` (key,value) and `WEEK BY WEEK`. The week-by-week columns are: `week,event,lock,shield,finance,masks,schools,travel,perm,surge,staff,test,vax,vaxPriority,epi,poe,comms,spend,economy,satisfaction,newCases,newDeaths,cumulativeDeaths,infectious,Reff,hospitalUtilPct`. Fields containing a quote, comma or newline are quoted.
- **Filename** — `outbreak-<scenario key>-<difficulty key>-<seed with non-alphanumerics removed>.{json,csv}`.
- **Copy** — a fixed-width text summary through `navigator.clipboard`, falling back to `execCommand('copy')` and then `window.prompt`.
- **Print** — the `@media print` rules hide every screen except the scorecard and use a light, single-column layout.

---

## 12. Rendering and display modes

### Charts
All charts are drawn with the Canvas 2D API without a library. `setupCanvas` sizes each canvas to its parent at `devicePixelRatio`. The charts are redrawn on `showCommand`, on window resize, on a mode change and after every forecast update (epidemic curve only).

| Chart | Function | Notes |
|---|---|---|
| Epidemic curve | `drawEpiChart` | Dual axis (left: I and new cases; right: weekly deaths). The left maximum covers the forecast `hi`, and the right maximum covers forecast deaths. HOSP CAP line at `cap / rate`, where `rate` = (Ig·0.05 + Iv·0.22)/(Ig + Iv) from the current compartments, or the population-weighted 0.0806 when no one is infectious. The line therefore marks the infectious count at which beds would be full with the current mix of patients. Event icons; hover tooltip via `EPI_GEOM` (history only) |
| Rₑ | `drawReffChart` | Plots the immunity-adjusted Rₑ. Segments coloured by whether the mean of the two endpoints is above 1; R = 1 reference line |
| Economy and satisfaction | `drawEconSatChart` | Guide lines at 70 and 40, red zone below 30, forecast bands |
| Compartments | `drawSeirChart` | Stacked S, R, E, I, D as fractions of `POP` |
| Debrief comparison | `drawCompareChart` | The player's I curve against the three reference runs, which are recomputed on each draw |

### Classroom mode
`setMode('class')` sets `html[data-mode="class"]`. The CSS overrides:
- enlarge type and controls;
- hide `.res-fx`, `#advisors-sec` and `#model-notes`, and also `.pol-note` at heights of 950px or less;
- narrow the side panels on screens 1500px or 1150px wide or less.

The chart helpers `CFS` (font ×1.8), `CLW` (line ×1.9), `CDOT` (dot ×1.7), `CPAD` (padding) and `CC` (a high-contrast palette) scale the canvas output.

- **Debate view**: `html[data-view="debate"]` hides `.p-left` and `.p-right`. `updateProposalBar` renders a read-only summary of `getDecisions()`.
- **Scores view**: `updateLobbyBar` renders the live output of `computeLobbyScores()`.
- **Keys**: Ctrl/Cmd+Alt+C works globally. Bare `D` and `S` work only in class mode on the command screen, and are ignored while focus is in a text input, textarea or contenteditable element.

### Advisors and ticker
Both are pure functions of `G`, the current decisions and the last history record. They hold no state of their own. See `ADVISORS` (line 1772) and `updateTicker` (line 1751) for the exact conditions.

---

## 13. Determinism and reproducibility

- The **disease, economy and satisfaction model is fully deterministic**. `computeStep` uses no randomness.
- The RNG is **mulberry32**, seeded from a string hash of `"<seed>|<scenario>|<difficulty>"`. It is used **only** by `buildEventSchedule`.
- Given the same seed, scenario and difficulty, the **scheduled** events are identical. **Triggered** events and all outcomes depend on the player's decisions and event responses.
- Two runs with identical settings, decisions and event choices produce identical results, including identical exports apart from `exportedAt`.

---

## 14. Resolved discrepancies and remaining simplifications

### 14.1 Resolved
An earlier version of this guide listed eighteen discrepancies. Items 1–16 have been addressed, either by fixing the code or by correcting the on-screen text to describe what the code does. None of the changes alters the game's balance beyond the small rounding effect measured in §4.9, so the lobby calibration (§10) still applies.

| # | Area | Previous behaviour | Resolution |
|---|---|---|---|
| 1 | Rₑ display | Excluded immunity, so "above 1 — growing" could appear while infections fell | **Code.** Reported Rₑ = policy R × susceptible share (§4.5). The policy-only value is kept as `Rpolicy` |
| 2 | HOSP CAP line | Used an unweighted mean hospitalisation rate | **Code.** Weighted by the current infectious mix (§12) |
| 3 | Permanent capacity | The order repeated every week the slider stayed up | **Code.** The slider resets to 0 after each week, and the lever shows beds built (§5) |
| 4 | Variant duration | The text implied a lasting change | **Text.** The card describes a one-week surge, and the options refer to "this week's" surge |
| 5 | Vaccine immunity | Waning of vaccine immunity was not mentioned | **Text.** The vaccination lever and model notes say vaccine immunity wanes at the natural rate |
| 6 | Bonus doses | Given out before vaccination opened | **Code.** Banked until `vaxWeek` (§4.6) |
| 7 | Forecast vs events | The forecast ignored this week's event | **Code.** The first projected week uses this week's event modifiers (§6) |
| 8 | Forecast accuracy | The band implied uncertainty that the central projection does not have | **Text.** The strip calls the range "indicative" and says next week is exact if no event fires and the plan is unchanged; the modelling lever says higher levels mean "further ahead, narrower indicative range" |
| 9 | Event text vs mechanics | Burnout and misinformation claimed interactions with staffing and comms | **Text.** Those claims were removed |
| 11 | Reference "Balanced" | Over budget without saying so | **Text.** Labelled "no budget limit" on the debrief |
| 12 | Integer indices | Weekly rounding lost changes below ±0.5 | **Code.** Unrounded values carried between weeks (§4.9) |
| 13 | Economy recovery bonus | The rule was not stated | **Text.** The model notes state the exact condition |
| 14 | "Served" label | Shield-only weeks labelled Business | **Code.** Now labelled Vuln·targeted (§10) |
| 15 | Schedule comment | Said weeks 2..11 | **Code comment** corrected to 3..11 |
| 16 | `G.compliance` | Stored but never read | **Code.** Removed |

The permanent-capacity forecast was also corrected: projections no longer assume that a one-off bed order repeats in later weeks.

### 14.2 Remaining simplifications
These are deliberate simplifications of the model. They are described accurately in the interface and the guides, and changing them would alter game balance and require recalibration. A brief for that work is in [`docs/prompts/mechanics-and-calibration.md`](prompts/mechanics-and-calibration.md).

| # | Area | Behaviour |
|---|---|---|
| 4 | Variant | A one-week rise in R₀, not a permanent change in the pathogen |
| 5 | Vaccine immunity | Wanes at the same rate as natural immunity |
| 8 | Forecast | The band is a heuristic width; modelling level does not change how accurate the central projection is |
| 9 | Events | Staffing and communications do not interact with the burnout and misinformation events |
| 10 | Strike and protest severity | `strike.mult` is fixed at 0.68 and `protests` ignores `sev`, so neither scales with difficulty |
| 17 | Homogeneous mixing | One force of infection for both groups, with no age or contact structure; shielding only reduces vulnerable susceptibility |
| 18 | Hospital demand | Prevalence-based (beds = a fraction of current I), with no length of stay, so bed occupancy follows infections with no lag |
| — | Reference strategies | Run without events and without a budget limit |

### 14.3 Interface limitation noted while capturing screenshots
In Classroom mode at 1920×1080, Debate view (D) on its own fits the screen. With the live scoreboard (S) shown, the bottom row of three charts is slightly clipped, and with both D and S on together it is heavily clipped. This is a layout issue, not a model issue, and has not been changed.

---

## 15. Extending the simulation

- **New scenario**: add an entry to `SCENARIOS` with `name, tag, desc, R0, ifrG, ifrV, waning, vaxWeek, seed0` (and optionally `extraVariant`). The briefing renders it automatically. Lobby calibration is per difficulty, not per scenario, so check that the grades remain meaningful.
- **New difficulty**: add an entry to `DIFFICULTIES`. Without a matching `LOBBY_CAL` entry, the scorecard falls back to the Hard bands and shows a warning.
- **New event**: add it to `EVENTS` with `icon, kicker, title, build, opts` (and `positive` or `conditional` if relevant). For a scheduled event, add its key to the pool in `buildEventSchedule`. For a triggered event, add a condition to `pickEvent`. Effects must be expressed through the `baseMods()` fields, or through a new field that `computeStep` reads.
- **New resource or policy**: add the markup, a cost in `RES_COST` or the policy arrays, read it in `getDecisions`, apply it in `computeStep`, and add it to the history `dec`, the export key list `dk`, the proposal bar and the decision log.
- **Keep `computeStep` pure**: forecasting and the reference strategies depend on calling it repeatedly without side effects.

---

## 16. Glossary

The terms below appear in this guide or in the code, and are not plain English. Where a term has a general meaning and a more specific meaning in OUTBREAK, both are given.

### Epidemiology

| Term | Definition |
|---|---|
| **Pathogen** | A microorganism, such as a virus or bacterium, that causes disease. |
| **Transmission** | The passing of an infection from one person to another. |
| **Compartmental model** | A model that divides a population into groups ("compartments") by disease state and tracks how many people move between them over time. |
| **Compartment** | One of those groups, such as Susceptible or Infectious. In OUTBREAK each compartment exists separately for the general (`g`) and vulnerable (`v`) groups. |
| **SEIR / SEIRD-S** | The compartments used: **S**usceptible, **E**xposed, **I**nfectious, **R**ecovered (or Removed), **D**ead. The trailing "-S" means that recovered people return to Susceptible as immunity wanes. |
| **Susceptible (S)** | Able to catch the infection. |
| **Exposed (E)** | Infected but not yet able to infect others. |
| **Latent period** | The time spent in E. Here its average is 1/σ ≈ 5.8 days. Often loosely called the incubation period, although strictly incubation is the time until symptoms appear. |
| **Infectious (I)** | Able to infect others. |
| **Infectious period** | The time spent in I. Here its average is 1/γ ≈ 7.8 days. |
| **Recovered / Removed (R)** | No longer infectious and currently immune, through recovery or vaccination. |
| **Prevalence** | The number of people infected at a given moment (here, I). Contrast with **incidence**. |
| **Incidence** | The number of *new* infections in a period (here, `newCases` per week). |
| **R₀ (basic reproduction number)** | The average number of people one infectious person infects in a fully susceptible population with no interventions. A scenario parameter. |
| **Rₑ / Reff (effective reproduction number)** | The average number of people one infectious person infects under current conditions. **In this code**, the reported `Reff` = R₀ × the policy multiplier × the susceptible share, so it includes immunity. Inside `computeStep`, the name `Reff` refers to the policy-only value before that adjustment. |
| **Rpolicy** | R₀ after policy effects only, without allowing for immunity. Stored in history for reference. |
| **Susceptible share** | The fraction of the living population that can still be infected, counting shielded vulnerable people in proportion to their remaining susceptibility. |
| **Epidemic threshold** | R = 1. Above it, each case causes more than one new case on average, so infections grow; below it, they shrink. |
| **Susceptible depletion** | The slowing of an outbreak as fewer people remain who can be infected. In the model this enters through the S/N term in the force of infection. |
| **Force of infection (λ)** | The rate at which susceptible people become infected, here per sub-step. Proportional to Rₑ, γ and the fraction of the population that is infectious. |
| **β (transmission rate)** | The rate of infectious contacts per infectious person. In this model β = Rₑ × γ. |
| **σ (sigma)** | The rate at which exposed people become infectious, per week (1.2). |
| **γ (gamma)** | The rate at which infectious people stop being infectious, per week (0.9). |
| **Homogeneous mixing** | The assumption that everyone is equally likely to contact everyone else, with no structure by age, household or place. |
| **IFR (infection fatality ratio)** | The fraction of infected people who die. `ifrG` and `ifrV` are the IFRs of the general and vulnerable groups. |
| **Waning immunity** | The loss of immunity over time. Here a fixed fraction (`sc.waning`) of R returns to S each week. |
| **Clinically vulnerable** | People at high risk of severe disease. In OUTBREAK, the 18% group with higher hospitalisation and fatality rates. |
| **Shielding** | Measures to reduce the exposure of vulnerable people specifically. Modelled as a cut in the vulnerable group's susceptibility. |
| **Compliance** | The fraction of the population following guidance. Here `cf`, from 0.15 to 1.0, which scales the effect of lockdown, masks, school closures and shielding. |
| **Variant** | A genetically changed form of the pathogen. Here, a one-week increase in R₀. |
| **Super-spreader cluster** | A single event or setting that causes an unusually large number of infections. Here, a one-off transfer of people from S to E. |
| **Surge capacity** | Temporary extra hospital capacity. Here, beds that last one week. |
| **Port of entry (POE)** | A border crossing point, such as an airport or seaport, where arrivals can be screened. |
| **Contact tracing** | Identifying and isolating people who have been in contact with a case. Combined with testing as one lever. |
| **Epidemic curve** | A chart of infections over time. |
| **Peak** | The point at which prevalence is highest. |
| **Overflow** | Hospital bed demand exceeding capacity. Raises fatality in the model. |
| **Endemic** | A disease that persists in a population at a steady or recurring level, rather than in a single outbreak. |

### Mathematics and numerical methods

| Term | Definition |
|---|---|
| **Unrounded (exact) value** | A number kept with its decimal places instead of being rounded to a whole number. |
| **Explicit Euler method** | A simple way to step equations forward in time: the change over a short step is the current rate multiplied by the step length. |
| **Sub-step / dt** | One of the 7 short (daily) steps inside each simulated week. `dt` is the step length, 1/7 of a week. Smaller steps reduce numerical error. |
| **Numerical stability** | Whether a step-by-step calculation stays well-behaved (for example, never producing negative people). Daily sub-steps are used for this reason. |
| **Deterministic** | Producing the same output every time for the same input; involving no randomness. |
| **Stochastic** | Involving randomness. |
| **Ensemble** | Many runs of a stochastic model, used to estimate a range of outcomes. The forecast band is *not* an ensemble. |
| **Horizon** | How many weeks ahead a forecast projects. |
| **Uncertainty band** | The shaded range around a forecast line. Here a heuristic width, `unc` × weeks ahead, not a statistical interval. |
| **Heuristic** | A rule of thumb chosen to be reasonable, not derived from data or theory. |
| **Multiplier / factor** | A number that another quantity is multiplied by. For example, ×0.65 reduces transmission to 65%. |
| **Clamp** | To force a value into a range, replacing anything below the minimum with the minimum and anything above the maximum with the maximum. Written clamp(x, min, max). |
| **Index (0–100)** | A score on a fixed scale. The Economy and Satisfaction indices start at 100. |
| **Arithmetic mean** | The ordinary average: sum divided by count. |
| **Geometric mean** | The nth root of the product of n values. A low value pulls it down far more than it would an arithmetic mean, and any zero makes it zero. |
| **Cube root (cbrt)** | The geometric mean of three values is the cube root of their product. |
| **Logarithmic (log) scale / log10** | A scale on which each step represents multiplication by a fixed factor (×10 for log10), not addition. Used where values range over orders of magnitude, such as deaths. |
| **`logIndex`** | The function that maps a raw value onto 0–100 on a log scale between a "best" and "worst" anchor. |
| **Anchor** | A fixed reference value that a scale is pinned to, for example the raw value that maps to 100. |
| **Calibration** | Choosing anchors and grade bands so that scores spread sensibly across the range of plausible play. |
| **Composite score** | A single score combined from several. The debrief composite is 40% deaths, 30% economy and 30% satisfaction. |
| **Weighting** | The relative importance given to each part of a composite. |
| **Spread** | The difference between the largest and smallest value in a set. |
| **dp** | Decimal places. |
| **Σ / Π** | Sum of / product of a series of values. |

### Scoring and game design

| Term | Definition |
|---|---|
| **Lobby** | An interest group that scores the government on one outcome: Business, General Public, Vulnerable, Healthcare or Treasury. |
| **Capture / capture spread** | "Capture" is when a government serves one interest group at others' expense. "Capture spread" is the gap between the best- and worst-scoring lobbies; 45 or more is reported as captured. |
| **Non-substitutable** | Unable to compensate for a poor score in one area with a high score in another. This is the property the geometric mean gives the government score. |
| **Grade band** | The score range that maps to a letter grade. |
| **Reference strategy** | A fixed, scripted plan run on the same scenario for comparison in the debrief. |
| **Scheduled event** | An event whose week is fixed at the start of the game by the seed. |
| **Triggered (conditional) event** | An event that fires when the game state meets a condition. |
| **Cooldown** | The minimum gap (2 weeks) between triggered events. |
| **Modifier (`mods`)** | A temporary adjustment that an event applies to the model for one week, such as `r0Delta` or `capMult`. |
| **Severity (`sev`)** | The difficulty's multiplier for event strength. |
| **Cumulative** | Added up over time. `poeCum` is the total of POE levels over all completed weeks. |
| **Bank (vaccine doses)** | A store of event doses received before vaccination opens, released in the first vaccine week. |
| **One-off order** | A purchase made once, not repeated each week. Permanent Capacity works this way. |
| **Lag / in arrears** | Taking effect later than when paid for. Modelling funded this week produces a forecast next week. |

### Software and web

| Term | Definition |
|---|---|
| **HTML / CSS / JavaScript** | The languages of web pages: structure, presentation and behaviour respectively. OUTBREAK is all three in one file. |
| **DOM (Document Object Model)** | The browser's live, in-memory representation of the page. The game reads slider values from the DOM. |
| **Canvas / Canvas 2D API** | An HTML element, and the browser's built-in drawing commands for it, used to draw the charts. |
| **devicePixelRatio** | The ratio of physical screen pixels to layout pixels. Canvases are sized by it so charts are sharp on high-resolution screens. |
| **Pure function** | A function that depends only on its inputs and has no side effects. `computeStep` is pure. |
| **Side effect** | Any change a function makes outside its return value, such as altering global state or the page. |
| **Global state** | Variables readable and writable from anywhere in the program, such as `G` and `SETUP`. |
| **Headless** | Run without a browser or display, here by extracting the model code and running it in Node.js to produce the reference table in §9. |
| **Node.js** | A program for running JavaScript outside a browser. |
| **RNG (random number generator)** | A function producing a sequence of numbers that appear random. |
| **Pseudo-random** | Generated by a deterministic algorithm, so the same starting point always gives the same sequence. |
| **Seed** | The starting value of a pseudo-random generator. Here, the text typed on the briefing screen combined with the scenario and difficulty. |
| **Hash** | A function that turns input, such as text, into a fixed-size number. Used to turn the seed text into the RNG's starting value. |
| **mulberry32** | The specific small, fast pseudo-random algorithm used. |
| **localStorage** | Browser storage that persists between visits for one website. Used only to remember the display mode. |
| **Clipboard API / `execCommand`** | Browser features for copying text. `execCommand` is the older fallback. |
| **JSON** | JavaScript Object Notation: a structured text format for data, readable by most programming languages. |
| **CSV** | Comma-separated values: a plain-text table format that spreadsheets can open. |
| **Media query (`@media`)** | A CSS rule that applies only under conditions such as screen height or printing. |
| **Data attribute (`data-mode`, `data-view`)** | A custom attribute on an HTML element. CSS rules key off these to switch the Classroom and Debate layouts. |
| **Tooltip** | A small box shown when hovering over an element, here over the epidemic curve. |
