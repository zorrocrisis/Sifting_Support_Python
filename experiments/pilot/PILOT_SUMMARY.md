# Two-channel sifting: Week 0 pilot summary

*Prepared 2026-11-23, covering 2026-11-17 to 2026-11-23. Corpus: one colony, two sessions (`SimulatedDay1`, `SimulatedDay2`).*

## TL;DR

- **The reference channel (RC, also called CC) only finds continuity when it matches on the right thing.** Matching the dialogue the player saw against session-2 event logs fails, whatever the measure. Matching the **session-1 logs each dialogue line was generated from** ("provenance") works: with the game's own NCD, the RC finds the author's continuity matches (Recall@5 0.10 → 0.57, 0.65 with filtered candidates).
- **Provenance also fixes redundancy.** The RC no longer floods the pool with near-identical fight lines, and the share between the two channels behaves as a breadth/depth dial that doesn't depend on how topics are counted.
- **Embeddings aren't needed.** On the original dialogue they fail too (0.17). With provenance, NCD or event indexing come within reach of them without any language model, which supports dropping embeddings for domain generalisation.
- **Next, three implementation steps (detailed at the end):**
  1. implement dialogue provenance in the game and the Python pipeline;
  2. let the RC pick only from the AC's 43 filtered cluster representatives, by default;
  3. a set of smaller fixes.

---

## 1. Process

| step | what we did |
|---|---|
| **Set-up** | Checked the handoff against both repos and reported mismatches before building. For example, the CLI is `sipport.py`, the RC ranking already runs in Python with **event-first** NCD, and dialogue lives in its own file. |
| **Pilot framework** | Built `experiments/` (headless Python, no game changes): loading, NCD, name masking, RC selectors, and a line-by-line port of the game's pool composer. **The port reproduces all three saved Nov 8 game pools exactly.** |
| **Data clean-up** | Removed a truncated "Ackmann" log and dialogue S116 (a retelling of S111). Froze the event codes so the author's gold stayed valid. |
| **Tests A1–A4** | A1: does the RC find the author's continuity matches? A2: does it match on names? A3: is what it picks redundant? A4: does the share act as a breadth/depth dial? (A5, readers' blind comparison, and the A2 interpretation are on hold.) |
| **Iterations** | Changed one thing at a time:<br>• the **reference**: dialogue → session-1 selected logs → provenance<br>• the **candidates**: all 162 session-2 events → the 43 the AC keeps after filtering<br>• the **similarity measure**: NCD → event indexing → embeddings |

Author input throughout: gold matches (two sets), 88 topic tags, provenance confirmation, and decisions such as keeping MMR λ at 0.7 and avoiding embeddings.

## 2. Approaches tried

### Reference sets (what the RC matches against)

| reference | what it is | finding |
|---|---|---|
| **dialogue** (original) | the 8 lines colonists spoke in session 1, as the game logs them | Paraphrase, so it can't be matched to events. NCD falls back to colonist names. |
| **dialogue, stripped** | the same, without the "X said '…'" frame and opening vocative | Doesn't help (Recall@5 0.10 → 0.07). Names weren't the obstacle; paraphrase was. |
| **selected logs** | the 13 logs the AC selected in session 1 | Easy to match, but mostly by **exact repeats**. Puts duplicate lines in the pool (the composer deduplicates by `_ID_`, not text). |
| **provenance** | the dialogue line is shown and pooled, but scored through the session-1 logs it was generated from | Best overall (below). |

### Candidate sets (which session-2 events the RC may pick)

| candidates | what it is | finding |
|---|---|---|
| **all 162** | every distinct session-2 event (the game today) | Near-duplicates can take every RC slot. |
| **filtered 43** | the AC's cluster representatives at NCD 0.5, before traversal | The 13 fight lines collapse to 2, so redundancy drops. Reuses the AC's own clustering. |

### Similarity measures (how the RC scores a link)

| measure | how | finding |
|---|---|---|
| **NCD** | compression distance on descriptions (the game today) | Behaves like **repetition priming**: it only matches shared wording. |
| **event indexing** | shared entities (IDF-weighted) 0.4, NCD text 0.3, map distance 0.2, log type 0.1, from the logs' structured fields; after the event-indexing model (Zwaan et al., 1995) | Makes links NCD can't (walrus shot → walrus burial). With dialogue it amplifies name matching. |
| **embeddings** | all-MiniLM-L6-v2 cosine, run locally | Comparison only. Fails on dialogue without provenance; dropped for domain generalisation. |

### Redundancy controls

`cap` (at most 2 events per reference line), `mmr` (Maximal Marginal Relevance, λ 0.7), and `mmr_ix` (MMR whose redundancy term uses event indexing).

## 3. Major findings

### 3.1 Dialogue alone doesn't work, whatever the measure

