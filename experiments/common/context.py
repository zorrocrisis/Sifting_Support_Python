"""
One object holding everything a pilot test needs for a session: event and
dialogue log sets, bios, the CC matrices (plain and name-masked) and the
event-event similarity matrix. Built once per process and reused.
"""

from dataclasses import dataclass, field
from functools import cached_property

import numpy as np

from experiments.common import data, ncd, paths
from experiments.common.masking import NameMasker


@dataclass
class PilotContext:
    events_path: object = None
    dialogue_path: object = None
    bios_path: object = None
    order: str = ncd.EVENT_FIRST
    session_name: str = "session2"
    mask_pawn_ids: bool = False
    single_token: str | None = None     # None: C1, C2, ... per colonist; "C": one token for all
    reference_kind: str | None = None   # "dialogue" | "events"; default: the active reference set
    cc_candidates: str | None = None    # "all" | "filtered"; default: paths.CC_CANDIDATES
    cc_similarity: str | None = None    # "ncd" | "index"; default: paths.CC_SIMILARITY
    _size_cache: dict = field(default_factory=dict, repr=False)

    @property
    def similarity_mode(self):
        return self.cc_similarity or paths.CC_SIMILARITY

    @cached_property
    def indexer(self):
        from experiments.common.event_index import EventIndexer
        vocab_logs = list(self.events.log_dict)
        if paths.SESSION1_EVENTS.exists():
            with open(paths.SESSION1_EVENTS, encoding="utf-8", errors="ignore") as f:
                vocab_logs += [l.strip() for l in f if l.strip()]
        return EventIndexer(self.masker, vocab_logs)

    @cached_property
    def index_dims(self):
        """Event-indexing score and its dimensions (reference x events), every event."""
        refs = [self.dialogue.short_to_full[u] for u in self.dialogue.unique]
        evs = [self.events.short_to_full[u] for u in self.events.unique]
        kind = self.reference_kind or (paths.REFERENCE_KIND if self.dialogue_path is None else "dialogue")
        return self.indexer.score(refs, evs, self.M_ncd_all, use_type=(kind == "events"))

    # ------------------------------------------------------------------
    # Dialogue logging simulations (see dialogue_logging.py)
    # ------------------------------------------------------------------
    @property
    def reference_spec(self):
        """The active reference set's settings (empty for contexts built on explicit paths)."""
        return getattr(paths, "REFERENCE_SPEC", {}) if self.dialogue_path is None else {}

    @cached_property
    def ref_texts(self):
        """Reference descriptions as the CC's text similarity sees them (speech frame stripped if asked)."""
        if self.reference_spec.get("transform") == "strip_speech":
            from experiments.common.dialogue_logging import strip_speech
            return [strip_speech(u, self.masker) for u in self.dialogue.unique]
        return list(self.dialogue.unique)

    @cached_property
    def provenance(self):
        """
        For `dialogue_prov`: {reference index: [source full lines]} plus bookkeeping, or None.
        """
        spec = self.reference_spec.get("provenance")
        if not spec:
            return None
        from experiments.common.dialogue_logging import read_provenance, source_lines
        ids_by_dialogue, used_suggested = read_provenance(spec)
        all_ids = sorted({i for ids in ids_by_dialogue.values() for i in ids})
        found = source_lines(all_ids)
        by_index, missing = {}, sorted(set(all_ids) - set(found))
        for d, u in enumerate(self.dialogue.unique):
            ids = ids_by_dialogue.get(self.dialogue.id_of(u), [])
            by_index[d] = [found[i] for i in ids if i in found]
        return {"sources": by_index, "missing_ids": missing, "used_suggested": used_suggested,
                "lines_without_sources": [self.dialogue.id_of(self.dialogue.unique[d])
                                          for d, s in by_index.items() if not s]}

    def _provenance_distance(self):
        """
        Distance from each dialogue line to each event through its source logs: the smallest
        distance from any source to the event, with the CC's own similarity (NCD or event indexing).
        A line without sources keeps its own distance.
        """
        from experiments.common.data import description_of
        prov = self.provenance
        srcs = sorted({s for lines in prov["sources"].values() for s in lines})
        if not srcs:
            return self.M_own_all
        descs = [description_of(s) for s in srcs]
        ncd_src = ncd.ncd_rect(descs, self.events.unique, order=self.order, size_cache=self._size_cache)
        if self.similarity_mode == "index":
            evs = [self.events.short_to_full[u] for u in self.events.unique]
            dist_src = 1.0 - self.indexer.score(srcs, evs, ncd_src, use_type=True)[0]
        elif self.similarity_mode == "embed":
            from experiments.common.embed import cosine_rect
            dist_src = 1.0 - cosine_rect(descs, self.events.unique)
        else:
            dist_src = ncd_src
        row = {s: i for i, s in enumerate(srcs)}
        out = self.M_own_all.copy()
        for d, lines in prov["sources"].items():
            if lines:
                out[d] = dist_src[[row[s] for s in lines]].min(axis=0)
        return out

    # ------------------------------------------------------------------
    # CC candidates
    # ------------------------------------------------------------------
    @property
    def candidate_mode(self):
        return self.cc_candidates or paths.CC_CANDIDATES

    @cached_property
    def clusters(self):
        """
        The AC's clusters of session-2 events at paths.CC_FILTER_THRESHOLD: every subtree of the
        canonical dendrogram merging below the threshold is one cluster, represented by the medoid
        the AC itself picks (tree_utils.build_zoomed_view, seed 42). Returns
        {event index: index of its cluster's representative}.
        """
        from experiments.common.pool import preprocess
        from tree_utils import build_zoomed_view

        state = preprocess(self.events)
        if list(state["unique_logs"]) != list(self.events.unique):
            raise RuntimeError("pipeline unique_logs and the experiment's event list differ")
        thr = paths.CC_FILTER_THRESHOLD
        view = build_zoomed_view(state["root_0"], state["unique_logs"], state["counts"],
                                 state["distance_matrix"], threshold=thr, log_dict=state["log_dict"], seed=42)
        reps = {self.events.unique.index(u) for u in view["unique_logs_after_filtering"]}

        rep_of = {}

        def walk(node):
            if node.is_leaf() or node.dist < thr:
                members = node.pre_order()
                rep = [m for m in members if m in reps]
                if len(rep) != 1:
                    raise RuntimeError(f"cluster with {len(rep)} representatives")
                for m in members:
                    rep_of[m] = rep[0]
                return
            walk(node.left)
            walk(node.right)

        walk(state["root_0"])
        return rep_of

    @cached_property
    def candidate_mask(self):
        """Boolean mask over session-2 events: which ones the CC may pick."""
        if self.candidate_mode == "all":
            return np.ones(len(self.events), dtype=bool)
        mask = np.zeros(len(self.events), dtype=bool)
        mask[sorted(set(self.clusters.values()))] = True
        return mask

    def restrict(self, matrix, fill=np.inf):
        """Copy of a (reference x events) matrix with non-candidate events set to `fill`."""
        if self.candidate_mode == "all":
            return matrix
        out = matrix.copy()
        out[:, ~self.candidate_mask] = fill
        return out

    def representative(self, e):
        """The candidate that stands for event e (itself when every event is a candidate)."""
        return e if self.candidate_mode == "all" else self.clusters[e]

    @cached_property
    def events(self):
        return data.load_session_events(self.events_path or paths.SESSION2_EVENTS, name=self.session_name)

    @cached_property
    def dialogue(self):
        """
        The CC reference set (named `dialogue` for history: with PILOT_REFERENCE=s1_selected
        these are session-1 event logs, not dialogue).
        """
        kind = self.reference_kind or (paths.REFERENCE_KIND if self.dialogue_path is None else "dialogue")
        return data.load_reference(self.dialogue_path or paths.REFERENCE_PATH, kind=kind)

    @cached_property
    def bios_text(self):
        return data.load_bios_text(self.bios_path or paths.BIOS)

    @cached_property
    def masker(self):
        return NameMasker(self.bios_text, mask_pawn_ids=self.mask_pawn_ids, single_token=self.single_token)

    @cached_property
    def S_ee_index(self):
        """
        (n_events x n_events) event-indexing similarity between session-2 events (entities, place,
        log type, NCD text), for MMR's redundancy term in the *_ix variants. The diagonal is 1.
        """
        evs = [self.events.short_to_full[u] for u in self.events.unique]
        S, _ = self.indexer.score(evs, evs, 1.0 - self.S_ee, use_type=True)
        np.fill_diagonal(S, 1.0)
        return S

    @cached_property
    def M_ncd_all(self):
        """(n_reference x n_events) NCD on the reference texts (see ref_texts), every event."""
        return ncd.ncd_rect(self.ref_texts, self.events.unique, order=self.order,
                            size_cache=self._size_cache)

    @cached_property
    def M_own_all(self):
        """The reference lines' own distance to every event: NCD, 1 - event-indexing score, or 1 - cosine."""
        if self.similarity_mode == "index":
            return 1.0 - self.index_dims[0]
        if self.similarity_mode == "embed":
            from experiments.common.embed import cosine_rect
            return 1.0 - cosine_rect(self.ref_texts, self.events.unique)
        return self.M_ncd_all

    @cached_property
    def M_all(self):
        """
        The CC's distance (lower = closer), every event. Selectors, A1 rankings and pools all read
        this (through M). With provenance, dialogue lines are scored through their source logs.
        """
        if self.provenance is not None:
            return self._provenance_distance()
        return self.M_own_all

    @cached_property
    def M(self):
        """M_all with non-candidate events set to +inf, so the CC can never pick them."""
        return self.restrict(self.M_all)

    @cached_property
    def masked_dialogue(self):
        return [self.masker.mask(t) for t in self.dialogue.unique]

    @cached_property
    def masked_events(self):
        return [self.masker.mask(t) for t in self.events.unique]

    @cached_property
    def M_masked(self):
        return self.restrict(ncd.ncd_rect(self.masked_dialogue, self.masked_events, order=self.order,
                                          size_cache=self._size_cache))

    @cached_property
    def S_ee(self):
        """(n_events x n_events) similarity, 1 - NCD, between current-session events."""
        S = 1.0 - ncd.ncd_square(self.events.unique)
        np.fill_diagonal(S, 1.0)
        return S

    def dialogue_id(self, d):
        return self.dialogue.id_of(self.dialogue.unique[d])

    @cached_property
    def code_map(self):
        """
        description -> event code, frozen in experiments/pilot/event_codes.csv so codes the
        author used in gold_matches.csv keep pointing at the same event when lines are removed
        from the corpus. Descriptions not in the file get new codes (N000, N001, ...).
        """
        frozen = {}
        if paths.EVENT_CODES.exists():
            import csv
            with open(paths.EVENT_CODES, newline="", encoding="utf-8") as f:
                frozen = {r["description"]: r["code"] for r in csv.DictReader(f)}
        out, n_new = {}, 0
        for desc in self.events.unique:
            if desc in frozen:
                out[desc] = frozen[desc]
            else:
                out[desc] = f"N{n_new:03d}"
                n_new += 1
        return out

    @cached_property
    def code_to_index(self):
        return {self.code_map[d]: i for i, d in enumerate(self.events.unique)}

    def event_code(self, e):
        """Stable short code for an event (see code_map)."""
        return self.code_map[self.events.unique[e]]

    def pair_lines(self, pairs):
        """(event_full, dialogue_full) tuples, the shape compose_pool expects."""
        return [(self.events.short_to_full[self.events.unique[p["e"]]],
                 self.dialogue.short_to_full[self.dialogue.unique[p["d"]]]) for p in pairs]

    def label_suffix(self, full_line):
        desc = data.description_of(full_line)
        for ls in (self.events, self.dialogue):
            if desc in ls.counts:
                return f"[x{ls.counts[desc]}][{ls.visibility[desc]}]"
        return ""
