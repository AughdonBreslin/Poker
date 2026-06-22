import multiprocessing
import os
import pickle
import tempfile
from functools import lru_cache
from itertools import combinations, permutations
from typing import Sequence

from treys import Card as TreysCard, Evaluator

from card import Card, Rank, Suit
from hand import Hand

_evaluator = Evaluator()

_SUITS: list[Suit] = sorted(Suit, key=lambda s: s.value)  # [CLUB, DIAMOND, HEART, SPADE]


def canonical_key(hands: Sequence[Hand]) -> tuple[tuple, list[int]]:
    """
    Suit-isomorphic canonical key for a set of hole card hands.

    Tries all N! orderings of hands, assigns suit indices in order of first
    appearance (reading each hand's cards in descending rank order), and
    returns the lexicographically smallest resulting key.

    Returns:
        key:     Immutable tuple usable as a dict key.
        mapping: mapping[canonical_idx] = actual_player_idx
    """
    best_key: tuple | None = None
    best_mapping: list[int] | None = None

    for perm in permutations(range(len(hands))):
        suit_map: dict[Suit, int] = {}
        next_idx = 0
        result: list[tuple] = []
        for i in perm:
            hand_key = []
            for card in hands[i]:  # Hand iterates descending by rank
                if card.suit not in suit_map:
                    suit_map[card.suit] = next_idx
                    next_idx += 1
                hand_key.append((card.rank.value[1], suit_map[card.suit]))
            result.append(tuple(hand_key))
        key = tuple(result)
        if best_key is None or key < best_key:
            best_key = key
            best_mapping = list(perm)

    return best_key, best_mapping  # type: ignore[return-value]


def _free_suits(hands: Sequence[Hand]) -> list[Suit]:
    """Suits that appear in no hole card — interchangeable on the board."""
    pinned = {card.suit for hand in hands for card in hand}
    return [s for s in _SUITS if s not in pinned]


def _runout_sorted_key(runout: tuple[Card, ...], suit_map: dict[Suit, Suit]) -> tuple:
    return tuple(sorted(
        (c.rank.value[1], suit_map.get(c.suit, c.suit).value)
        for c in runout
    ))


def _is_canonical_runout(runout: tuple[Card, ...], free_suits: list[Suit]) -> bool:
    """
    A runout is canonical iff its sorted (rank, suit) sequence is lexicographically
    minimal across all permutations of the free suits. This correctly handles cases
    where two cards of the same rank appear in different free suits — swapping those
    suits produces the same card set, shrinking the orbit below P(n_free, k_used).
    """
    if not free_suits:
        return True
    own_key = _runout_sorted_key(runout, {})
    for perm in permutations(free_suits):
        suit_map = dict(zip(free_suits, perm))
        if _runout_sorted_key(runout, suit_map) < own_key:
            return False
    return True


def _runout_weight(runout: tuple[Card, ...], free_suits: list[Suit]) -> int:
    """
    Orbit size of this runout under free-suit permutations — i.e., how many
    distinct card sets are isomorphic to it. Equals |orbit| = n! / |stabilizer|.
    Computed by enumerating all permutations and counting distinct results.
    """
    if not free_suits:
        return 1
    orbit: set[tuple] = set()
    for perm in permutations(free_suits):
        suit_map = dict(zip(free_suits, perm))
        orbit.add(_runout_sorted_key(runout, suit_map))
    return len(orbit)


def _abstract_pattern(runout: tuple[Card, ...], free_suits: list[Suit]) -> tuple:
    """
    Abstract suit pattern: for each rank that has free-suit cards in the runout,
    record the sorted tuple of free-suit values. Groups are ordered by rank.

    Two runouts share a pattern iff their free-suit cards have the same
    multiset structure across ranks — meaning they're in the same orbit class.
    """
    free_set = set(free_suits)
    rank_suits: dict[int, list[str]] = {}
    for card in runout:
        if card.suit in free_set:
            r = card.rank.value[1]
            if r not in rank_suits:
                rank_suits[r] = []
            rank_suits[r].append(card.suit.value)
    return tuple(tuple(sorted(suits)) for _, suits in sorted(rank_suits.items()))


