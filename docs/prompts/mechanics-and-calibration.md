# Session brief: mechanics changes and score recalibration

Paste everything below the line into a new Claude Code session on the `mxtdnl/outbreak` repository.

---

## Context

OUTBREAK is a single-file browser simulation (`index.html`, no build step and no dependencies) of a 12-week public health crisis. It uses a two-group SEIR model with events, a forecast, and two scoring systems: the debrief composite, and the Class Scorecard of lobby indices with difficulty-specific grade bands. Read `docs/TECHNICAL_GUIDE.md` in full before changing anything. §4 (the weekly step), §6 (forecast), §7 (events), §10 (lobby scoring) and §14.2 (remaining simplifications) are the relevant sections.

An earlier session fixed the outright bugs and aligned the on-screen text with the model, without changing balance. This session makes the **mechanics** changes that were deliberately deferred because they alter balance. It then **rebuilds the calibration** of the lobby scorecard, because the existing anchors and grade bands will no longer be valid.

Per a comment in `index.html`, the existing calibration (`LOBBY_CAL`) was derived from about 60,000 simulated policies plus named reference strategies over 8 seeds. The harness that produced it is not in the repository, and its exact method and band-setting criteria are not recorded. Do not try to reverse-engineer or assume them. Define your own method, state it explicitly, and commit the harness so the calibration is reproducible.

## Part 1: mechanics changes

Make each change in `computeStep`, the event definitions or the forecast, as appropriate. Keep `computeStep` pure: it is reused by gameplay, the forecast and the reference strategies.

1. **Persistent variants.** A variant should permanently raise transmissibility, instead of causing a one-week surge.
   - Add a persistent component to the game state (for example `G.r0Variant`) that `computeStep` adds to R₀ every week from the variant's arrival onwards.
   - Border screening (`poeCum`) and modelling forewarning should reduce the persistent increase, as they reduce the surge now.
   - The response options should keep a distinct, meaningful role. For example, they could delay or reduce how quickly the variant becomes established, by phasing it in over a few weeks, rather than only scaling one week's effect.
   - In Variant Storm, a second variant should stack, with a sensible cap on total R₀.
   - Update the event card text to match.

2. **Vaccine immunity that wanes more slowly than natural immunity.**
   - Track vaccinated people separately from recovered people (for example `Vg`, `Vv` compartments), with a waning rate set per scenario, below `sc.waning`.
   - Make sure the population charts, the counters (decide whether vaccinated people show as "Recovered" or get their own counter), the exports and the debrief all handle the new compartment.
   - Update the lever text.

3. **Modelling accuracy that depends on level.** Lower modelling levels should give genuinely less accurate projections, not just a wider drawn band.
   - One approach is to perturb the projection inputs (for example R₀, compliance, IFR) by an error drawn from a **separate seeded RNG**. Size it by `0.30 / level`, and keep it fixed for a given week and level, so the projection does not flicker as sliders move.
   - The band should then reflect that real error.
   - The "exact next week" wording in the forecast strip must be removed or changed accordingly.
   - Do not let the forecast RNG disturb the event-schedule RNG sequence.

4. **Severity scaling for the strike and protest events.** `strike.mult` (currently fixed at 0.68) and the effects of the `protests` options (currently independent of `sev`) should scale with difficulty severity, as the other events do.

5. **Staffing and communications interacting with events.**
   - Medical Staff level should reduce the burnout event's fatality spike before the response is applied.
   - Communications level should reduce the misinformation event's compliance loss.
   - Restore wording to that effect on the event cards; earlier text claimed this, but it was removed because it was not modelled.

After Part 1, run a full game in the headless browser (Playwright is installed; `require('playwright')` works with no install step) to confirm there are no console errors and that every screen renders.

## Part 2: calibration harness

Build a reproducible calibration tool and use it to re-derive `LOBBY_CAL`.