A1 Recall@5 on the original dialogue (pass ≥ 0.5):

| | NCD | event indexing | embeddings |
|---|---|---|---|
| 162 events | 0.10 | 0.23 | 0.17 |
| 43 events | 0.00 | 0.22 | 0.29 |

- **Names, not content:** NCD matches on colonist names (A2). With all 162 events, the treeline line ("I watched the far treeline for more raiders") takes every RC slot with blow-by-blow fight lines between Odette and Stench: 1 dialogue line in the pool, redundancy 0.50.
- **Masking doesn't help:** replacing names with tokens, or deleting them, reshuffles the top pairs but doesn't improve recall (0.10 → 0.06–0.07).
- **MMR spreads, but can't fix:** it spreads the slots over 3 lines (redundancy 0.38), but it can't make the matches right.

### 3.2 Provenance fixes it, even with plain NCD

| | 162 · NCD | 162 · index | 162 · embeddings | 43 · NCD | 43 · index | 43 · embeddings |
|---|---|---|---|---|---|---|
| **A1 Recall@5** | **0.57** | 0.47 | 0.70 | **0.65** | **0.74** | 0.75 |
| A1 MRR | 0.65 | **0.81** | 0.66 | 0.74 | 0.72 | 0.77 |
| A3 `nearest`: lines / redundancy | 3 / 0.26 | 3 / 0.26 | 3 / 0.26 | 3 / 0.29 | 2 / 0.27 | 2 / 0.27 |
| A4 ρ, all labels / first label (pass ≤ −0.7) | −0.76 / −0.73 | −0.81 / −0.81 | −0.83 / −0.83 | −0.90 / −0.68 | −0.81 / −0.79 | −0.89 / −0.81 |

- **A1:** gold events jump from ranks 50–100 to the top 3 for most lines. The treeline line now finds "Boyd watching for targets" (rank 77 → 1), because its sources are "Odette watching for targets" and the tribal raid, not the fistfight.
- **A3:** with the game's own `nearest` selector, the pool spreads over 3 dialogue lines with the lowest redundancy of any dialogue set-up. The flooding came from name matching only.
- **A4:** breadth falls as the share rises under both ways of counting multi-topic tags. Original dialogue's dial depended on those tags (first label −0.53).
- **Which measure:** NCD and event indexing complement each other. Event indexing finds the walrus and anteater burials (rank 1–4 instead of 27–36). NCD keeps the exact-wording matches that event indexing loses ("watching for targets": 1 vs 16).

### 3.3 Provenance vs embeddings

![provenance vs embeddings](out_compare/provenance_vs_embeddings_a1.png)

- **Provenance is the bigger lever.** It raises every measure (NCD 0.10 → 0.57, embeddings 0.17 → 0.70). Changing the measure on the original line peaks at 0.29.
- **Embeddings alone don't understand the game.** They miss that "walrus" is a tribesperson (burial at rank 13) and that the dialogue's gazelles and grizzly are logged animals (ranks 50 and 22). They also give no dial (A4 ρ −0.61, first label +0.04).
- **With provenance and filtered candidates,** event indexing is within 0.01 of embeddings (0.74 vs 0.75) without a language model.

### 3.4 Selected logs work, but by repetition

With the 13 selected logs as the reference, NCD reaches 0.33 (0.16 without exact repeats) and event indexing 0.72. Half the share-0.5 pool is the same three logs written twice, though. Provenance keeps the advantage of event-like references while showing the player dialogue, and only the dialogue line enters the pool, so the duplicate problem goes away.

### 3.5 The dial is gentle

![dial, original vs provenance](out_compare/dial_original_vs_provenance.png)

- **Depth is the robust signal.** Redundancy rises with the share in every set-up (ρ ≈ 0.99), and provenance pools stay less redundant at every share (0.27 vs 0.41 at share 1).
- **Breadth moves little.** One or two topics across the whole range.
- **ρ overstates the evidence.** The 5 seeds barely change the AC, so most of the 25 pools behind each ρ are near-copies.

### 3.6 Smaller findings

- **Concatenation order matters for NCD** with dialogue: only 68% top-5 overlap between event-first and dialogue-first. It barely matters for event-like references (82%).
- **Actor match is weak evidence:** 41% of all dialogue × event pairs share a colonist by chance (mostly Stench).
- **Filtered candidates + event indexing + selected logs gives no dial** (A4 ρ +0.13): topics stay at 8–9 while redundancy rises. That's continuity without losing breadth, which is interesting for the game but contradicts A4's claim.
- **MMR with event-indexing redundancy** breaks up the dialogue fight lines (all 3 lines at λ 0.5). At the default λ 0.7 it stays one line short.

## 4. Psychology framing

