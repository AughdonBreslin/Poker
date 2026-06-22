import sys
import time

from dataclasses import dataclass
from itertools import combinations
from typing import Any, Iterable, List, Sequence

import evaluator as ev
from card import Card, Rank, Suit, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, JACK, QUEEN, KING, ACE, CLUB, DIAMOND, HEART, SPADE
from hand import Hand
from preflop_equity import preflop_equity_iso
from table import Table


@dataclass
class BoardSnapshot:
    board: tuple[Card, ...]
    strengths: list[ev.HandStrength]
    ranking: list[list[int]]
    positions: list[int]
    winners: list[int]


def _remaining_cards(table: Table) -> list[Card]:
    return list(table.board.deck.deck)


def _normalize_out(runout: tuple[Card, ...]) -> Card | tuple[Card, ...]:
    if len(runout) == 1:
        return runout[0]
    return runout


def _rank_players(strengths: Sequence[ev.HandStrength]) -> list[list[int]]:
    ordered_players = sorted(range(len(strengths)), key=lambda player: strengths[player], reverse=True)
    ranking: list[list[int]] = []
    for player in ordered_players:
        if not ranking or strengths[player] != strengths[ranking[-1][0]]:
            ranking.append([player])
        else:
            ranking[-1].append(player)
    return ranking


def _evaluate_board(hands: Sequence[Hand], board_cards: Sequence[Card]) -> BoardSnapshot:
    strengths = [ev.determineHandStrength(hand.hand, list(board_cards)) for hand in hands]
    ranking = _rank_players(strengths)
    positions = [0 for _ in hands]
    for position, tied_players in enumerate(ranking):
        for player in tied_players:
            positions[player] = position
    return BoardSnapshot(
        board=tuple(board_cards),
        strengths=strengths,
        ranking=ranking,
        positions=positions,
        winners=ranking[0],
    )


def _runout_snapshots(table: Table, cards_to_draw: int) -> Iterable[tuple[tuple[Card, ...], BoardSnapshot]]:
    current_board = list(table.board.board)
    for runout in combinations(_remaining_cards(table), cards_to_draw):
        yield runout, _evaluate_board(table.hands, current_board + list(runout))


def _equity_for_runouts(table: Table, cards_to_draw: int, *, track_outs: bool = True) -> tuple[list[float], list[list[Card | tuple[Card, ...]]]]:
    equities = [0.0 for _ in table.hands]
    outs: list[list[Card | tuple[Card, ...]]] = [[] for _ in table.hands]
    total_possibilities = 0
    current_board = list(table.board.board)
    hands = list(table.hands)
    remaining_cards = _remaining_cards(table)

    for runout in combinations(remaining_cards, cards_to_draw):
        total_possibilities += 1
        board_cards = current_board + list(runout)
        strength_keys = [ev.hand_strength_key(hand.hand, board_cards) for hand in hands]
        winning_key = max(strength_keys)
        winners = [player for player, strength_key in enumerate(strength_keys) if strength_key == winning_key]
        equity_share = 1 / len(winners)
        normalized_runout = _normalize_out(runout)
        for winner in winners:
            equities[winner] += equity_share
            if track_outs:
                outs[winner].append(normalized_runout)

    if total_possibilities > 0:
        equities = [equity / total_possibilities for equity in equities]
    return equities, outs


def _normalize_equities(equities: list[float], total_possibilities: int) -> list[float]:
    if total_possibilities > 0:
        return [equity / total_possibilities for equity in equities]
    return equities


def _analysis_result(table: Table, current_snapshot: BoardSnapshot, equities: list[float], outs: list[list[Any]]) -> dict[str, Any]:
    return {
        'street': len(table.board),
        'equities': equities,
        'outs': outs,
        'current_strengths': current_snapshot.strengths,
        'current_ranking': current_snapshot.ranking,
        'current_positions': current_snapshot.positions,
        'current_winners': current_snapshot.winners,
    }


def turn_equity_analysis(table: Table) -> dict[str, Any]:
    if len(table.board) != 4:
        raise UserWarning("Not four cards on the board. %s", table.board)

    current_board = list(table.board.board)
    remaining_cards = _remaining_cards(table)
    current_snapshot = _evaluate_board(table.hands, current_board)
    equities = [0.0 for _ in table.hands]
    outs: list[list[Card]] = [[] for _ in table.hands]
    current_positions = current_snapshot.positions
    current_winners = set(current_snapshot.winners)
    position_improvers: list[list[Card]] = [[] for _ in table.hands]
    winning_outs: list[list[Card]] = [[] for _ in table.hands]
    river_details: dict[Card, dict[str, Any]] = {}
    total_possibilities = 0

    for river_card in remaining_cards:
        snapshot = _evaluate_board(table.hands, current_board + [river_card])
        total_possibilities += 1
        equity_share = 1 / len(snapshot.winners)
        for winner in snapshot.winners:
            equities[winner] += equity_share
            outs[winner].append(river_card)
        river_details[river_card] = {
            'strengths': snapshot.strengths,
            'ranking': snapshot.ranking,
            'positions': snapshot.positions,
            'winners': snapshot.winners,
        }
        for player in range(len(table.hands)):
            if snapshot.positions[player] < current_positions[player]:
                position_improvers[player].append(river_card)
            if player not in current_winners and player in snapshot.winners:
                winning_outs[player].append(river_card)

    analysis = _analysis_result(table, current_snapshot, _normalize_equities(equities, total_possibilities), outs)
    analysis['position_improvers'] = position_improvers
    analysis['winning_outs'] = winning_outs
    analysis['river_details'] = river_details
    return analysis


