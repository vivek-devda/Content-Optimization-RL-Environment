import re


def compute_reward(draft: str, keywords: list[str]) -> float:
    """
    Rule-based reward. Returns a score between 0.0 and 1.0.

    Components:
    - keyword_score  (0.35 weight)
    - structure_score (0.25 weight)
    - clarity_score  (0.25 weight)
    - length_score   (0.15 weight)
    """

    if not draft or not draft.strip():
        return 0.0

    keyword_score = _keyword_coverage(draft, keywords)
    structure_score = _structure_score(draft)
    clarity_score = _clarity_score(draft)

    # ✅ ADD HERE (inside function, after scores)
    length_score = min(len(draft.split()) / 100, 1.0)

    total = (
        0.35 * keyword_score +
        0.25 * structure_score +
        0.25 * clarity_score +
        0.15 * length_score
    )

    return round(min(max(total, 0.0), 1.0), 4)


def _keyword_coverage(draft: str, keywords: list[str]) -> float:
    """Fraction of keywords present in draft."""
    if not keywords:
        return 1.0  # no keywords required = full score

    draft_lower = draft.lower()
    found = sum(1 for kw in keywords if kw.lower() in draft_lower)
    return found / len(keywords)


def _structure_score(draft: str) -> float:
    """
    Score based on:
    - Has multiple sentences
    - Sentences are properly capitalized
    - Ends with punctuation
    """
    sentences = re.split(r'(?<=[.!?])\s+', draft.strip())
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return 0.0

    score = 0.0

    # Reward multiple sentences
    if len(sentences) >= 2:
        score += 0.4

    # Reward proper capitalization
    capitalized = sum(1 for s in sentences if s and s[0].isupper())
    score += 0.3 * (capitalized / len(sentences))

    # Reward ending punctuation
    if re.search(r'[.!?]$', draft.strip()):
        score += 0.3

    return min(score, 1.0)


def _clarity_score(draft: str) -> float:
    """Penalize filler words and repeated sentences."""
    fillers = [
        'basically', 'actually', 'just', 'very', 'really',
        'quite', 'sort of', 'kind of', 'you know', 'in order to',
        'due to the fact that'
    ]

    words = draft.lower().split()
    if not words:
        return 0.0

    draft_lower = draft.lower()
    filler_count = sum(1 for f in fillers if f in draft_lower)
    filler_penalty = min(filler_count / 10, 0.5)

    # Repetition penalty
    sentences = re.split(r'(?<=[.!?])\s+', draft.strip())
    unique = set(s.strip().lower() for s in sentences)
    repetition_penalty = 0.0
    if sentences:
        repetition_penalty = 1.0 - (len(unique) / len(sentences))

    score = 1.0 - filler_penalty - (0.3 * repetition_penalty)
    return round(min(max(score, 0.0), 1.0), 4)