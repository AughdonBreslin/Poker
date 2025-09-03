from typing import List

import evaluator as ev
from cards import Card, Rank, Suit
TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, JACK, QUEEN, KING, ACE = Rank.TWO, Rank.THREE, Rank.FOUR, Rank.FIVE, Rank.SIX, Rank.SEVEN, Rank.EIGHT, Rank.NINE, Rank.TEN, Rank.JACK, Rank.QUEEN, Rank.KING, Rank.ACE
CLUB, DIAMOND, HEART, SPADE = Suit.CLUB, Suit.DIAMOND, Suit.HEART, Suit.SPADE
from table import Table, Hand, Deck

def turn_equity(table: Table) -> List[float]:
    '''
    Calculate the equity of each hand given the current board and remaining deck.
    '''
    if len(table.board) != 4:
        raise UserWarning("Not four cards on the board. %s", table.board)
    equities = [0.0 for _ in range(len(table.hands))]
    outs = [[] for _ in range(len(table.hands))]
    for card in table.board.deck:
        table.board.board.append(card)
        hand_strengths = [ev.determineHandStrength(hand.hand, table.board.board) for hand in table.hands]
        max_strength = max(hand_strengths)
        winners = [i for i, strength in enumerate(hand_strengths) if strength == max_strength]
        for winner in winners:
            equities[winner] += 1 / len(winners)
            outs[winner].append(card)
        table.board.board.pop()
    total_possibilities = len(table.board.deck)
    if total_possibilities > 0:
        equities = [equity / total_possibilities for equity in equities]
    return equities, outs

def flop_equity(table: Table):
    '''
    Calculate the equity of each hand given the current board and remaining deck.
    '''
    if len(table.board) != 3:
        raise UserWarning("Not three cards on the board. %s", table.board)
    equities = [0.0 for _ in range(len(table.hands))]
    outs = [[] for _ in range(len(table.hands))]
    for i in range(len(table.board.deck)):
        for j in range(i + 1, len(table.board.deck)):
            table.board.board.append(table.board.deck.deck[i])
            table.board.board.append(table.board.deck.deck[j])
            hand_strengths = [ev.determineHandStrength(hand.hand, table.board.board) for hand in table.hands]
            max_strength = max(hand_strengths)
            winners = [k for k, strength in enumerate(hand_strengths) if strength == max_strength]
            for winner in winners:
                equities[winner] += 1 / len(winners)
                outs[winner].append((table.board.deck.deck[i], table.board.deck.deck[j]))
            table.board.board.pop()
            table.board.board.pop()
    total_possibilities = len(table.board.deck) * (len(table.board.deck) - 1) / 2 # Order doesn't matter, so divide by 2
    if total_possibilities > 0:
        equities = [equity / total_possibilities for equity in equities]
    return equities, outs

def preflop_equity(table: Table):
    '''
    Calculate the equities of each hand given the remaining deck. - Now how to optimize.
    a) Only check cards that change hand strength, ie sort deck, then go through reverse strength
     - how to identify card combos that change strength efficiently?
        - need to recurringly account for later cards granting the opposite hand greater strength
     - how to track combos of unchanging runouts? draws?
        - rem_cards*combinations - num_evaluations
     - 
    '''
    if len(table.board) != 0:
        raise UserWarning("Not zero cards on the board. %s", table.board)
    equities = [0.0 for _ in range(len(table.hands))]
    outs = [[] for _ in range(len(table.hands))]
    for i in range(len(table.board.deck)):
        for j in range(i + 1, len(table.board.deck)):
            for k in range(j + 1, len(table.board.deck)):
                for l in range(k + 1, len(table.board.deck)):
                    for m in range(l + 1, len(table.board.deck)):
                        table.board.board.append(table.board.deck.deck[i])
                        table.board.board.append(table.board.deck.deck[j])
                        table.board.board.append(table.board.deck.deck[k])
                        table.board.board.append(table.board.deck.deck[l])
                        table.board.board.append(table.board.deck.deck[m])
                        hand_strengths = [ev.determineHandStrength(hand.hand, table.board.board) for hand in table.hands]
                        max_strength = max(hand_strengths)
                        winners = [n for n, strength in enumerate(hand_strengths) if strength == max_strength]
                        for winner in winners:
                            equities[winner] += 1 / len(winners)
                            # outs[winner].append((table.board.deck.deck[i], table.board.deck.deck[j], table.board.deck.deck[k], table.board.deck.deck[l], table.board.deck.deck[m]))
                        table.board.board.pop()
                        table.board.board.pop()
                        table.board.board.pop()
                        table.board.board.pop()
                        table.board.board.pop()
    total_possibilities = (len(table.board.deck) * (len(table.board.deck) - 1) * (len(table.board.deck) - 2) * (len(table.board.deck) - 3) * (len(table.board.deck) - 4)) / 120 # Order doesn't matter, so divide by 5!
    if total_possibilities > 0:
        equities = [equity / total_possibilities for equity in equities]
    return equities, outs

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
    table = Table(
        # hands=[
        #     Hand('4h6c'),
        #     Hand('2h9h'),
        #     Hand('8dAc'),
        #     Hand('8s9c'),
        #     Hand('3sKd'),
        #     Hand('4s8c'),
        # ],
        # board=[
        #     Card('3h'),
        #     Card('Ad'),
        #     Card('Jh'),
        #     Card('9d')
        # ]
    )
    # if not table.hands:
    table.dealToHands()
    print("Hands:", [str(hand) for hand in table.hands])
    if not table.board:
        table.board.dealToBoard(4)
    print(table.board)
    equities, outs = equity(table)
    print("Equities:", equities)
    print("Outs:", outs)