def flop_equity_analysis(table: Table) -> dict[str, Any]:
    if len(table.board) != 3:
        raise UserWarning("Not three cards on the board. %s", table.board)

    current_board = list(table.board.board)
    remaining_cards = _remaining_cards(table)
    current_snapshot = _evaluate_board(table.hands, current_board)
    equities = [0.0 for _ in table.hands]
    outs: list[list[tuple[Card, Card]]] = [[] for _ in table.hands]
    current_positions = current_snapshot.positions
    turn_improvers: list[list[Card]] = [[] for _ in table.hands]
    improving_runouts: list[list[tuple[Card, Card]]] = [[] for _ in table.hands]
    reversal_runouts: list[list[tuple[Card, Card]]] = [[] for _ in table.hands]
    turn_details: list[dict[Card, dict[str, Any]]] = [dict() for _ in table.hands]
    total_possibilities = 0

    for turn_index, turn_card in enumerate(remaining_cards):
        turn_snapshot = _evaluate_board(table.hands, current_board + [turn_card])

        river_snapshots: dict[Card, BoardSnapshot] = {}
        for river_index, river_card in enumerate(remaining_cards):
            if river_index == turn_index:
                continue

            river_snapshot = _evaluate_board(table.hands, current_board + [turn_card, river_card])
            river_snapshots[river_card] = river_snapshot

            if turn_index < river_index:
                total_possibilities += 1
                equity_share = 1 / len(river_snapshot.winners)
                runout = (turn_card, river_card)
                for winner in river_snapshot.winners:
                    equities[winner] += equity_share
                    outs[winner].append(runout)

        for player in range(len(table.hands)):
            improves_on_turn = turn_snapshot.positions[player] < current_positions[player]
            if improves_on_turn:
                turn_improvers[player].append(turn_card)

            river_improvers: list[Card] = []
            river_reversals: list[Card] = []
            river_winners: dict[Card, list[int]] = {}

            for river_card, river_snapshot in river_snapshots.items():
                river_winners[river_card] = river_snapshot.winners

                if river_snapshot.positions[player] < current_positions[player]:
                    river_improvers.append(river_card)
                    improving_runouts[player].append((turn_card, river_card))
                if improves_on_turn and river_snapshot.positions[player] > turn_snapshot.positions[player]:
                    river_reversals.append(river_card)
                    reversal_runouts[player].append((turn_card, river_card))

            turn_details[player][turn_card] = {
                'turn_strength': turn_snapshot.strengths[player],
                'turn_ranking': turn_snapshot.ranking,
                'turn_position': turn_snapshot.positions[player],
                'turn_winners': turn_snapshot.winners,
                'improves_on_turn': improves_on_turn,
                'river_improvers': river_improvers,
                'river_reversals': river_reversals,
                'river_winners': river_winners,
            }

    analysis = _analysis_result(table, current_snapshot, _normalize_equities(equities, total_possibilities), outs)
    analysis['turn_improvers'] = turn_improvers
    analysis['improving_runouts'] = improving_runouts
    analysis['reversal_runouts'] = reversal_runouts
    analysis['turn_details'] = turn_details
    return analysis


def equity_analysis(table: Table) -> dict[str, Any]:
    match len(table.board):
        case 3:
            return flop_equity_analysis(table)
        case 4:
            return turn_equity_analysis(table)
        case _:
            raise UserWarning("Board length is not 3 or 4. %s", table.board)


def turn_equity_legacy(table: Table) -> tuple[list[float], list[list[Card]]]:
    if len(table.board) != 4:
        raise UserWarning("Not four cards on the board. %s", table.board)

    equities = [0.0 for _ in range(len(table.hands))]
    outs: list[list[Card]] = [[] for _ in range(len(table.hands))]
    for card in table.board.deck:
        table.board.board.append(card)
        hand_strengths = [ev.determineHandStrength(hand.hand, table.board.board) for hand in table.hands]
        max_strength = max(hand_strengths)
        winners = [player for player, strength in enumerate(hand_strengths) if strength == max_strength]
        for winner in winners:
            equities[winner] += 1 / len(winners)
            outs[winner].append(card)
        table.board.board.pop()

    total_possibilities = len(table.board.deck)
    if total_possibilities > 0:
        equities = [equity / total_possibilities for equity in equities]
    return equities, outs


