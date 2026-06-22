import multiprocessing
import pickle
from itertools import combinations, islice
from math import comb, factorial

import pytest

from card import Card, Suit
from hand import Hand
from preflop_equity import (
    _free_suits,
    _is_canonical_runout,
    _runout_weight,
    _all_cards,
    _atomic_pickle_dump,
    _enumerate_canonical_tasks,
    canonical_key,
    preflop_equity_iso,
)

CLUB, DIAMOND, HEART, SPADE = Suit.CLUB, Suit.DIAMOND, Suit.HEART, Suit.SPADE


class TestCanonicalKey:
    def test_suit_permutation_gives_same_key(self):
        # AcKd vs QsQh and AcKs vs QdQh differ only by swapping d↔s
        hands_a = [Hand('AcKd'), Hand('QsQh')]
        hands_b = [Hand('AcKs'), Hand('QdQh')]
        assert canonical_key(hands_a)[0] == canonical_key(hands_b)[0]

    def test_player_order_gives_same_key(self):
        hands = [Hand('AhKh'), Hand('QcQd')]
        reversed_hands = [Hand('QcQd'), Hand('AhKh')]
        assert canonical_key(hands)[0] == canonical_key(reversed_hands)[0]

    def test_suited_ak_independent_suits_isomorphic(self):
        # AhKh vs QcQd and AsKs vs QhQd: both AK suited, QQ offsuit, no suit overlap
        hands_a = [Hand('AhKh'), Hand('QcQd')]
        hands_b = [Hand('AsKs'), Hand('QhQd')]
        assert canonical_key(hands_a)[0] == canonical_key(hands_b)[0]

    def test_suit_overlap_differs_from_no_overlap(self):
        # AhKh vs QhQd: QQ shares AK's suit (h) — flush draw dominated
        # AhKh vs QcQd: no suit overlap
        hands_overlap = [Hand('AhKh'), Hand('QhQd')]
        hands_independent = [Hand('AhKh'), Hand('QcQd')]
        assert canonical_key(hands_overlap)[0] != canonical_key(hands_independent)[0]

    def test_offsuit_ak_with_all_different_suits(self):
        # AcKd vs QsQh: all 4 suits appear → 0 free suits
        # AhKs vs QcQd: all 4 suits appear → 0 free suits, but same pattern?
        # These are isomorphic: AK offsuit, QQ offsuit, no shared suits between hands
        hands_a = [Hand('AcKd'), Hand('QsQh')]
        hands_b = [Hand('AhKs'), Hand('QcQd')]
        assert canonical_key(hands_a)[0] == canonical_key(hands_b)[0]

    def test_player_mapping_is_inverse_of_canonical_order(self):
        hands = [Hand('AhKh'), Hand('QcQd')]
        key, mapping = canonical_key(hands)
        # mapping[canonical_idx] = actual_idx; all actual indices must appear
        assert sorted(mapping) == list(range(len(hands)))


class TestFreeSuits:
    def test_all_suits_pinned(self):
        # AcKd vs QsQh uses all 4 suits
        hands = [Hand('AcKd'), Hand('QsQh')]
        assert _free_suits(hands) == []

    def test_one_free_suit(self):
        # AsAh vs KdKh: pinned = {s, h, d} → free = [c]
        hands = [Hand('AsAh'), Hand('KdKh')]
        assert _free_suits(hands) == [CLUB]

    def test_two_free_suits(self):
        # AhKh vs QhQd: pinned = {h, d} → free = [c, s]
        hands = [Hand('AhKh'), Hand('QhQd')]
        assert _free_suits(hands) == [CLUB, SPADE]

    def test_three_free_suits(self):
        # AhKh vs 2h3h: only h is pinned → free = [c, d, s]
        hands = [Hand('AhKh'), Hand('2h3h')]
        assert _free_suits(hands) == [CLUB, DIAMOND, SPADE]