### Requirements
- **Location:** `tools/calibrate.js`, run with `node tools/calibrate.js [--difficulty standard|hard|nightmare] [--n 60000] [--seeds 8]`. No npm dependencies.
- **Engine:** load the engine code directly from `index.html`, extracting the constants, events, `computeStep`, `freshComp`, `scenarioParams`, `buildEventSchedule`, `makeRng` and the scoring functions. Do **not** keep a copy of the model that could drift out of sync. If extraction is fragile, it is acceptable to refactor the engine into a clearly delimited `<script>` block or section that both the page and the tool read, as long as the app remains one self-contained file that opens in a browser with no build step.
- **Events included:** simulate the full game as a player experiences it: scheduled events from the seed, triggered events by the same rules as `pickEvent`, event responses, budget constraints and vaccine banking. Reference strategies in the debrief may remain event-free, but calibration must reflect real play.
- **Policy sampling.** Cover the space a class is likely to produce, not just uniform noise. Include:
  - uniform random weekly plans **that respect the weekly budget**;
  - "sticky" plans that change only occasionally, as real groups do;
  - rule-based plans (for example react to Rₑ or hospital load with lagged thresholds);
  - **named reference strategies**: do nothing; strict-only; the debrief's balanced strategy cut down to fit within budget; shield-focused; economy-first; suppression-first; and any others that represent distinct political choices;
  - a random choice among the available responses for each event, plus variants that always pick the cheapest or the most expensive.
- **Seeds:** run every policy across multiple seeds (default 8), as the original did.
- **Output:** for each difficulty, print the distribution (percentiles) of each lobby's raw quantity (vulnerable deaths, peak utilisation %, final and mean economy and satisfaction, spend fraction) and each resulting index. Then write the proposed `LOBBY_CAL` entry as JSON.

### Anchors and bands
- Set the `logIndex` anchors (`vd`, `util`) and `effK` from explicit, documented rules. For example, "best" could be the 1st percentile of named-good strategies and "worst" the 99th percentile of all sampled play; choose your own and justify it.
- Set the grade bands by an explicit rule as well, for example fixed percentiles of the government composite across sampled play. Apply the same bands to every lobby and the government, as now.
- **Calibrate Nightmare separately** (it currently falls back to Hard with an "indicative" warning). If that succeeds, set `exact: true` and remove the fallback warning for it.

### Acceptance checks (print these)
- Each lobby index uses most of its 0–100 range across sampled play; report the share of runs pinned at 0 or at 100, which should be small.
- The named "good" strategies grade A or better and do-nothing and strict-only grade D or F, in every scenario on each difficulty. If not, report it, and say whether the cause is the calibration or the mechanics.
- The geometric-mean government score still penalises capture: a strategy that maxes one lobby and zeroes another must score F.

## Part 3: integration and documentation
- Replace `LOBBY_CAL` in `index.html` with the new values, and update the comment to cite `tools/calibrate.js`, the command used, and the date.
- Recompute the reference-strategy outcome table in `docs/TECHNICAL_GUIDE.md` §9, and add a calibration section that describes the harness, the sampling, the anchor and band rules, and the acceptance-check results.
- Move the items you changed from §14.2 (remaining simplifications) into §14.1 (resolved), and update the formulas in §4, §6 and §7 and the glossary.
- Update `docs/FACILITATOR_GUIDE.md`: the grade-band table, event descriptions, forecast description, vaccine text, §18 and §19. Update `docs/USER_GUIDE.md` in plain English to match.
- Re-capture any screenshots in `docs/images/` whose content changed, using Playwright at `deviceScaleFactor: 2`. Large full-screen captures are stored as quality-85 JPEG at 2,000px width; element crops as PNG.
- Note in the guides that grades from before this change are **not comparable** with grades after it.

## Constraints
- Work on a new branch. Commit in logical steps (mechanics, harness, calibration, docs). Do not open a pull request unless asked.
- The app must remain a single `index.html` that opens directly in a browser with no build step or network dependency, other than the optional Google Fonts.
- Report any result you could not achieve, such as an acceptance check that fails, instead of adjusting the checks to pass.
