"""Canonical multiple-myeloma cytogenetic marker values."""

CANONICAL_CYTOGENETIC_MARKERS = (
    'del17p',
    't(4;14)',
    't(11;14)',
    't(14;16)',
    '1q_gain',
    '1q_amp',
    'hyperdiploidy',
    'del13q',
    'MYC rearrangement',
)

_ALIASES = {
    'del(17p13)': 'del17p',
    'del(17p)': 'del17p',
    'tp53/17p deletion': 'del17p',
    '1q21 amplification': '1q_amp',
    '1q21 gain': '1q_gain',
    '1q21 gain/amplification': '1q_gain',
    'fgfr3/igh translocation t(4;14)': 't(4;14)',
    'maf/igh translocation t(14;16)': 't(14;16)',
    'myc rearrangement': 'MYC rearrangement',
}
_CANONICAL_BY_CASEFOLD = {
    marker.casefold(): marker for marker in CANONICAL_CYTOGENETIC_MARKERS
}
_NO_MARKER_VALUES = {
    'standard risk — no high-risk markers detected',
    'standard risk - no high-risk markers detected',
}


def normalise_cytogenetic_markers(value, *, strict=False) -> str:
    """Return a stable, de-duplicated comma-separated marker list.

    UI writes use ``strict=True`` so PatientRecord never receives an answer the
    chooser cannot represent. Import refreshes are deliberately lossless:
    recognized aliases are normalized while unfamiliar source values survive.
    """
    if value in (None, ''):
        return ''
    parts = value if isinstance(value, (list, tuple)) else str(value).split(',')
    normalized = []
    unknown = []
    for part in parts:
        raw = str(part).strip()
        if not raw or raw.casefold() in _NO_MARKER_VALUES:
            continue
        folded = raw.casefold()
        marker = _ALIASES.get(folded) or _CANONICAL_BY_CASEFOLD.get(folded)
        if marker is None:
            unknown.append(raw)
            marker = raw
        if marker not in normalized:
            normalized.append(marker)
    if strict and unknown:
        raise ValueError(f"Unrecognized cytogenetic marker values: {unknown}")
    return ', '.join(normalized)
