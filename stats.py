
from cards import Rank, Suit, Card, Deck
from table import Hand
from evaluator import Ranking

import pandas as pd

TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, JACK, QUEEN, KING, ACE = Rank.TWO, Rank.THREE, Rank.FOUR, Rank.FIVE, Rank.SIX, Rank.SEVEN, Rank.EIGHT, Rank.NINE, Rank.TEN, Rank.JACK, Rank.QUEEN, Rank.KING, Rank.ACE
CLUB, DIAMOND, HEART, SPADE = Suit.CLUB, Suit.DIAMOND, Suit.HEART, Suit.SPADE
def hands():
    deck = Deck()
    deck2 = Deck()

    allHands = set(Hand([card1,card2]) for card1 in deck for card2 in deck2 if card1 != card2)
    chart = [[None for _ in range(len(Rank))] for _ in range(len(Rank))]
    for hand in allHands:
        if len(repr(hand)) == 2:
            index = len(Rank)-(hand.hand[0].rank.value[1]-2)-1
            chart[index][index] = hand
            continue
        if repr(hand)[2] == 'o':
            index1 = len(Rank)-(hand.hand[0].rank.value[1]-2)-1
            index2 = len(Rank)-(hand.hand[1].rank.value[1]-2)-1
            chart[index1][index2] = hand
            continue
        if repr(hand)[2] == 's':
            index1 = len(Rank)-(hand.hand[1].rank.value[1]-2)-1
            index2 = len(Rank)-(hand.hand[0].rank.value[1]-2)-1
            chart[index1][index2] = hand
            continue
    return chart

winCount = [[0 for _ in range(len(Rank))] for _ in range(len(Rank))]
def getWinCount():
    df = pd.DataFrame(winCount, columns=[rank.name for rank in reversed(Rank)], index=[rank.name for rank in reversed(Rank)])
    df.columns.name = 'Wins'
    return df

def updateWinCount(hand):
    if len(repr(hand)) == 2:
        index = len(Rank)-(hand.hand[0].rank.value[1]-2)-1
        winCount[index][index] += 1
    elif repr(hand)[2] == 'o':
        index1 = len(Rank)-(hand.hand[0].rank.value[1]-2)-1
        index2 = len(Rank)-(hand.hand[1].rank.value[1]-2)-1
        winCount[index1][index2] += 1
    elif repr(hand)[2] == 's':
        index1 = len(Rank)-(hand.hand[1].rank.value[1]-2)-1
        index2 = len(Rank)-(hand.hand[0].rank.value[1]-2)-1
        winCount[index1][index2] += 1

winningHandStrengthCount = [[0 for _ in range(9)] for _ in range(9)]

def getWinningHandStrength():
    df = pd.DataFrame(winningHandStrengthCount,  columns=[rank.name for rank in Ranking], index=[rank.name for rank in Ranking])
    df.columns.name = 'Board vs. Winner'
    return df

def updateWinningHandStrength(boardStrength, handStrength):
    winningHandStrengthCount[boardStrength.value-1][handStrength.value-1] += 1

# TODO: Add a lose count!