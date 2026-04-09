import difflib

from thefuzz import fuzz

from ibge.config import FUZZY_THRESHOLD
from ibge.models import MunicipioIBGE
from ibge.text import normalize


def _word_edit_acceptable(word_input: str, word_candidate: str) -> bool:
    if word_input == word_candidate:
        return True

    ops = difflib.SequenceMatcher(None, word_input, word_candidate).get_opcodes()

    inserts = sum(op[4] - op[3] for op in ops if op[0] == "insert")
    deletes = sum(op[2] - op[1] for op in ops if op[0] == "delete")
    replaces = sum(
        max(op[2] - op[1], op[4] - op[3]) for op in ops if op[0] == "replace"
    )
    total_ops = inserts + deletes + replaces

    is_short_word = len(word_candidate) <= 5 or len(word_input) <= 6
    if is_short_word:
        if inserts + deletes > 0:
            return False
        if replaces > 1:
            return False

    return total_ops <= 2


def _words_alignment_ok(input_normalized: str, candidate: str) -> bool:
    words_input = input_normalized.split()
    words_candidate = candidate.split()

    if abs(len(words_input) - len(words_candidate)) > 1:
        return False

    return all(
        _word_edit_acceptable(w_in, w_cand)
        for w_in, w_cand in zip(words_input, words_candidate)
    )


def _find_best_fuzzy_match(
    normalized_name: str,
    candidates: list[str],
    lookup: dict[str, MunicipioIBGE],
) -> MunicipioIBGE | None:
    best_name: str | None = None
    best_score: int = 0

    for candidate in candidates:
        score = fuzz.ratio(normalized_name, candidate)
        if score < FUZZY_THRESHOLD or score <= best_score:
            continue
        if _words_alignment_ok(normalized_name, candidate):
            best_score = score
            best_name = candidate

    if best_name is None:
        return None
    return lookup[best_name]


def match_municipio(
    nome_input: str,
    lookup: dict[str, MunicipioIBGE],
    nomes_normalizados: list[str],
) -> tuple[MunicipioIBGE | None, str]:
    normalized = normalize(nome_input)

    if normalized in lookup:
        return lookup[normalized], "OK"

    match = _find_best_fuzzy_match(normalized, nomes_normalizados, lookup)
    if match is not None:
        return match, "OK"

    return None, "NAO_ENCONTRADO"
