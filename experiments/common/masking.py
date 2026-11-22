"""
Name masking: replace every way of writing one colonist's name with the same
token (C1, C2, ...), so NCD can no longer match on names alone.

Variants per colonist, built from the bios:
  - "First 'anything' Last"  (dialogue lines write e.g. "Odette 'Odette' O'Neill",
                              "Dillon 'Boyd' Boyd" even when the bios have no nickname)
  - the bios full name, "First Last", first name, last name, nickname
Matching is longest-variant-first, so "Odette 'Odette' O'Neill" becomes "C2",
not "C2 'C2' O'Neill".

If a short variant belongs to more than one colonist (e.g. two Boyds), it is
given to the colonist for whom it is the nickname, otherwise it is dropped
and reported in `ambiguous`.

Optionally (mask_pawn_ids=True) also masks numbered pawn IDs such as
"Turkey38339" -> "P1", consistently.
"""

import re

from experiments.common.data import parse_colonists

_PAWN_ID_RE = re.compile(r"(?<![A-Za-z0-9])([A-Z][A-Za-z]*)(\d{3,})(?![A-Za-z0-9])")
_WORD = r"A-Za-z0-9"


class NameMasker:
    def __init__(self, bios_text, mask_pawn_ids=False, single_token=None):
        """
        single_token: if set (e.g. "C"), every colonist is replaced by this same
        token in mask(), so NCD can't even match on *which* colonist is
        involved. "" removes the names altogether (plus the punctuation they
        leave behind), so NCD can't see *how many* colonists a line names either.
        colonists_in() still tells colonists apart.
        """
        self.colonists = parse_colonists(bios_text)
        self.tokens = {c.full_name: f"C{i + 1}" for i, c in enumerate(self.colonists)}
        self.mask_pawn_ids = mask_pawn_ids
        self.single_token = single_token
        self.ambiguous = []
        self._pawn_tokens = {}

        # variant -> (token, priority); higher priority wins on conflicts
        variants = {}

        def add(text, token, priority):
            text = text.strip()
            if not text:
                return
            if text in variants and variants[text][0] != token:
                if priority > variants[text][1]:
                    variants[text] = (token, priority)
                elif priority == variants[text][1]:
                    variants[text] = (None, priority)   # genuinely ambiguous
                return
            variants.setdefault(text, (token, priority))

        for c in self.colonists:
            tok = self.tokens[c.full_name]
            add(c.full_name, tok, 3)
            add(f"{c.first} {c.last}", tok, 3)
            if c.nick:
                add(c.nick, tok, 2)
            add(c.first, tok, 1)
            add(c.last, tok, 1)

        for text, (tok, _) in list(variants.items()):
            if tok is None:
                self.ambiguous.append(text)
                del variants[text]
        self.variants = {t: tok for t, (tok, _) in variants.items()}

        # "First 'X' Last" with any quoted middle part, then plain variants, longest first.
        patterns = []
        for c in self.colonists:
            patterns.append((len(c.first) + len(c.last) + 100,
                             re.escape(c.first) + r"\s+'[^']*'\s+" + re.escape(c.last),
                             self.tokens[c.full_name]))
        for text, tok in self.variants.items():
            patterns.append((len(text), re.escape(text), tok))
        patterns.sort(key=lambda p: -p[0])

        self._pattern_tokens = [tok for _, _, tok in patterns]
        alternation = "|".join(f"(?P<g{i}>{p})" for i, (_, p, _) in enumerate(patterns))
        self._regex = re.compile(rf"(?<![{_WORD}])(?:{alternation})(?![{_WORD}])")

    def _sub(self, m):
        if self.single_token is not None:
            return self.single_token
        return self._pattern_tokens[int(m.lastgroup[1:])]

    def _pawn_sub(self, m):
        key = m.group(0)
        if key not in self._pawn_tokens:
            self._pawn_tokens[key] = f"P{len(self._pawn_tokens) + 1}"
        return self._pawn_tokens[key]

    def mask(self, text):
        out = self._regex.sub(self._sub, text)
        if self.single_token == "":
            out = _tidy_removed(out)
        if self.mask_pawn_ids:
            out = _PAWN_ID_RE.sub(self._pawn_sub, out)
        return out

    def colonists_in(self, text):
        """Set of colonist tokens mentioned in `text` (used for the actor-match rate)."""
        return {self._pattern_tokens[int(m.lastgroup[1:])] for m in self._regex.finditer(text)}


def _tidy_removed(text):
    """
    Clean up after names were deleted (single_token=""): drop a dangling possessive
    ("'s rifle" -> "rifle"), a comma left right after an opening quote or at the start
    ("said ', I" -> "said 'I"), spaces before punctuation, and doubled spaces.
    """
    text = re.sub(r"(^|[\s(])'s\b\s*", r"\1", text)          # possessive of a removed name
    text = re.sub(r"(^|['(])\s*,\s*", r"\1", text)          # comma right after a removed name
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def mask_names(text, bios, mask_pawn_ids=False):
    """Convenience wrapper. For many lines, build one NameMasker and reuse it (tokens stay consistent)."""
    masker = bios if isinstance(bios, NameMasker) else NameMasker(bios, mask_pawn_ids=mask_pawn_ids)
    return masker.mask(text)
