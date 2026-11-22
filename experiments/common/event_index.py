"""
Event-indexing similarity for the CC (game: RC), as an alternative to plain NCD.

Inspired by the event-indexing model of story comprehension (Zwaan, Langston &
Graesser, 1995): readers link events that share a protagonist, place, time, cause or
goal. Logs carry some of these as structured fields, so the CC can score a reference
line r against a session-2 event e on several dimensions, with no language model:

  entity   weighted overlap of the entities involved (colonists, animals, other pawns)
           -- the "protagonist" index. Entities come from the Actors field plus any
           entity name mentioned in the text; each entity is weighted by its IDF over
           session-2 events, so ubiquitous ones (Stench is in a third of all events)
           count for less than rare ones (the walrus, the grizzly).
  place    exp(-distance / PLACE_SCALE) between map positions (x, z); 0 when either
           position is off-map (e.g. (-1000, -1000, -1000)).
  type     1 if both logs have the same tag (CL/JOB/ARC/HP/SL), else 0. Only used when
           the reference lines are events: dialogue is always SL.
  text     1 - NCD, the existing measure (event-first, as in the game).

Time and causality are not used: across sessions every reference line is "long ago",
and the logs record no causes or goals.

score(r, e) = weighted mean of the dimensions; distance = 1 - score, so the existing CC
selectors (nearest, cap, MMR) work unchanged. The weights are untuned defaults (a gold
set of 8-13 lines is too small to fit them without overfitting).
"""

import math
import re

import numpy as np

from experiments.common.data import parse_line

DEFAULT_WEIGHTS = {"entity": 0.4, "text": 0.3, "place": 0.2, "type": 0.1}
PLACE_SCALE = 25.0          # map cells; similarity 0.37 at 25 cells, 0.13 at 50
IGNORED_ACTORS = {"NoSpecifiedActor"}
_WORD = re.compile(r"[A-Za-z]+")


def _split_actor(name):
    """'BearGrizzly38350' -> ['bear', 'grizzly']; 'Wolf_Timber38343' -> ['wolf', 'timber']; 'Papyrus' -> ['papyrus']."""
    name = re.sub(r"\d+$", "", name).replace("_", " ")
    parts = re.findall(r"[A-Z][a-z]+|[a-z]+", name)
    return [p.lower() for p in parts]


class EventIndexer:
    """
    Builds the entity vocabulary and per-line features, then scores reference x event.

    vocab_logs: full log lines whose Actors fields define the entity vocabulary
                (session-1 and session-2 event logs: the game has both).
    """

    def __init__(self, masker, vocab_logs, weights=None):
        self.masker = masker
        self.weights = dict(DEFAULT_WEIGHTS if weights is None else weights)
        colonist_variants = {v.lower() for v in masker.variants} | {
            w.lower() for v in masker.variants for w in v.split()}
        vocab = set()
        for line in vocab_logs:
            p = parse_line(line)
            if p is None:
                continue
            for a in p["actors"]:
                if a in IGNORED_ACTORS or a in masker.variants:
                    continue
                vocab.update(_split_actor(a))
        # Colonist names are handled by the masker (it knows every spelling); keep them out
        # of the word vocabulary so a colonist isn't counted twice.
        self.vocab = {w for w in vocab if w not in colonist_variants and len(w) > 2}

    # ------------------------------------------------------------------
    def entities(self, full_line):
        p = parse_line(full_line)
        desc = p["desc"] if p else full_line
        ents = set(self.masker.colonists_in(desc))
        if p:
            for a in p["actors"]:
                if a in IGNORED_ACTORS:
                    continue
                ents |= self.masker.colonists_in(a)
                ents.update(w for w in _split_actor(a) if w in self.vocab)
        for w in _WORD.findall(desc):
            w = w.lower()
            if w in self.vocab:
                ents.add(w)
            elif w.endswith("s") and w[:-1] in self.vocab:      # "gazelles" -> "gazelle"
                ents.add(w[:-1])
        return ents

    @staticmethod
    def place(full_line):
        p = parse_line(full_line)
        if p is None:
            return None
        nums = [int(n) for n in re.findall(r"-?\d+", p["loc"])]
        if len(nums) != 3 or min(nums) < 0:
            return None
        return nums[0], nums[2]

    @staticmethod
    def tag(full_line):
        p = parse_line(full_line)
        return p["tag"] if p else None

    # ------------------------------------------------------------------
    def score(self, ref_lines, event_lines, ncd_matrix, use_type=True):
        """
        ref_lines / event_lines: full log lines (one per unique description).
        ncd_matrix: (n_ref x n_events) NCD, used for the text dimension.
        Returns (score matrix, {dimension: matrix}) with scores in [0, 1].
        """
        ev_ents = [self.entities(l) for l in event_lines]
        ref_ents = [self.entities(l) for l in ref_lines]
        n = len(event_lines)
        df = {}
        for es in ev_ents:
            for x in es:
                df[x] = df.get(x, 0) + 1
        idf = lambda x: math.log((n + 1) / (df.get(x, 0) + 1)) + 1.0          # noqa: E731

        R, E = len(ref_lines), len(event_lines)
        ent = np.zeros((R, E))
        for i, a in enumerate(ref_ents):
            for j, b in enumerate(ev_ents):
                union = a | b
                if union:
                    ent[i, j] = sum(idf(x) for x in a & b) / sum(idf(x) for x in union)

        rp = [self.place(l) for l in ref_lines]
        ep = [self.place(l) for l in event_lines]
        place = np.zeros((R, E))
        for i, a in enumerate(rp):
            for j, b in enumerate(ep):
                if a and b:
                    place[i, j] = math.exp(-math.dist(a, b) / PLACE_SCALE)

        rt = [self.tag(l) for l in ref_lines]
        et = [self.tag(l) for l in event_lines]
        typ = np.array([[1.0 if a and a == b else 0.0 for b in et] for a in rt])

        text = np.clip(1.0 - ncd_matrix, 0.0, 1.0)
        dims = {"entity": ent, "place": place, "type": typ, "text": text}
        w = {k: v for k, v in self.weights.items() if k != "type" or use_type}
        total = sum(w.values())
        S = sum(w[k] * dims[k] for k in w) / total
        return S, dims
