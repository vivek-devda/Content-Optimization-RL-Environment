import re


def apply_action(action: str, draft: str, keywords: list[str]) -> str:
    """Route to the correct action function."""
    actions = {
    "refine_structure": refine_structure,
    "add_keywords": add_keywords,
    "remove_redundancy": remove_redundancy,
    "improve_clarity": improve_clarity,
    "improve_hook": improve_hook,
    }

    if action not in actions:
        raise ValueError(f"Unknown action: '{action}'")

    return actions[action](draft, keywords)


def refine_structure(draft: str, keywords: list[str]) -> str:
    """Improve structure and readability."""
    sentences = re.split(r'(?<=[.!?])\s+', draft.strip())
    sentences = [s.strip() for s in sentences if s.strip()]

    # Remove duplicate sentences
    seen = set()
    unique_sentences = []
    for s in sentences:
        norm = s.lower()
        if norm not in seen:
            seen.add(norm)
            unique_sentences.append(s)

    # Rewrite slightly cleaner
    improved = []
    for s in unique_sentences:
        s = s.capitalize()
        s = s.replace("you should try to", "focus on")
        s = s.replace("and actually", "and")
        s = s.replace("kind of", "")
        improved.append(s.strip())

    return " ".join(improved)


def add_keywords(draft: str, keywords: list[str]) -> str:
    """Append missing keywords naturally at the end of the draft."""
    if not keywords:
        return draft

    draft_lower = draft.lower()
    missing = [kw for kw in keywords if kw.lower() not in draft_lower]

    if not missing:
        return draft

    keyword_str = ", ".join(missing)
    return f"{draft.rstrip()} This content covers {keyword_str}."


def remove_redundancy(draft: str, keywords: list[str]) -> str:
    """Remove duplicate sentences from the draft."""
    sentences = re.split(r'(?<=[.!?])\s+', draft.strip())
    seen = set()
    unique = []

    for s in sentences:
        normalized = s.strip().lower()
        if normalized not in seen:
            seen.add(normalized)
            unique.append(s.strip())

    return " ".join(unique)


def improve_clarity(draft: str, keywords: list[str]) -> str:
    """Improve clarity and rewrite sentences slightly."""
    import re

    # Remove filler words
    fillers = [
        r'\bbasically\b', r'\bactually\b', r'\bjust\b',
        r'\bvery\b', r'\breally\b', r'\bquite\b',
        r'\bsort of\b', r'\bkind of\b', r'\byou know\b',
        r'\bin order to\b', r'\bdue to the fact that\b',
    ]

    result = draft
    for filler in fillers:
        result = re.sub(filler, '', result, flags=re.IGNORECASE)

    # Clean spacing
    result = re.sub(r'\s+', ' ', result).strip()

    # 🔥 NEW: basic rewriting
    result = result.replace("you should try to", "focus on")
    result = result.replace("you should", "aim to")

    # Capitalize sentences
    sentences = re.split(r'(?<=[.!?])\s+', result)
    sentences = [s.strip().capitalize() for s in sentences if s.strip()]

    # Remove duplicates
    seen = set()
    unique = []
    for s in sentences:
        if s.lower() not in seen:
            seen.add(s.lower())
            unique.append(s)

    return " ".join(unique)


def improve_hook(draft: str, keywords: list[str]) -> str:
    """Add a stronger opening sentence."""
    if not draft:
        return draft

    # Prevent repeated hooks
    if draft.lower().startswith("did you know"):
        return draft

    hook = "Did you know this could change everything? "
    return hook + draft