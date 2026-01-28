from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Iterable, List, Optional


def normalize_name(s: str) -> str:
    """Normalize a name for comparison: lowercase, remove extra whitespace, standardize separators."""
    # Convert to lowercase and replace common separators with spaces
    s = (s or "").strip().lower()
    s = s.replace("_", " ").replace("-", " ").replace("=", " ")
    # Remove extra whitespace
    return " ".join(s.split())


def extract_key_terms(s: str) -> set:
    """Extract key terms from a name for partial matching."""
    normalized = normalize_name(s)
    # Split into words and remove very short words (except pH, mM, etc.)
    words = normalized.split()
    # Keep words that are meaningful (length >= 2 or special units/terms)
    key_terms = set()
    for word in words:
        # Keep all words with 3+ chars, or 2-char words that look like units/numbers
        if len(word) >= 3 or (len(word) == 2 and (word.isdigit() or word in ['ph', 'mm', 'um', 'nm'])):
            key_terms.add(word)
    return key_terms


def similarity(a: str, b: str) -> float:
    """
    Calculate similarity between two strings using multiple strategies:
    1. Exact match (after normalization)
    2. Substring containment
    3. Key term overlap
    4. Sequence similarity
    Returns the best score from all strategies.
    """
    a_norm = normalize_name(a)
    b_norm = normalize_name(b)
    
    if not a_norm or not b_norm:
        return 0.0
    
    # Strategy 1: Exact match after normalization
    if a_norm == b_norm:
        return 1.0
    
    # Strategy 2: Substring containment (case-insensitive)
    # If query is fully contained in candidate, give high score
    if a_norm in b_norm:
        # Score based on how much of the candidate the query covers
        containment_score = len(a_norm) / len(b_norm)
        # Boost the score significantly for substring matches
        containment_score = 0.7 + (containment_score * 0.3)
    elif b_norm in a_norm:
        containment_score = len(b_norm) / len(a_norm)
        containment_score = 0.7 + (containment_score * 0.3)
    else:
        containment_score = 0.0
    
    # Strategy 3: Key term overlap
    # Check how many important words match
    a_terms = extract_key_terms(a)
    b_terms = extract_key_terms(b)
    
    if a_terms and b_terms:
        intersection = a_terms & b_terms
        union = a_terms | b_terms
        if union:
            term_overlap_score = len(intersection) / len(union)
            # If all query terms are in candidate, boost score
            if a_terms and a_terms.issubset(b_terms):
                term_overlap_score = max(term_overlap_score, 0.75)
        else:
            term_overlap_score = 0.0
    else:
        term_overlap_score = 0.0
    
    # Strategy 4: Traditional sequence matching (handles typos well)
    sequence_score = SequenceMatcher(None, a_norm, b_norm).ratio()
    
    # Return the best score from all strategies
    return max(containment_score, term_overlap_score, sequence_score)


@dataclass
class Match:
    query: str
    candidate: str
    score: float


def best_match(query: str, candidates: Iterable[str], min_score: float = 0.72) -> Optional[Match]:
    best: Optional[Match] = None
    for c in candidates:
        sc = similarity(query, c)
        if best is None or sc > best.score:
            best = Match(query=query, candidate=c, score=sc)
    if best is None or best.score < min_score:
        return None
    return best


def top_matches(query: str, candidates: Iterable[str], n: int = 5) -> List[Match]:
    ms: List[Match] = []
    for c in candidates:
        ms.append(Match(query=query, candidate=c, score=similarity(query, c)))
    ms.sort(key=lambda m: m.score, reverse=True)
    return ms[:n]