class TestIsCanonicalRunout:
    def _cards(self, *names: str) -> tuple[Card, ...]:
        return tuple(Card(n) for n in names)

    def test_no_free_suits_always_canonical(self):
        runout = self._cards('2h', '3h', '4h', '5h', '6h')
        assert _is_canonical_runout(runout, []) is True

    def test_first_free_suit_is_club(self):
        # free = [CLUB, DIAMOND]: first new free suit must be club
        free = [CLUB, DIAMOND]
        assert _is_canonical_runout(self._cards('2c', '3h', '4h', '5h', '6h'), free) is True
        assert _is_canonical_runout(self._cards('2d', '3h', '4h', '5h', '6h'), free) is False

    def test_second_free_suit_is_diamond(self):
        free = [CLUB, DIAMOND]
        # c then d → canonical
        assert _is_canonical_runout(self._cards('2c', '3d', '4h', '5h', '6h'), free) is True
        # c then s would not be canonical if d and s are both free... but here free=[c,d]
        # so s is pinned; any s card is ignored in the check
        assert _is_canonical_runout(self._cards('2c', '3s', '4h', '5h', '6h'), free) is True

    def test_order_determined_by_rank_sort(self):
        # Sort order is by rank first: lower rank comes first
        # 2d < 3c by rank → 2d is first card seen; d is not CLUB → not canonical
        free = [CLUB, DIAMOND]
        assert _is_canonical_runout(self._cards('2d', '3c', '4h', '5h', '6h'), free) is False
        # 2c < 3d by rank → 2c first, c=CLUB ✓
        assert _is_canonical_runout(self._cards('2c', '3d', '4h', '5h', '6h'), free) is True

    def test_same_rank_different_free_suit_uses_suit_tiebreak(self):
        # Two cards of same rank: sort by suit value ('c' < 'd')
        free = [CLUB, DIAMOND]
        # Ac and Ad: sort → Ac before Ad → c first (CLUB ✓) → canonical
        assert _is_canonical_runout(self._cards('Ac', 'Ad', '4h', '5h', '6h'), free) is True
        # Ad and Ac in tuple: sorted still puts Ac first → canonical
        assert _is_canonical_runout(self._cards('Ad', 'Ac', '4h', '5h', '6h'), free) is True

    def test_same_rank_lex_min_picks_single_canonical(self):
        # {2c, 2d, 3c}: canonical — no permutation gives a lex-smaller sorted sequence
        # {2c, 2d, 3d}: NOT canonical — c↔d swap gives {2c, 2d, 3c} which is lex-smaller
        free = [CLUB, DIAMOND, SPADE]
        assert _is_canonical_runout(self._cards('2c', '2d', '3c', '5h', '6h'), free) is True
        assert _is_canonical_runout(self._cards('2c', '2d', '3d', '5h', '6h'), free) is False


class TestRunoutWeight:
    def test_no_free_suits(self):
        runout = tuple(Card(n) for n in ['2h', '3h', '4h', '5h', '6h'])
        assert _runout_weight(runout, []) == 1

    def test_one_free_suit_used(self):
        # only one distinct free suit used → orbit size = 2 (can use either free suit)
        free = [CLUB, DIAMOND]
        runout = tuple(Card(n) for n in ['2c', '3h', '4h', '5h', '6h'])
        assert _runout_weight(runout, free) == 2

    def test_two_distinct_free_suits_used(self):
        # two distinct free suits, all cards at different ranks → orbit size = 2
        free = [CLUB, DIAMOND]
        runout = tuple(Card(n) for n in ['2c', '3d', '4h', '5h', '6h'])
        assert _runout_weight(runout, free) == 2

    def test_three_free_suits_all_at_different_ranks(self):
        # three distinct free suits, each at a unique rank → full orbit = 6
        free = [CLUB, DIAMOND, SPADE]
        runout = tuple(Card(n) for n in ['2c', '3d', '4s', '5h', '6h'])
        assert _runout_weight(runout, free) == 6

    def test_three_free_suits_one_used(self):
        # one free suit used → orbit size = 3
        free = [CLUB, DIAMOND, SPADE]
        runout = tuple(Card(n) for n in ['2c', '3h', '4h', '5h', '6h'])
        assert _runout_weight(runout, free) == 3

    def test_same_rank_two_free_suits_shrinks_orbit(self):
        # {2c, 2d, 4s}: swapping c↔d gives the same set → orbit size = 3, not 6
        free = [CLUB, DIAMOND, SPADE]
        runout = tuple(Card(n) for n in ['2c', '2d', '4s', '5h', '6h'])
        assert _runout_weight(runout, free) == 3


