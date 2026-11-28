# Session corpus: recording protocol and layout

The corpus for the two-channel sifting study: several colonies, each played over several sessions. While playing you **record logs only**. Narrative and dialogue are generated **offline**, session by session, so every condition (original dialogue, provenance, later variants) can be generated from the same logs, with the same frozen model and prompts, and with provenance known by construction.

Target: **at least 3 colonies × 3 sessions** (the handoff's goal was 5 × 3).

Check the corpus at any time with:

```
python -m experiments.corpus_validate
```

---

## 1. What a session is

**One session = one map load = one log folder.** The mod creates a new folder under `SaveData/SipportLogs/<date>` each time a map is loaded (`ModPaths.SetLoggingFolder`). Play a session in one sitting: load, play, press F9, save, quit. Don't reload mid-session; that starts a new folder and splits the session in two.

## 2. Before you record anything

1. **Finalise the definition of interesting continuity** in [`CONTINUITY.md`](CONTINUITY.md). The session plans and, later, the gold matches should both follow it.
2. **Fix the play settings** you'll keep the same within a colony: session length (the same number of in-game days per session, e.g. 3), game speed habits, and whether dev mode is allowed (yes, but only for planned events, see §4).
3. **Keep in-game dialogue out of the recordings.** Dialogue the game shows is also written into `event_logs.txt` (the pilot's session 1 has 4 such lines), and `MainEventLogGatherer` triggers dialogue checks periodically while `ModConfig.EnableSupport` is on. Turn that off for recording, or at least don't load or trigger dialogue (L, K, F10, LeftAlt, M). The validator warns if dialogue lines turn up in an event log.

## 3. Per colony

1. Start a new colony with the design from §5. Keep the storyteller, difficulty and scenario the same as the other colonies; vary biome, map and starting colonists.
2. Create `corpus/<colony_id>/` (e.g. `c01_tundra`) and copy [`_templates/colony.md`](_templates/colony.md) into it as `colony.md`. Fill in the set-up.

## 4. Per session

**Before playing**

1. Create `corpus/<colony_id>/s<n>/` (`s1`, `s2`, ...).
2. Copy [`_templates/session_plan.md`](_templates/session_plan.md) into it and write the plan: the colony's design (§5), the planned event and when to trigger it, if any. Keep it short.

**While playing**

3. Load the colony (session 1: the new colony; later sessions: the previous session's save).
4. Play normally for the agreed length. Trigger planned events with dev mode when needed (raids, arrivals), so they happen reliably. Everything else stays natural.
5. Don't use the in-game story pipeline (F1, N, M, LeftControl, LeftAlt) as data. It's fine to look, but its outputs come from a different configuration.

**At the end of the session**

6. Press **F9** once. It runs the sifting step only (no LLM call) and writes `formatted_event_logs.txt` into the session's log folder.
7. Save the game and note the save name.
8. Copy from the session's `SaveData/SipportLogs/<date>/` folder into `corpus/<colony_id>/s<n>/`:
   - `event_logs.txt`
   - `formatted_event_logs.txt`
   - `character_bios.txt`
9. Write `notes.md` (template in `_templates/`): what actually happened, anything surprising, and the save name. Write the gold later from what happened, not from the plan.
10. Run the validator.

**Order matters:** session *n*'s dialogue is generated from session *n* only, before session *n+1* is analysed. Recording ahead is fine; the offline steps run in sequence.

## 5. Colony designs (first round)

Each colony gets one design and is played for **3 sessions of 3 in-game days**. Only the planned event differs; everything else is the same across colonies.

| colony | design | planned event | why |
|---|---|---|---|
| **c01** | normal playthrough | none: progress the colony, trigger nothing | baseline: how much continuity arises from ordinary play |
| **c02** | raid | a raid on **day 2 of s1** (dev mode) | a strong, late thread: its aftermath (injuries, burials, prisoners, repairs) carries into s2 and s3 |
| **c03** | noteworthy event | **Refugee chased** on **day 1 of s1** (dev mode): a refugee arrives pursued by raiders; accept them | a new character plus a fight on arrival: character continuity (the newcomer's relationships and integration) and the pursuers, with time to develop within s1 and beyond |

Planned events always happen in **session 1**, so two later sessions (s2, s3) can show their consequences. The RC links each session's dialogue to the next session, so an event in s3 would have no later session to continue in.

**Kept the same across colonies:** storyteller and difficulty (one baseline, e.g. Cassandra Classic at a fixed difficulty), scenario, session length, game-speed habits. Write them in each `colony.md`.

**Varied across colonies:** biome, map and starting colonists, so the three colonies aren't the same colony three times.

**Notes:**

- "Nothing triggered" doesn't mean "nothing happens": the storyteller's own events (raids, visitors, illnesses) still occur in every colony. Record them in `notes.md` like everything else.
- After the planned event, play normally. Don't steer later sessions towards the event's consequences; whether they show up is part of what's being measured.
- **Limitation:** each design has one colony, so a difference between colonies can't be separated from the design (c02 might show more continuity because of the raid, or because of that colony). A second round with the designs swapped across new colonies would separate the two.

## 6. Layout

```
corpus/
  README.md                    this protocol
  CONTINUITY.md                what counts as interesting continuity (author)
  _templates/                  colony.md, session_plan.md, notes.md
  <colony_id>/
    colony.md                  set-up: storyteller, biome, colonists, settings   (author)
    s1/
      session_plan.md          written before playing                             (author)
      event_logs.txt           raw log, from SaveData/SipportLogs/<date>/         (game)
      formatted_event_logs.txt written by F9                                      (game)
      character_bios.txt       colonists at the end of the session                (game)
      notes.md                 what happened, save name                           (author)
      generated/               offline outputs, one folder per condition          (scripts)
        <condition>/           pool, narrative, dialogue_logs.txt, provenance
      gold/                    gold matches and topic tags for this session       (author, later)
    s2/
    ...
```

Files marked *author* are never overwritten by scripts. `generated/` is written only by the offline scripts and can be regenerated.

## 7. After recording (offline, not part of the protocol)

For each colony, in session order:

1. Build session *n*'s pool and generate its narrative and dialogue for each condition (frozen model and prompts; outputs cached). Write the dialogue in the game's log format, stamped on the event clock (just after session *n*'s last event), with provenance recorded from the pool that produced it.
2. Use that dialogue as the RC reference for session *n+1*.
3. Write gold matches and topic tags for session *n+1* from what happened, following `CONTINUITY.md`.

These scripts don't exist yet; they will be built on the pilot code (`experiments/`) once the first sessions are in.
