# OUTBREAK — Facilitator Guide

This guide is for the **instructor, teacher or facilitator** who runs OUTBREAK, the public health crisis simulation, with a group. It explains every screen, control, decision and score in enough depth for you to answer participants' questions, to steer discussion, and to interpret results.

Companion documents:
- [User Guide](USER_GUIDE.md): a plain-English guide for the **participants** who play. Hand it out before or during the session.
- [Technical Guide](TECHNICAL_GUIDE.md): the equations, constants and scoring formulas, with a full glossary.

### Facilitator quick start

1. Open `index.html` in a desktop browser on the machine connected to the projector ([§2](#2-running-the-simulation)).
2. Choose a **scenario**, **difficulty**, **seed** and **lobby count** ([§4](#4-screen-1--briefing-and-setup)). For your first session, use Novel Respiratory / Standard / seed `meridian` / 5 lobbies.
3. Switch to **Classroom** display ([§16](#16-classroom-projection-mode)).
4. Assign participants to lobbies, and brief them using the [User Guide](USER_GUIDE.md) ([§20](#20-planning-and-running-a-session)).
5. Run the 12 weeks, alternating **Debate view** (D) for argument with the controls for committing the agreed plan.
6. Use the Debrief and Class Scorecard for the closing discussion, and export the results ([§21](#21-assessment-and-collating-results)).

Before the session, read [§19](#19-model-behaviours-to-pre-empt). It lists the behaviours of the model that most often confuse a room.

---

## Contents

1. [What the simulation is](#1-what-the-simulation-is)
2. [Running the simulation](#2-running-the-simulation)
3. [The flow of a game](#3-the-flow-of-a-game)
4. [Screen 1 — Briefing and setup](#4-screen-1--briefing-and-setup)
5. [Screen 2 — Command Centre](#5-screen-2--command-centre)
6. [Resource sliders (left panel)](#6-resource-sliders-left-panel)
7. [Policy levers (right panel)](#7-policy-levers-right-panel)
8. [The weekly budget](#8-the-weekly-budget)
9. [Reading the centre panel](#9-reading-the-centre-panel)
10. [Forecasting](#10-forecasting)
11. [Advisors, situation panel and model notes](#11-advisors-situation-panel-and-model-notes)
12. [Screen 3 — Events](#12-screen-3--events)
13. [Screen 4 — Weekly report](#13-screen-4--weekly-report)
14. [Screen 5 — Debrief](#14-screen-5--debrief)
15. [Screen 6 — Class Scorecard](#15-screen-6--class-scorecard)
16. [Classroom (projection) mode](#16-classroom-projection-mode)
17. [Keyboard shortcuts](#17-keyboard-shortcuts)
18. [What participants commonly miss](#18-what-participants-commonly-miss)
19. [Model behaviours to pre-empt](#19-model-behaviours-to-pre-empt)
20. [Planning and running a session](#20-planning-and-running-a-session)
21. [Assessment and collating results](#21-assessment-and-collating-results)

---

## 1. What the simulation is

A novel pathogen has reached **Meridian City (population 500,000)**. You are the Emergency Public Health Director. For **12 simulated weeks** you set resources and policies within a fixed weekly budget, then run the week and see the consequences.

The population has two groups:

| Group | Share | Size | Why it matters |
|---|---|---|---|
| General | 82% | 410,000 | Most infections; lower hospitalisation and fatality |
| Clinically vulnerable | 18% | 90,000 | Hospitalised about 4× as often, and roughly 12–13× more likely to die per infection |

You are judged on three things that pull against each other: **deaths**, the **Economy Index** and **Public Satisfaction**. In the classroom scorecard, these become separate interest groups ("lobbies") that each grade the government.

Decisions **bind**: once a week has run, it cannot be undone. There is no undo or save, so if the room disagrees about a week, settle it before anyone presses RUN WEEK.

---

## 2. Running the simulation

OUTBREAK is a single file, `index.html`, with no build step and no server. Open it in a current desktop browser (Chrome, Edge, Firefox or Safari). An internet connection is only needed for the Google Fonts; if they are blocked, the interface falls back to system fonts and remains fully usable.

The only thing stored between sessions is your display-mode choice (Solo or Classroom), kept in the browser's local storage. A game in progress is **not** saved; reloading the page loses it.

---

## 3. The flow of a game

```
Briefing ──► [Event, if any] ──► Command Centre ──► RUN WEEK ──► Weekly Report ──┐
                ▲                                                                │
                └──────────────────────── next week (weeks 1–12) ◄───────────────┘
                                                                                 │
                                                     after week 12 ──► Debrief ──► Class Scorecard
```

Each week:

1. **An event may fire** before you see the controls. You must choose a response.
2. **You set your plan** in the Command Centre: sliders, policy tiers and toggles.
3. **You press RUN WEEK.** The model simulates seven days.
4. **The Weekly Report** summarises what happened. Press CONTINUE.

Your settings **carry over** from week to week. Nothing resets automatically. If you set a strict lockdown in week 2, it remains in place, and keeps costing money, until you change it.

---

## 4. Screen 1 — Briefing and setup

### Situation briefing
The opening text explains the premise. It has no controls.

### Scenario
Choose one of four pathogens. Each has its own transmissibility (R₀), fatality rates, rate at which immunity wears off ("waning"), the week vaccines become available, and the number of people infected at the start.

| Scenario | Tag | R₀ | Fatality (general / vulnerable) | Waning | Vaccine from | What it tests |
|---|---|---|---|---|---|---|
| **Novel Respiratory** | BASELINE | 3.4 | 0.6% / 8% | Slow (2%/wk) | Week 4 | A balanced, standard outbreak |
| **Fast & Deadly** | SEVERE | 4.5 | 1.2% / 14% | Very slow (1.2%/wk) | Week 5 | Speed of response; hospital overflow |
| **Slow Burn / Endemic** | PERSISTENT | 2.6 | 0.4% / 5% | Fast (9%/wk) | Week 4 | Reinfection waves; sustained management |
| **Variant Storm** | VOLATILE | 3.2 | 0.7% / 9% | Moderate (3%/wk) | Week 4 | Variant shocks; rewards early border screening |

In Variant Storm, the variant event is more likely to be drawn again in the random event schedule.

### Difficulty

| Difficulty | Weekly budget | R₀ multiplier | Event severity | Scheduled events |
|---|---|---|---|---|
| **Standard** | $10.0M | ×1.0 | ×1.0 | 3 |
| **Hard** | $8.0M | ×1.1 | ×1.25 | 4 |
| **Nightmare** | $6.5M | ×1.2 | ×1.5 | 5 |

The R₀ multiplier applies to the scenario's R₀. For example, Novel Respiratory on Nightmare has R₀ 3.4 × 1.2 ≈ 4.1.

### Seed
A text field (default `meridian`). The seed, scenario and difficulty together decide **which events happen in which weeks**. Two players with the same three settings get the same scheduled events, which makes class comparisons fair. The seed does not affect the disease model, which is fully deterministic. Some events are triggered by your own play (see [§12](#12-screen-3--events)), so they can differ between players even on the same seed.

### Display
- **Solo** — the standard layout for one person at a screen.
- **Classroom** — a large-type, high-contrast projection layout with debate and scoreboard views. See [§16](#16-classroom-projection-mode).

The choice is remembered by the browser.

### Lobbies
Sets how many interest groups score the government on the Class Scorecard.
- **3 groups** — Business, General Public, Vulnerable.
- **5 groups** (default) — adds Healthcare and Treasury.

### Summary tiles
Four tiles update as you change the settings: Population, Effective R₀ (after the difficulty multiplier), Vulnerable fatality rate, and Weekly Budget.

### ASSUME COMMAND
Starts the game. All sliders and toggles reset to zero/off, policies to None, and vaccine priority to Elderly first.

---

## 5. Screen 2 — Command Centre

This is where you spend almost all of your time. It has six areas:

| Area | Position | Contents |
|---|---|---|
| Header | Top | Scenario and difficulty, current week (of 12), **Budget Remaining** |
| News ticker | Below header | "MERIDIAN WIRE" headlines reflecting the current state |
| Left panel | Left | **Resource Allocation** sliders and the **Weekly Budget** breakdown |
| Centre panel | Middle | Population counts, hospital bar, economy and satisfaction bars, forecast strip, four charts |
| Right panel | Right | **Policy Levers**, Advisors, Active Situation, Model Notes |
| Footer | Bottom | Status message and the **RUN WEEK →** button |

### Header
- **Budget Remaining** is this week's budget minus everything currently selected. It is **green** when healthy, **amber** when less than 20% of the budget is left, and **red with a minus sign** when you are over budget.

### News ticker
Scrolling headlines generated from the current state: the week, any breaking event, whether Rₑ is high (above 1.4) or below 1, cumulative deaths, hospital strain (above 90% load), economy (below 40 or above 75), satisfaction (below 40 or above 75) and the vaccine programme. It reflects what has happened; it is not an extra source of information.

### Footer
- The status message reads "Set resources and policies, then run the week", or warns that you are over budget, and by how much.
- **RUN WEEK →** is disabled while you are over budget.

---

## 6. Resource sliders (left panel)

Every resource is a slider from **level 0 to level 5**. The figure on the right of each slider is its cost **this week** (level × unit cost). In Classroom mode it is prefixed with the level, for example `L3 · $1.5M`.

Resources are charged **every week they are set above zero**.

### Permanent Capacity — $1.5M per level per week
- Adds **250 hospital beds per level**, available immediately and **kept for the rest of the game**.
- The base hospital system has 1,000 beds.
- **Important:** each week the slider is above zero, you buy *more* beds and pay again. Leaving it at level 2 for three weeks adds 1,500 beds and costs $9M in total. Once you have enough beds, set it back to 0. The beds you bought stay.
- Best bought early: beds bought in week 1 serve for 12 weeks.

### Surge Capacity — $0.6M per level per week
- Adds **300 beds per level, for this week only**.
- Cheaper per bed than permanent capacity, but it disappears at the end of the week.
- Useful for responding to a peak you can see coming.

### Medical Staff — $1.0M per level per week
- Lowers the fatality rate: by **9% per level** for the general group and **7% per level** for the vulnerable group (up to 45% / 35% at level 5).
- The reduction applies to the fatality rate whether or not hospitals are full. Its value is greatest when hospitals overflow, because overflow multiplies fatality (see [§9](#9-reading-the-centre-panel)).
- Keeping staff at 0–1 while hospitals are above 80% full can trigger a **Hospital Staff Walkout** event.

### Testing & Tracing — $0.6M per level per week
- Cuts transmission by **5.5% per level** (27.5% at level 5).
- Unlike lockdown, masks and school closures, its effect does **not** depend on public compliance.
- Keeping testing at 0–1 while infections are above 3,000 and rising can trigger a **Super-Spreader Cluster** event.

### Vaccination — $1.0M per level per week
- **Locked** (greyed out) until the scenario's vaccine week (week 4, or week 5 for Fast & Deadly).
- Each level immunises about **10,000 susceptible people per week**, so 50,000 per week at level 5.
- Vaccinated people become immune, but that immunity **wears off at the same rate as natural immunity** for the scenario. In Slow Burn (9% per week), vaccination needs to be sustained.
- **Prioritisation** (three buttons below the slider) decides who gets doses first:

| Option | Who is vaccinated first | Effect |
|---|---|---|
| **Elderly first** (default) | All susceptible vulnerable people, then the general group | Cuts deaths fastest |
| **Balanced** | Both groups in proportion to how many are still susceptible | A middle course |
| **Workers first** | All susceptible general-group people, then the vulnerable | Removes more of the population driving transmission |

Bonus doses from events also follow this setting, and they arrive even if the vaccine week has not yet been reached.

### Epidemic Modelling — $0.5M per level per week
- Funds the **forecast**. Modelling is **bought a week in advance**: what you fund this week produces projections **next** week. See [§10](#10-forecasting).
- Higher levels give a longer forecast horizon and a narrower uncertainty band.
- At **level 3 or higher**, your modelling team spots variants early, which makes a variant event less severe (see [§12](#12-screen-3--events)).
- If you defund it, the forecast stops the following week.

### Port-of-Entry Screening — $0.5M per level per week
- Gives a small ongoing reduction in transmission (1% per level).
- Its main value is **cumulative**: every level-week of screening is added up. When a variant arrives, each accumulated level cuts the variant's impact by 6%, up to a maximum of 75% (reached after 13 level-weeks, for example level 3 for five weeks).
- It costs a little economic output: 0.25 index points per level per week.
- It can only help if it is bought **before** the variant arrives. The first variant always arrives in week 3, 4 or 5.

### Public Communications — $0.5M per level per week
- Raises **compliance**, which scales how effective lockdown, masks, school closures and shielding are.
- At level 0, compliance is 55%. Each level adds 9 points, reaching 100% at level 5.
- When any restriction is active (lockdown, school closures, travel restrictions or shielding), each level also adds 0.5 satisfaction per week. Masks alone do not count as a restriction here.
- It is cheap and makes every policy you choose more effective.

---

## 7. Policy levers (right panel)

Tiered policies are a row of buttons; click one to select it. Toggles are on/off switches. All policies are charged **every week they are active**.

The "R₀ ×" figures shown in the panel are what each policy achieves at **100% compliance**. At lower compliance they achieve proportionally less. With no communications and no financial support, compliance is 55%, so a "×0.40" strict lockdown actually gives about ×0.67.

### Lockdown Stringency

| Tier | Cost/wk | Transmission at full compliance | Economy cost/wk | Satisfaction cost/wk |
|---|---|---|---|---|
| None | $0 | ×1.00 | 0 | 0 |
| Mild | $1M | ×0.82 | −5 | −3 |
| Moderate | $2M | ×0.65 | −9 | −8 |
| Strict | $4M | ×0.40 | −17 | −13 |

- Moderate or Strict for **two or more consecutive weeks** while satisfaction is below 55 can trigger **Anti-Restriction Protests**.
- Economy costs are reduced by Public Financial Support.

### Shield Vulnerable

| Tier | Cost/wk | Cut in vulnerable infections (full compliance) | Economy/wk | Satisfaction/wk |
|---|---|---|---|---|
| None | $0 | 0% | 0 | 0 |
| Voluntary | $0.8M | 40% | −0.4 | −1.0 |
| Mandatory | $1.5M | 68% | −0.9 | −3.0 |

Shielding reduces how often vulnerable people **catch** the disease. It does not reduce transmission in the general group. It protects the group most likely to die without closing the whole city. **Mandatory** shielding counts as a restriction that prevents the economy's weekly recovery bonus (see [§9](#9-reading-the-centre-panel)); Voluntary does not.

### Public Financial Support

| Tier | Cost/wk | Restriction economic damage absorbed | Satisfaction/wk | Compliance bonus |
|---|---|---|---|---|
| None | $0 | 0% | 0 | 0 |
| Partial | $3M | 40% | +1.5 | +6 points |
| Full | $6M | 72% | +3.2 | +11 points |

Financial support only cushions the economic damage **caused by restrictions** (lockdown, school closures, travel restrictions and shielding). It does not offset economic losses from deaths or border screening. At $6M it takes 60% of the Standard budget and more than 90% of the Nightmare budget.

### Mask Mandate — $0.5M/wk
Cuts transmission by 16% × compliance. It has **no economy or satisfaction cost**.

### Schools Closed — $1.0M/wk
Cuts transmission by 11% × compliance. Costs 2 economy and 1.5 satisfaction per week.

### Travel Restrictions — $0.5M/wk
Cuts transmission by 6%, regardless of compliance. Costs 1.5 economy and 0.5 satisfaction per week.

All transmission reductions **multiply** together. For example, at full compliance, Moderate lockdown (×0.65) plus masks (×0.84) plus testing level 2 (×0.89) gives roughly ×0.49.

---

## 8. The weekly budget

The **Weekly Budget** box under the sliders shows:

| Line | Meaning |
|---|---|
| Income | This week's budget, including any grant from an event |
| Resources | Total of all slider costs |
| Policies | Total of all policy costs |
| Event response | The cost of the option you chose for this week's event (shown only if it is above zero) |
| Remaining | What is left; turns red if negative |

Rules:
- **Unspent money does not carry over** to the next week. If you spend less than half the budget, the weekly report says so.
- You **cannot** run the week while over budget.
- The cost of an event response is taken from **this week's** budget. Choosing an expensive response leaves less for everything else.

---

## 9. Reading the centre panel

### Population counters
Six figures across the top:

| Counter | Meaning |
|---|---|
| **Susceptible** | Can catch the disease, including people whose immunity has worn off |
| **Exposed** | Infected but not yet infectious (incubating; about 6 days on average) |
| **Infectious** | Currently able to spread it (about 8 days on average) |
| **Recovered** | Currently immune, through recovery or vaccination |
| **Deaths (cum.)** | Total deaths so far |
| **Hosp. Load** | Last week's peak bed demand as a percentage of capacity. Green below 75%, amber 75–99%, red at 100% or above |

### Hospital Capacity Usage bar
Shows the beds in use out of the beds available (for example `812 / 1,250 beds`). When a forecast is active, the projected load for next week is shown alongside it, with **⚠ OVERFLOW** if it would reach 100%.

Bed demand comes from the number of people who are infectious at the same time: about 5% of infectious general-group people and 22% of infectious vulnerable people need a bed. When demand exceeds capacity, **fatality rises steeply**. At double capacity, fatality is three times higher; the multiplier approaches five times as overload becomes extreme, with a ceiling of 10% (general) and 30% (vulnerable) fatality. Any overflow during the week also costs 4 satisfaction points.

### Economy Index and Public Satisfaction bars
Both run from 0 to 100 and start at 100. The colour is green or purple at 70 and above, amber from 40 to 69, and red below 40.

**The economy is driven by:**
- Restrictions (lockdown, school closures, travel restrictions and shielding), reduced by financial support
- Deaths: about −1 point per 90 deaths in a week
- Border screening: −0.25 per level
- A **+1.2 recovery bonus** each week with no lockdown, no school closures, no travel restrictions, and no more than Voluntary shielding

**Satisfaction is driven by:**
- Restrictions (losses), financial support (gains), and communications (gains, only while restrictions are active)
- Deaths: about −1 point per 180 deaths in a week
- Hospital overflow: −4
- High case numbers: up to −4 (−1 per 10,000 new cases)
- Event outcomes

> **Economic collapse:** if the Economy Index reaches **0 in any week**, the debrief gives an automatic **F (ECONOMIC COLLAPSE)**, whatever the health outcome.

### Forecast strip
A one-line projection. See [§10](#10-forecasting).

### Epidemic Curve (main chart)
- **Red line with dots, shaded area**: people infectious, on the left axis.
- **Purple line**: new cases each week, on the left axis.
- **Grey line**: deaths each week, on the **right axis**, which has its own scale.
- **Dashed blue line with shaded band**: forecast of infectious people, when modelling is active.
- **Dashed grey line**: forecast of weekly deaths.
- **Dashed amber "HOSP CAP" line**: a rough guide to the number of infectious people at which hospitals fill. It assumes a 50/50 mix of the two groups, so it usually sits lower than the true point at which hospitals fill. Treat it as an early warning, not an exact threshold. Use the hospital bar for the actual figure.
- **Event icons** above the curve mark the weeks in which events fired.
- **Hover** over a week to see its infectious count, new cases, weekly and cumulative deaths, Rₑ, economy and satisfaction, and lockdown tier.

### Effective Rₑ over time
The transmission number your policies produced each week. The line is red above 1 and green at or below 1, and a dashed line marks R = 1.

> Rₑ here is the R₀ after the effect of your policies. It does **not** account for how many people are already immune. Late in an outbreak, when many people have recovered or been vaccinated, infections can fall even while this figure is above 1. Use the infectious curve to judge whether the outbreak is actually growing.

### Economy & Satisfaction chart
Both indices over time. Dotted guide lines mark 70 ("good") and 40 ("weak"), and the shaded red zone below 30 is the danger area. Forecast lines and bands appear when modelling is active.

### Population Compartments chart
A stacked area chart of the whole population as percentages: Susceptible (blue), Recovered (green), Exposed (amber), Infectious (red), Deaths (grey). Cumulative deaths are labelled at the top left.

---

## 10. Forecasting

Forecasts are a capability you **buy in advance**:

- The forecast you see **this week** depends on the Epidemic Modelling level you funded **last week**.
- The level you fund **this week** decides next week's forecast.
- You cannot briefly raise the slider, read a projection, and lower it again at no cost.

### What the strip shows

| State | Message |
|---|---|
| Not funded last week, not funded now | "Forecast — locked" |
| Not funded last week, funded now | "Forecast — active next week" |
| Funded last week | A projection of next week if you commit to the current plan: new cases, deaths, economy (with change), satisfaction (with change), hospital load and Rₑ, then the position at the end of the horizon |

The projection **updates live** as you move sliders and change policies, so you can compare plans before you commit to one.

### Horizon and band by level funded last week

| Level | Horizon | Band (± per week ahead) |
|---|---|---|
| 1 | 3 weeks | ±30% |
| 2 | 4 weeks | ±15% |
| 3 | 5 weeks | ±10% |
| 4 | 6 weeks | ±7.5% |
| 5 | 6 weeks | ±6% |

The band widens with each week further ahead. Below level 3, the strip is labelled "coarse".

### What the forecast assumes
- You keep **exactly the current plan** for every future week.
- **No events occur**. That includes this week's event: the forecast does not include the effect of the response you just chose (for example a variant surge or super-spreader cluster).
- Vaccination counts only if it is already available this week.

If no event is active and your plan does not change, the next-week projection matches what actually happens. The difference between projection and outcome therefore comes from events and from your own later changes. See the Technical Guide, §6.

Warnings in the strip:
- **"⚠ modelling unfunded this week — forecast stops next week"** when the slider is at 0.
- **"· L*n* funded, effective next week"** when this week's level differs from last week's.

---

## 11. Advisors, situation panel and model notes

### Consult Advisors (Solo mode only)
Click an advisor to open or close their advice. Advice updates as you change your plan.

| Advisor | Role | Advises on |
|---|---|---|
| 🩺 Dr. Adeyemi | Chief Epidemiologist | Last week's Rₑ (above 1.5, above 1, or below 1) and whether infection is concentrated in the vulnerable group |
| 💼 Okonkwo | City Treasurer | Economy below 40, the cost of strict lockdown, the value of permanent capacity |
| 🎙️ Vance | Communications Chief | Satisfaction below 40, restrictions with communications below level 2 |

Advisors each see one side of the problem and can contradict each other.

### Active Situation
After you respond to an event, a red-edged panel restates the event and your choice. It lasts for the current week only.

### Model Notes (Solo mode only)
A short summary of the model's assumptions and how the scores are weighted.

---

## 12. Screen 3 — Events

At the start of a week, an event card may appear **before** the Command Centre. At most one event occurs per week. You **must** pick one response; there is no option to close the card without choosing. The response's cost is taken from this week's budget, and its effects last **this week only**.

The card has a red top edge for a crisis and a green one for good news. Text in teal tells you when an earlier investment you made has reduced the impact.

### How events are chosen
- **Scheduled events** are fixed at the start by the seed, scenario and difficulty: 3, 4 or 5 of them in weeks 3–11. A **variant always appears** in week 3, 4 or 5.
- **Triggered events** fire only in a week with no scheduled event, at least two weeks after the previous triggered event, and only when their condition is met (checked in this order):
  1. **Protests**: Moderate or Strict lockdown for 2+ consecutive weeks **and** satisfaction below 55.
  2. **Super-spreader**: testing at level 0–1 last week, infections rising, **and** more than 3,000 infectious.
  3. **Staff walkout**: medical staff at level 0–1 last week **and** hospitals above 80% full.

"Severity" below is the difficulty's event severity (×1.0, ×1.25 or ×1.5).

### 🧬 More Transmissible Variant (scheduled)
Raises R₀ this week by **1.4 × severity**, or **1.1 × severity** if you funded modelling at level 3+ last week. Accumulated port-of-entry screening then cuts this by 6% per level-week (maximum 75%).

| Response | Cost | Effect |
|---|---|---|
| Close borders & sequence aggressively | $1.5M | 40% of the surge applies; −2 satisfaction |
| Targeted containment of clusters | $0.7M | 70% of the surge applies |
| Monitor only | Free | The full surge applies |

### 🏥 Healthcare Worker Burnout (scheduled)
Raises fatality by 25% × severity.

| Response | Cost | Effect |
|---|---|---|
| Emergency retention bonuses | $1.2M | No fatality increase |
| Redeploy trained reserves | $0.5M | Half the increase |
| Ask staff to push through | Free | The full increase; −3 satisfaction |

### 📱 Misinformation Surge (scheduled)
Cuts compliance by 28% × severity.

| Response | Cost | Effect |
|---|---|---|
| Rapid counter-messaging campaign | $1.0M | 15% of the loss applies; −1 satisfaction |
| Partner with trusted local voices | $0.4M | Half the loss; −2 satisfaction |
| Ignore it | Free | The full loss; −6 satisfaction |

### 😮‍💨 Lockdown Fatigue (scheduled)
Cuts lockdown effectiveness by 26% × severity.

| Response | Cost | Effect |
|---|---|---|
| Announce a public support package | $1.0M | 15% of the loss applies; +2 satisfaction |
| Renewed public messaging | $0.5M | Half the loss |
| Do nothing | Free | The full loss; −4 satisfaction |

### 🤝 International Aid Grant (scheduled, good news)

| Response | Cost | Effect |
|---|---|---|
| Accept — general relief fund | Free | +$4M budget this week |
| Accept — earmarked, plus matched vaccines | Free | +$3M budget and 8,000 doses this week |

### 💉 Vaccine Supply Windfall (scheduled, good news)

| Response | Cost | Effect |
|---|---|---|
| Fast-track distribution | $0.4M | +22,000 doses this week |
| Standard rollout | Free | +13,000 doses this week |

### 📢 Anti-Restriction Protests (triggered)

| Response | Cost | Effect |
|---|---|---|
| Ease restrictions to relieve pressure | Free | Lockdown is 32% less effective this week; −1 satisfaction |
| Hold firm | Free | −8 satisfaction; compliance ×0.75 |
| Open dialogue + financial support | $1.0M | −2 satisfaction |

### 🦠 Super-Spreader Cluster (triggered)
About 9,000 × severity extra people are infected at once at the start of the week. Shielding protects some of the vulnerable people among them.

| Response | Cost | Effect |
|---|---|---|
| Mass testing blitz | $1.2M | 20% of the cluster gets through |
| Localised lockdown of the area | $0.5M | 50% gets through; −2 satisfaction |
| Manual contact tracing only | Free | The full cluster |

### ⛑️ Hospital Staff Walkout (triggered)

| Response | Cost | Effect |
|---|---|---|
| Meet staffing demands | $1.2M | Capacity ×0.95 |
| Bring in agency & military reserves | $0.5M | Capacity ×0.85 |
| Refuse to negotiate | Free | Capacity ×0.68; −4 satisfaction |

---

## 13. Screen 4 — Weekly report

After each week, a report summarises it.

### Six headline figures

| Figure | Detail line |
|---|---|
| New Cases | Change from last week: red if up, green if down |
| Deaths This Wk | Cumulative deaths |
| Hosp. Load | Peak beds in use / beds available |
| Effective R | "✓ Below epidemic threshold" or "⚠ Above 1.0 — growing" (see the note on Rₑ in [§9](#9-reading-the-centre-panel)) |
| Economy | Change in points |
| Satisfaction | Change in points |

### Intelligence Report
Automatic notes on what happened. These cover:
- Whether Rₑ is above or below 1.
- Hospital status: overflowing, approaching overflow (above 75%), or managing.
- Deaths by group, and whether shielding is active.
- Whether an event shaped this week's figures.
- Vaccine availability, in the week vaccines unlock.
- A warning if you spent less than half the budget.
- Warnings if the economy falls below 40 or satisfaction below 35.

### Reflection Prompt
A different question each week, designed for discussion or written reflection.

**CONTINUE →** takes you to the next week's event (if any) and the Command Centre. After week 12 it opens the Debrief.

---

## 14. Screen 5 — Debrief

### Grade
A letter grade based on a **composite score**: 40% deaths, 30% final economy, 30% final satisfaction. The deaths part is 100 with no deaths and falls by 1 point per 100 deaths, so it reaches 0 at 10,000 deaths.

| Composite | Grade | Label |
|---|---|---|
| 87+ | A+ | EXEMPLARY |
| 72–86 | A | EXCELLENT |
| 55–71 | B | COMPETENT |
| 36–54 | C | ADEQUATE |
| 18–35 | D | POOR |
| 0–17 | F | CATASTROPHIC |
| Economy hit 0 in any week | F | ECONOMIC COLLAPSE |

### Summary tiles
Total deaths, final Economy Index, final Satisfaction and the composite score.

### How Your Run Compared
Your infection curve against three reference strategies. Each was run on the same scenario and difficulty but **without any events**:

| Reference | What it does |
|---|---|
| **Do nothing** | No spending at all |
| **Strict-only** | Strict lockdown and communications level 1, every week |
| **Balanced ref** | Moderate then mild lockdown, staff 2, testing 2, communications 3, voluntary shielding, masks, early border screening and permanent beds, modelling 1, vaccination 3 when available, partial financial support for the first six weeks |

The legend shows each strategy's total deaths. **Note:** the Balanced reference ignores the budget limit (it costs about $14M in week 1). It is a teaching benchmark, not a plan you can afford. Strict-only typically drives the economy and satisfaction to zero.

### Final Outcomes
A paragraph covering total and per-group deaths, final indices, peak infections and the week it occurred, the number of weeks hospitals overflowed, the composite score, your weakest dimension, and total spending.

### Class Reflection Questions
Five discussion questions on how the score is weighted, shielding versus suppression, vaccine priority, investing in advance, and who bears the costs. Some include figures from your run.

### Buttons
- **CLASS SCORECARD →** opens the lobby scorecard.
- **CONFIGURE NEW SIMULATION** returns to the briefing.

---

## 15. Screen 6 — Class Scorecard

The scorecard scores the same run from the point of view of each interest group, then scores the government on how well it served **all** of them.

### Lobby cards (0–100 each)

| Lobby | Index | What it measures |
|---|---|---|
| 💼 **Business** | Economy Index | Half the final economy plus half the average economy over the 12 weeks |
| 🏘️ **General Public** | Satisfaction Index | Half the final satisfaction plus half the 12-week average |
| 🛡️ **Vulnerable** | Protection Index | Vulnerable-group deaths, on a log scale (fewer is better) |
| 🏥 **Healthcare** (5-group mode) | Capacity Index | Peak hospital load as a percentage of capacity, on a log scale |
| 🏛️ **Treasury** (5-group mode) | Value for Money | How well Business, Public and Vulnerable did, with a bonus for spending less of the total budget. Spending nothing and achieving nothing scores 0 |

Each card shows the index, its grade and the raw figure behind it.

### Government composite
The government score is the **geometric mean** of the active lobby indices. Unlike a simple average, one very low score drags the whole result down, and a score of 0 for any lobby makes the government score 0. You cannot score well by serving one group and abandoning another.

**Capture spread** is the gap between the best- and worst-served lobbies. At **45 or more**, the scorecard says the government was "captured" by its best-served lobby.

### Grade bands
All lobbies and the government use the same bands, which depend on difficulty:

| Grade | Standard | Hard |
|---|---|---|
| A+ | 90+ | 82+ |
| A | 78–89 | 70–81 |
| B | 62–77 | 55–69 |
| C | 46–61 | 40–54 |
| D | 30–45 | 25–39 |
| F | below 30 | below 25 |

Nightmare has no bands of its own; it uses the Hard bands and shows a warning that grades are indicative.

### Government Decision Log
A table with one row per week: lockdown, shielding, financial support, masks, schools, travel, testing, communications, staff, vaccine level and priority, spending, economy, satisfaction, deaths, hospital load, and a **"Served"** label suggesting whose interests that week favoured:

| Label | Rule |
|---|---|
| Vulnerable | Lockdown tier + schools closed + travel restricted adds up to 3 or more |
| Business | None of lockdown, school closures or travel restrictions (even if shielding is on) |
| Vuln·targeted | Shielding active with lockdown at None or Mild |
| Mixed | Anything else |
| …+Public | Added when any financial support was given |

### Export buttons

| Button | Output |
|---|---|
| Copy scorecard | A plain-text summary copied to the clipboard, ready to paste into a chat or document |
| Download CSV | Summary, lobby scores, raw outcomes and a week-by-week table: `outbreak-<scenario>-<difficulty>-<seed>.csv` |
| Download JSON | The full record of the run, for collating a class's results: `outbreak-<scenario>-<difficulty>-<seed>.json` |
| Print / PDF | Prints the scorecard only, on a light background, ready to save as PDF |
| ← Back to debrief | Returns to the debrief |

---

## 16. Classroom (projection) mode

Select **Classroom** on the briefing screen, or press **Ctrl+Alt+C** (Cmd+Alt+C on a Mac) at any time.

### What changes
- Larger type, thicker chart lines and higher-contrast colours for projectors.
- The epidemic curve takes the spare vertical space.
- To fit every control on screen without scrolling, the following are **hidden**: lever descriptions, Advisors and Model Notes. On short screens (950px high or less), policy notes are hidden too.
- Slider cost readouts show the level, for example `L2 · $1.2M`.
- Two view buttons appear in the header: **DEBATE** and **SCORES**.

### Debate view (D)
Hides both control panels so the charts fill the screen. A **Current Proposal** bar shows the plan on the table in read-only form: every policy, every resource level, the vaccine setting, and the total committed (or **OVER** by how much). Use it while the room argues, then press D again to return to the controls.

### Scores view (S)
Shows a live **lobby scoreboard** under the ticker: each lobby's current index and grade, and the government composite with its capture spread. It is off by default, for use at checkpoints. Before any week has run, all averages equal the starting values.

---

## 17. Keyboard shortcuts

| Key | Where | Action |
|---|---|---|
| Ctrl+Alt+C / Cmd+Alt+C | Anywhere | Toggle Solo / Classroom mode |
| D | Command Centre, Classroom mode | Toggle Debate view |
| S | Command Centre, Classroom mode | Toggle the lobby scoreboard |

D and S are ignored while you are typing in a text field.

---

## 18. What participants commonly miss

These follow directly from how the model works. They are useful prompts when a group is struggling, or for the closing discussion. Consider whether to reveal them in advance: discovering them is part of the learning. The [User Guide](USER_GUIDE.md) explains how each control and event works, including what triggers events, but gives no strategy advice; the strategic points in this table are not in it.

| Common miss | What happens | Prompt you can use |
|---|---|---|
| Acting late | Transmission compounds. Restrictions applied after the peak cost the economy and satisfaction while saving few lives | "What did weeks 1–3 decide?" |
| Ignoring communications | Without them, compliance is 55%. Lockdown, mask and shielding spending achieves only about half of what the panel suggests | "Why is your strict lockdown only giving ×0.67?" |
| Leaving Permanent Capacity on | Each week it stays on, more beds are bought and paid for | "How many beds did you actually need?" |
| No border screening before week 3 | The variant arrives in week 3–5, and screening only helps if it has accumulated by then | "Could you have known the variant was coming?" |
| No modelling before it is needed | Modelling works a week in arrears. Level 3+ in the previous week also softens the variant | "When did you decide you needed a forecast?" |
| Blanket suppression instead of shielding | Shielding cuts vulnerable deaths at far less economic cost | "Who bore the cost of your strategy?" |
| Letting the economy hit 0 | One week at 0 means an automatic F on the debrief | "Was there a point of no return?" |
| Tripping event triggers | Testing ≤1 while cases rise (super-spreader); staff ≤1 under high hospital load (walkout); long hard lockdown while satisfaction is low (protests) | "Was that event bad luck, or a consequence?" |
| Leaving masks off | Masks have no economic or satisfaction cost | "What did masks cost you?" |
| Treating Slow Burn as one-off | Immunity, including vaccine immunity, wears off at 9% a week | "Why did the second wave come?" |

---

## 19. Model behaviours to pre-empt

The simulation is a simplified teaching model. The behaviours below are not bugs that stop play, but participants regularly notice them and ask about them. Knowing them in advance lets you answer confidently, or turn them into discussion about the limits of models. The Technical Guide, §14, lists the full set.

| Behaviour | What to tell the room |
|---|---|
| The report says "Above 1.0 — growing" while infections are falling | Rₑ here is the R number after the effect of policies. It ignores how many people are already immune. Look at the infectious curve to see whether the outbreak is growing |
| The forecast was exactly right | The model has no randomness. Without events and with an unchanged plan, next week's projection is exact. Higher modelling buys a longer view and a narrower displayed band, not more real accuracy |
| The forecast missed this week's event | The forecast ignores events, including the response chosen this week |
| A variant's effect disappeared the next week | A variant raises transmission for one week only |
| Vaccinated people became susceptible again | Vaccine immunity wears off at the same rate as natural immunity |
| Bonus doses arrived before vaccines unlocked | Doses from aid or a windfall apply whenever the event happens |
| The Balanced reference did far better than we could | It ignores the budget and costs about $14M in week 1. It is a benchmark, not an achievable plan |
| Strict-only did worst on economy | Strict-only drives the economy and satisfaction to 0 in every scenario |
| The HOSP CAP line was crossed but hospitals were not full | The line is an approximation that usually signals overflow early. The hospital bar is the accurate figure |
| The burnout event said staffing would help; it did not | The event's text describes an interaction that is not modelled. Staffing lowers fatality generally but does not change the event. The same applies to "best with high comms" on misinformation |
| A shield-only week was labelled "Business" in the decision log | The "Served" label checks for no lockdown, schools or travel restrictions before checking shielding |

---

## 20. Planning and running a session

### Before the session
- **Test the projector.** Switch to Classroom mode and check that every control is visible without scrolling, and that the charts are legible from the back of the room. Projectors with a short screen (950px high or less) hide policy notes automatically.
- **Check the network.** If Google Fonts are blocked, the system fonts still work; nothing else needs the internet.
- **Fix the settings.** Agree a seed, scenario and difficulty. Every group with the same three settings faces the same scheduled events, which keeps comparisons fair. Only Standard and Hard have calibrated scorecard grades; Nightmare grades are marked as indicative.
- **Choose a scenario for the learning goal:**

| Learning goal | Suggested scenario |
|---|---|
| A first, balanced introduction | Novel Respiratory |
| Speed of response and hospital capacity | Fast & Deadly |
| Long-term management and reinfection | Slow Burn / Endemic |
| Investing ahead of a threat | Variant Storm |

- **Play a run yourself** on the same settings, so that you know when the events land. The seed fixes the scheduled events, though triggered events depend on decisions.
- **Distribute the [User Guide](USER_GUIDE.md)** in advance if the group is new to the simulation.

### Session formats

| Format | How it works |
|---|---|
| **Whole class, one government** | One projected game. Participants are split into lobbies and argue each week; the facilitator or an elected "director" enters the agreed plan |
| **Small groups, parallel games** | Each group plays on its own device with the same seed. Compare scorecards at the end |
| **Individual** | Solo mode. Useful as homework or preparation; the advisors panel and model notes are visible in Solo mode only |

### Assigning lobbies
In 3-lobby mode, use Business, General Public and Vulnerable. In 5-lobby mode, add Healthcare and Treasury. Give each lobby its index from the Class Scorecard ([§15](#15-screen-6--class-scorecard)), so that each knows exactly what it is arguing for. Because the government is scored on a geometric mean, a group that wins every argument for one lobby will still score badly; this tension is the core of the exercise.

### Weekly rhythm
A suggested pattern for each week (adjust the time to your session length):

1. **Event.** If an event card appears, read it aloud and let lobbies argue for a response, then choose.
2. **Debate view (D).** Show the charts and the Current Proposal bar. Each lobby makes its case.
3. **Controls (D again).** Enter the agreed plan. If modelling was funded last week, the forecast strip updates live, so the room can compare options before committing.
4. **Scores (S), optional.** Show the live lobby scoreboard at checkpoints, for example in weeks 4, 8 and 12, rather than every week, so that the room argues from evidence and not from the scoreboard.
5. **Run the week and read the report.** Use the Reflection Prompt as a short discussion or writing point.

Twelve weeks at five minutes each is about an hour of play, plus the debrief. For a shorter session, set the debate time per week in advance and keep to it.

### Closing discussion
- Start with the **Debrief**: the grade, the comparison chart and the Final Outcomes paragraph.
- Use the **Class Reflection Questions**, which are designed for group discussion.
- Move to the **Class Scorecard**. Ask: which lobby was best served, which worst, and was the government "captured"? Which week in the decision log decided the outcome?
- Ask what the model leaves out: the debrief's fifth reflection question addresses who bears the costs within groups. [§19](#19-model-behaviours-to-pre-empt) gives further examples of simplifications to discuss.

---

## 21. Assessment and collating results

- **Copy scorecard** gives a text summary that participants can paste into a submission.
- **Download CSV** gives one file per run, with a week-by-week table suitable for a spreadsheet. Filenames include the scenario, difficulty and seed, so files from different groups do not collide unless the settings are identical; ask groups to rename them with a group name.
- **Download JSON** holds the complete record, suitable for collating many runs with a script.
- **Print / PDF** produces a printable scorecard.

Possible assessment approaches:
- A written justification of the group's strategy, using its decision log and charts as evidence.
- A comparison across groups on the same seed: why did similar strategies lead to different results?
- A critique of the scoring itself: who benefits from the 40/30/30 debrief weighting, and how would the outcome change under the scorecard's geometric mean?