- **AC = bottom-up salience:** novelty and surprise, like the orienting response.
- **RC = selection history** (Awh, Belopolsky & Theeuwes, 2012): past selections bias current selection. With NCD it behaves like **priming of pop-out / repetition priming** (Maljkovic & Nakayama, 1994): surface features that repeat win.
- **Why dialogue failed and provenance works:** dialogue is a **gist** trace and the source logs are **verbatim** traces (fuzzy-trace theory, Reyna & Brainerd). Retrieval works when the cue matches how the memory was encoded (encoding specificity, Tulving & Thomson). Provenance lets the player experience continuity through gist while selection uses the verbatim trace.
- **Event indexing** follows the situation-model links readers use to keep stories coherent (Zwaan, Langston & Graesser, 1995). It is related to "object files" (Kahneman, Treisman & Gibbs, 1992).
- **The redundancy controls:** MMR resembles **inhibition of return** (Klein, 2000); filtered candidates resemble attending to **category prototypes** rather than instances (Rosch).

## 5. Recommended implementation steps

> ### Step 1 — Implement dialogue provenance
> - **Generation (Python, `story_llm.py` + prompts):** give the dialogue step the pool logs (with `_ID_`s) as well as the narrative. Have it return each line together with the IDs of the logs it is about. Drop IDs that aren't in the pool; a line left without valid IDs has no provenance.
> - **Logging (C#, `DialogueManager.cs`, needs approval):** write provenance to a **sidecar file** (dialogue `_ID_` → source IDs + full source log text) rather than changing the log line format, which every parser depends on. Storing the text keeps session 2 self-contained.
> - **Reference channel (Python, `reference_sifting_channel`):** score a dialogue line by the smallest distance from any of its sources to each event, falling back to the line itself without provenance. The pool still receives the dialogue line. **Keep NCD**: it passes with provenance and needs no entity vocabulary or weights; event indexing can be an option later.

> ### Step 2 — RC candidates: the 43 filtered events by default
> - **Why:** better A1 with provenance + NCD (0.65 vs 0.57) and lower redundancy. It reuses the AC's existing `unique_logs_after_filtering`, so there's no extra clustering, and it scales to real sessions with thousands of distinct logs.
> - **Costs to report:** a slightly weaker dial (first label −0.68 vs −0.73), and the RC returns a cluster's representative, not the exact event.
> - **Keep "all events" as a setting** for experiments. With provenance, "all logs vs selected" on the reference side is moot: the sources are by construction session-1 selected logs.

> ### Step 3 — Other changes
> 1. **A dedicated dialogue tag (`DLG_`)**, instead of detecting dialogue by the "said '…'" pattern in `SL_` lines.
> 2. **Consistent name format** in dialogue logs: `DialogueManager.cs` writes short names, but the saved file uses full names.
> 3. **Quota accounting as a parameter:** whether the dialogue line counts against the RC's slots, which caps the RC at 3 lines at share 0.5.
> 4. **Skip MMR and text deduplication in the game for now:** with provenance + filtering, `nearest` already gives 3 lines and low redundancy.
> 5. **Commit the pilot work:** everything since the first pilot commit is uncommitted.
> 6. **Before the paper:** more colonies and sessions, and RQ1 restated more modestly (the share moves the pool from varied to focused, with redundancy as the main measure).

## 6. Caveats

- One colony, two sessions, 8 dialogue lines and 13 selected logs; single author's gold and topic tags.
- Provenance was simulated by hand-mapping each line to its sources. In the game the LLM will produce it and can be wrong.
- Event-indexing weights and the MMR λ were set by hand, not fitted.
- Seeds barely vary the AC, so spreads over seeds understate real variability.
- Filtered-candidate A1 credits a representative for its whole cluster; a stricter scoring would rate filtering lower.

## 7. Where everything is

| file | contents |
|---|---|
| `experiments/README.md` | how to run the pilot |
| `out*/PILOT_REPORT.md` | per-run report (one folder per reference × candidates × similarity) |
| `out_compare/REFERENCE_COMPARISON.md` | dialogue vs selected logs (NCD, embeddings, A2 masking) |
| `out_compare/CANDIDATE_FILTER_COMPARISON.md` | 162 vs 43 candidates |
| `out_compare/EVENT_INDEX_COMPARISON.md` | NCD vs event indexing, `mmr_ix`, λ sweep |
| `out_compare/DIALOGUE_LOGGING_COMPARISON.md` | original vs stripped vs provenance, dial plots |
| `out_compare/PROVENANCE_VS_EMBEDDINGS.md` | provenance vs embeddings |
| `out_compare/dialogue_pool_nearest_vs_mmr.md` | example pools with and without MMR |
| `gold_matches*.csv`, `topic_tags.csv`, `dialogue_provenance.csv`, `event_codes.csv` | author inputs (never regenerated) |
