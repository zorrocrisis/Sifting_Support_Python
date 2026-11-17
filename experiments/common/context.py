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
    _size_cache: dict = field(default_factory=dict, repr=False)

    @cached_property
    def events(self):
        return data.load_session_events(self.events_path or paths.SESSION2_EVENTS, name=self.session_name)

    @cached_property
    def dialogue(self):
        return data.load_past_dialogue(self.dialogue_path or paths.PAST_DIALOGUE)

    @cached_property
    def bios_text(self):
        return data.load_bios_text(self.bios_path or paths.BIOS)

    @cached_property
    def masker(self):
        return NameMasker(self.bios_text, mask_pawn_ids=self.mask_pawn_ids, single_token=self.single_token)

    @cached_property
    def M(self):
        """(n_dialogue x n_events) NCD on raw descriptions."""
        return ncd.ncd_rect(self.dialogue.unique, self.events.unique, order=self.order,
                            size_cache=self._size_cache)

    @cached_property
    def masked_dialogue(self):
        return [self.masker.mask(t) for t in self.dialogue.unique]

    @cached_property
    def masked_events(self):
        return [self.masker.mask(t) for t in self.events.unique]

    @cached_property
    def M_masked(self):
        return ncd.ncd_rect(self.masked_dialogue, self.masked_events, order=self.order,
                            size_cache=self._size_cache)

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