class TestPreflopEquityIso:
    def _remaining(self, hands: list[Hand]) -> list[Card]:
        used = {repr(card) for hand in hands for card in hand}
        return [c for c in _all_cards() if repr(c) not in used]

    def test_equities_sum_to_one(self):
        hands = [Hand('AhKh'), Hand('QcQd')]
        remaining = self._remaining(hands)
        equities = preflop_equity_iso(hands, remaining)
        assert sum(equities) == pytest.approx(1.0)

    def test_symmetric_hands_split_evenly(self):
        # AhKh vs AcKc: both suited AK in different suits — perfectly symmetric
        hands = [Hand('AhKh'), Hand('AcKc')]
        remaining = self._remaining(hands)
        equities = preflop_equity_iso(hands, remaining)
        assert equities[0] == pytest.approx(equities[1])
        assert equities[0] == pytest.approx(0.5)

    def test_isomorphic_hands_give_same_equities(self):
        # AhKh vs QcQd and AsKs vs QdQh are isomorphic — same equities
        hands_a = [Hand('AhKh'), Hand('QcQd')]
        hands_b = [Hand('AsKs'), Hand('QdQh')]
        eq_a = preflop_equity_iso(hands_a, self._remaining(hands_a))
        eq_b = preflop_equity_iso(hands_b, self._remaining(hands_b))
        assert eq_a[0] == pytest.approx(eq_b[0])
        assert eq_a[1] == pytest.approx(eq_b[1])

    def test_total_weight_equals_combinations(self):
        # Verify the weighted enumeration covers C(remaining, 5) total runouts
        from preflop_equity import _free_suits, _is_canonical_runout, _runout_weight
        hands = [Hand('AhKh'), Hand('2h3h')]  # 3 free suits → 6x reduction
        remaining = self._remaining(hands)
        total_weight = sum(
            _runout_weight(runout, _free_suits(hands))
            for runout in combinations(remaining, 5)
            if _is_canonical_runout(runout, _free_suits(hands))
        )
        assert total_weight == comb(len(remaining), 5)


class TestAtomicPickleDump:
    def test_writes_and_reads_back(self, tmp_path):
        p = tmp_path / "table.pkl"
        obj = {("a",): [0.5, 0.5]}
        _atomic_pickle_dump(obj, str(p))
        with open(p, "rb") as f:
            assert pickle.load(f) == obj

    def test_overwrite_leaves_no_temp_files(self, tmp_path):
        p = tmp_path / "table.pkl"
        _atomic_pickle_dump({"v": 1}, str(p))
        _atomic_pickle_dump({"v": 2}, str(p))
        with open(p, "rb") as f:
            assert pickle.load(f) == {"v": 2}
        # Atomic replace must not leave temp scratch files behind
        assert [f.name for f in tmp_path.iterdir()] == ["table.pkl"]


class TestParallelEnumeration:
    def _serial_keys(self, combos, all_cards):
        keys = set()
        for combo in combos:
            flat = [i for pair in combo for i in pair]
            if len(flat) != len(set(flat)):
                continue
            hands = [Hand([all_cards[i] for i in pair]) for pair in combo]
            keys.add(canonical_key(hands)[0])
        return keys

    def test_parallel_dedup_matches_serial(self):
        all_cards = _all_cards()
        pairs = list(combinations(range(52), 2))
        combos = list(islice(combinations(pairs, 2), 5000))

        expected = self._serial_keys(combos, all_cards)

        with multiprocessing.Pool(2) as pool:
            tasks = _enumerate_canonical_tasks(iter(combos), set(), pool)

        produced = [t[0] for t in tasks]
        assert len(produced) == len(set(produced))  # no duplicate keys
        assert set(produced) == expected

    def test_skips_keys_already_seen(self):
        all_cards = _all_cards()
        pairs = list(combinations(range(52), 2))
        combos = list(islice(combinations(pairs, 2), 2000))
        all_keys = self._serial_keys(combos, all_cards)

        with multiprocessing.Pool(2) as pool:
            tasks = _enumerate_canonical_tasks(iter(combos), set(all_keys), pool)

        assert tasks == []  # everything already seen → nothing to compute