_canonical_cache: dict[tuple, tuple[bool, int]] = {}


def _canonical_info(runout: tuple[Card, ...], free_suits: list[Suit]) -> tuple[bool, int]:
    """
    Returns (is_canonical, weight) for a runout, using a cache keyed on
    the abstract suit pattern. Cache miss triggers full permutation enumeration;
    subsequent runouts with the same pattern are O(1).
    """
    if not free_suits:
        return True, 1
    pattern = _abstract_pattern(runout, free_suits)
    if pattern in _canonical_cache:
        return _canonical_cache[pattern]
    free_vals = tuple(s.value for s in free_suits)
    orbit: set[tuple] = set()
    is_canonical = True
    for perm in permutations(free_vals):
        perm_map = dict(zip(free_vals, perm))
        permuted = tuple(tuple(sorted(perm_map[v] for v in group)) for group in pattern)
        orbit.add(permuted)
        if permuted < pattern:
            is_canonical = False
    result = (is_canonical, len(orbit))
    _canonical_cache[pattern] = result
    return result


def preflop_equity_iso(hands: Sequence[Hand], remaining: list[Card]) -> list[float]:
    """
    Exact preflop equities via suit-isomorphic weighted runout enumeration.

    Only evaluates canonical runouts (a ~(n_free)!-fold reduction) and
    multiplies each by its weight so the total equals C(remaining, 5).
    Uses treys for O(1) hand evaluation via precomputed lookup tables.
    """
    free = _free_suits(hands)
    equities = [0.0] * len(hands)
    total_weight = 0

    # Pre-convert to treys integers once — avoids per-runout string parsing
    treys_hands = [[TreysCard.new(repr(c)) for c in hand] for hand in hands]
    treys_remaining = [TreysCard.new(repr(c)) for c in remaining]

    # Zip two combinations iterators: Card tuples for canonical check,
    # treys int tuples for evaluation — both iterate in identical order
    for runout, treys_runout in zip(
        combinations(remaining, 5),
        combinations(treys_remaining, 5),
    ):
        is_canonical, w = _canonical_info(runout, free)
        if not is_canonical:
            continue
        total_weight += w
        treys_board = list(treys_runout)
        # treys: lower score = stronger hand
        scores = [_evaluator.evaluate(treys_board, th) for th in treys_hands]
        best = min(scores)
        winners = [p for p, s in enumerate(scores) if s == best]
        share = w / len(winners)
        for p in winners:
            equities[p] += share

    return [e / total_weight for e in equities]


@lru_cache(maxsize=1)
def _all_cards() -> list[Card]:
    # Cached: built once per process. Treat the returned list as read-only.
    return [Card(rank, suit) for rank in Rank for suit in Suit]


def _equity_worker(args: tuple) -> tuple[tuple, list[float]]:
    """Top-level worker: reconstruct hands/remaining from strings, compute equity."""
    key, hand_strs, remaining_strs = args
    hands = [Hand(s) for s in hand_strs]
    remaining = [Card(s) for s in remaining_strs]
    return key, preflop_equity_iso(hands, remaining)


def _atomic_pickle_dump(obj, path: str) -> None:
    """
    Pickle obj to path atomically: write to a temp file in the same directory,
    then os.replace() it into place. A crash mid-write can never leave a
    truncated/corrupt checkpoint at path.
    """
    directory = os.path.dirname(os.path.abspath(path))
    fd, tmp_path = tempfile.mkstemp(dir=directory, suffix='.tmp')
    try:
        with os.fdopen(fd, 'wb') as f:
            pickle.dump(obj, f)
        os.replace(tmp_path, path)
    except BaseException:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def _canonical_repr(hand_index_combo: tuple) -> tuple | None:
    """
    Worker for the enumeration phase: validate a combo of hole-card index pairs
    and return (canonical_key, mapping, hand_index_combo), or None if the pairs
    share a card. Runs canonical_key — the expensive part of enumeration — in
    parallel across the pool.
    """
    flat = [idx for pair in hand_index_combo for idx in pair]
    if len(flat) != len(set(flat)):
        return None
    all_cards = _all_cards()
    hands = [Hand([all_cards[i] for i in pair]) for pair in hand_index_combo]
    key, mapping = canonical_key(hands)
    return key, mapping, hand_index_combo