def flop_equity_legacy(table: Table) -> tuple[list[float], list[list[tuple[Card, Card]]]]:
    if len(table.board) != 3:
        raise UserWarning("Not three cards on the board. %s", table.board)

    equities = [0.0 for _ in range(len(table.hands))]
    outs: list[list[tuple[Card, Card]]] = [[] for _ in range(len(table.hands))]
    for first_index in range(len(table.board.deck)):
        for second_index in range(first_index + 1, len(table.board.deck)):
            table.board.board.append(table.board.deck.deck[first_index])
            table.board.board.append(table.board.deck.deck[second_index])
            hand_strengths = [ev.determineHandStrength(hand.hand, table.board.board) for hand in table.hands]
            max_strength = max(hand_strengths)
            winners = [player for player, strength in enumerate(hand_strengths) if strength == max_strength]
            for winner in winners:
                equities[winner] += 1 / len(winners)
                outs[winner].append((table.board.deck.deck[first_index], table.board.deck.deck[second_index]))
            table.board.board.pop()
            table.board.board.pop()

    total_possibilities = len(table.board.deck) * (len(table.board.deck) - 1) / 2
    if total_possibilities > 0:
        equities = [equity / total_possibilities for equity in equities]
    return equities, outs


def preflop_equity_legacy(table: Table) -> tuple[list[float], list[list[Any]]]:
    if len(table.board) != 0:
        raise UserWarning("Not zero cards on the board. %s", table.board)

    equities = [0.0 for _ in range(len(table.hands))]
    outs: list[list[Any]] = [[] for _ in range(len(table.hands))]
    for first_index in range(len(table.board.deck)):
        for second_index in range(first_index + 1, len(table.board.deck)):
            for third_index in range(second_index + 1, len(table.board.deck)):
                for fourth_index in range(third_index + 1, len(table.board.deck)):
                    for fifth_index in range(fourth_index + 1, len(table.board.deck)):
                        table.board.board.append(table.board.deck.deck[first_index])
                        table.board.board.append(table.board.deck.deck[second_index])
                        table.board.board.append(table.board.deck.deck[third_index])
                        table.board.board.append(table.board.deck.deck[fourth_index])
                        table.board.board.append(table.board.deck.deck[fifth_index])
                        hand_strengths = [ev.determineHandStrength(hand.hand, table.board.board) for hand in table.hands]
                        max_strength = max(hand_strengths)
                        winners = [player for player, strength in enumerate(hand_strengths) if strength == max_strength]
                        for winner in winners:
                            equities[winner] += 1 / len(winners)
                        table.board.board.pop()
                        table.board.board.pop()
                        table.board.board.pop()
                        table.board.board.pop()
                        table.board.board.pop()

    total_possibilities = (
        len(table.board.deck)
        * (len(table.board.deck) - 1)
        * (len(table.board.deck) - 2)
        * (len(table.board.deck) - 3)
        * (len(table.board.deck) - 4)
    ) / 120
    if total_possibilities > 0:
        equities = [equity / total_possibilities for equity in equities]
    return equities, outs


def equity_legacy(table: Table):
    match len(table.board):
        case 0:
            return preflop_equity_legacy(table)
        case 3:
            return flop_equity_legacy(table)
        case 4:
            return turn_equity_legacy(table)
        case _:
            raise UserWarning("Board length is not 0, 3, or 4. %s", table.board)

def turn_equity(table: Table) -> List[float]:
    '''
    Calculate the equity of each hand given the current board and remaining deck.
    '''
    if len(table.board) != 4:
        raise UserWarning("Not four cards on the board. %s", table.board)
    return _equity_for_runouts(table, 1)

def flop_equity(table: Table):
    '''
    Calculate the equity of each hand given the current board and remaining deck.
    '''
    if len(table.board) != 3:
        raise UserWarning("Not three cards on the board. %s", table.board)
    return _equity_for_runouts(table, 2)

def preflop_equity(table: Table):
    if len(table.board) != 0:
        raise UserWarning("Not zero cards on the board. %s", table.board)
    remaining = _remaining_cards(table)
    equities = preflop_equity_iso(table.hands, remaining)
    return equities, [[] for _ in table.hands]

def equity(table: Table):
    match len(table.board):
        case 0:
            return preflop_equity(table)
        case 3:
            return flop_equity(table)
        case 4:
            return turn_equity(table)
        case _:
            raise UserWarning("Board length is not 0, 3, or 4. %s", table.board)

if __name__ == '__main__':
    hands = []
    for hand in sys.argv[1:]:
        hands.append(Hand(hand))
    table = Table(
        hands=hands,
        # board=[
        #     Card('3h'),
        #     Card('Ad'),
        #     Card('Jh'),
        #     Card('9d')
        # ]
    )
    print("Hands:", [str(hand) for hand in table.hands])
    print(table.board)
    start_time = time.time()
    equities, outs = equity(table)
    end_time = time.time()
    print(f"Calculated equities in {end_time - start_time:.2f} seconds")
    print("Equities:", equities)
    # print("Outs:", outs)
    start_time = time.time()
    equities, outs = equity_legacy(table)
    end_time = time.time()
    print(f"Calculated legacy equities in {end_time - start_time:.2f} seconds")
    print("Equities:", equities)