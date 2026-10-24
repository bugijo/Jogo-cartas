# A Cisterna night-travel implementation plan

> Execution method: continuous implementation in the current authorized experimental branch, with focused tests, regression, independent reviews, checkpoint commits and normal fast-forward push.

**Goal:** Resolve each road segment in order, including the extra no-clock travel card in segments 9–10, while preserving M1 round costs, resources, fatigue and save/load.

**Architecture:** `IntegratedCampaign` owns the canonical clock and advances one road segment at a time. `Travel02` records normal and extra occurrences separately so one road segment cannot be charged twice; M1 spends only its actual rounds. Return settlement remains transactional and the persistent travel shoe commits only the revealed prefix.

**Tech Stack:** Existing Python dataclasses, campaign modules and `unittest`; no new dependencies.

**Global constraints:** Keep `RULES.md`, `CAMPAIGN.md`, `content/catalog.json`, kit físico 0.2 and `main` unchanged. Never award an item or victory without a legal receipt. Do not call a fixed scenario a complete campaign or a simulation a human playtest.

## Tasks

1. Add failing tests for normal segment transitions 8→9 and 9→10, extra occurrence without clock cost, one fatigue per nocturnal segment, card sequencing and duplicate prevention.
2. Add a persistent occurrence model/API that separates road-segment payment from regular and extra card revelation; save/load each pending state and keep the shoe exact on completion, emergency and reshuffle.
3. Integrate outbound and return flows; M1 consumes only its started rounds and its return/retreat behavior follows existing clock limits. Test normal-card M1 and extra-card M1, including clock 10.
4. Run focused and full regression; audit legal loadout, ammo, carried stock, save/load and receipts; fix defects before checkpoint.
5. Continue the Cisterna executor through the next actual blocker (Ponte/routes, rescues/promises, five-day night/cerco, filter and legal victory) without injecting prerequisites. Each implemented layer gets its own reproducible replay and commit.
6. Only after a legal Cisterna `verified_victory`, investigate migration/Última Transmissão and campaign simulation. Keep physical 0.2 intact; prepare no new print content while rules remain unresolved.

## Review focus

- Extra card after paying the night segment must not advance or fatigue the same segment twice.
- Save/load between normal card, extra card, choice, M1 and return must not duplicate draws or rewards.
- A route that reaches clock 10 must not receive free M1 rounds or silently skip its required minimum.
- Persistent shoe exhaustion must recycle deterministically only when a new draw actually needs it.
- Manually editable saves are structurally validated but are not cryptographically trusted.