def _enumerate_canonical_tasks(combos, seen_keys: set, pool, chunksize: int = 2000) -> list[tuple]:
    """
    Deduplicate canonical matchups across `combos` (an iterable of
    num_players-tuples of card-index pairs), keeping one representative task per
    unique canonical key not already in seen_keys.

    canonical_key is computed in parallel via `pool`; deduplication and the
    (cheap) string-payload construction for the kept representatives happen here
    in the caller. Any representative of a canonical key yields identical equity,
    so unordered results are safe. Mutates seen_keys with the keys it accepts.
    """
    all_cards = _all_cards()
    tasks: list[tuple] = []
    for result in pool.imap_unordered(_canonical_repr, combos, chunksize=chunksize):
        if result is None:
            continue
        key, mapping, hand_index_combo = result
        if key in seen_keys:
            continue
        seen_keys.add(key)

        flat = [idx for pair in hand_index_combo for idx in pair]
        used = set(flat)
        remaining = [all_cards[i] for i in range(52) if i not in used]
        hands = [Hand([all_cards[i] for i in pair]) for pair in hand_index_combo]
        canonical_hands = [hands[mapping[i]] for i in range(len(hands))]

        hand_strs = [''.join(repr(c) for c in hand) for hand in canonical_hands]
        remaining_strs = [repr(c) for c in remaining]
        tasks.append((key, hand_strs, remaining_strs))
    return tasks


def build_lookup_table(
    num_players: int = 2,
    checkpoint_path: str | None = None,
    num_workers: int | None = None,
    checkpoint_every: int = 500,
) -> dict[tuple, list[float]]:
    """
    Build the complete suit-isomorphic preflop equity lookup table.

    Enumerates all valid combinations of num_players hole card hands,
    deduplicates via canonical_key, and computes exact equity once per
    unique canonical matchup. A single multiprocessing Pool parallelizes both
    the enumeration (canonical_key) and the equity computation.

    Saves an atomic checkpoint every `checkpoint_every` completed entries when
    checkpoint_path is provided, and resumes from it if it already exists.
    """
    table: dict[tuple, list[float]] = {}

    if checkpoint_path and os.path.exists(checkpoint_path):
        with open(checkpoint_path, 'rb') as f:
            table = pickle.load(f)
        print(f"Resumed from checkpoint: {len(table)} entries.")

    card_index_pairs = list(combinations(range(52), 2))
    seen_keys: set[tuple] = set(table.keys())

    with multiprocessing.Pool(processes=num_workers) as pool:
        combos = combinations(card_index_pairs, num_players)
        tasks = _enumerate_canonical_tasks(combos, seen_keys, pool)

        total = len(tasks)
        print(f"Tasks to compute: {total}  (workers: {num_workers or multiprocessing.cpu_count()})")

        completed = 0
        for key, equities in pool.imap_unordered(_equity_worker, tasks):
            table[key] = equities
            completed += 1
            print(f"  {completed}/{total}", end='\r', flush=True)
            if checkpoint_path and completed % checkpoint_every == 0:
                _atomic_pickle_dump(table, checkpoint_path)

    print()  # newline after \r progress line
    if checkpoint_path:
        _atomic_pickle_dump(table, checkpoint_path)
        print(f"Saved: {len(table)} entries → {checkpoint_path}")

    return table


def save_table(table: dict[tuple, list[float]], path: str) -> None:
    with open(path, 'wb') as f:
        pickle.dump(table, f)


def load_table(path: str) -> dict[tuple, list[float]]:
    with open(path, 'rb') as f:
        return pickle.load(f)


def lookup(hands: Sequence[Hand], table: dict[tuple, list[float]]) -> list[float]:
    """
    Look up preflop equities for actual hands, remapping canonical equities
    back to actual player indices.
    """
    key, mapping = canonical_key(hands)
    canonical_equities = table[key]
    equities = [0.0] * len(hands)
    for canonical_idx, actual_idx in enumerate(mapping):
        equities[actual_idx] = canonical_equities[canonical_idx]
    return equities
