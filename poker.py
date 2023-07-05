from cards import Card, Deck, Rank, Suit
from player import Player
from table import Board, Hand, Table
from evaluator import Ranking
from typing import List, Tuple

import stats as st
import evaluator as ev
import pandas as pd

TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, JACK, QUEEN, KING, ACE = Rank.TWO, Rank.THREE, Rank.FOUR, Rank.FIVE, Rank.SIX, Rank.SEVEN, Rank.EIGHT, Rank.NINE, Rank.TEN, Rank.JACK, Rank.QUEEN, Rank.KING, Rank.ACE
CLUB, DIAMOND, HEART, SPADE = Suit.CLUB, Suit.DIAMOND, Suit.HEART, Suit.SPADE

def play(numPlayers, iterations):
    count = 0
    table = Table(numPlayers)

    while(count < iterations):
        table.commenceRound()
        # print(table, "\n")
        
        hands = []
        boardStrength, board = ev.determineHandStrength([], table.board.board)

        for i in range(numPlayers):
            hand = ev.determineHandStrength(table.hands[i].hand, table.board.board)
            hands.append(hand)
            # print(f"P{i}'s Hand Strength: {str(hand)}")
        # print()

        winner : Tuple[Ranking, List[Card]] = max(hands)

        winningHands = [(f'P{i}', hand) for i, hand in enumerate(hands) if hand == winner]
        # print(f"Winner(s): {winningHands}", count, "\n")

        # Update stats
        for (player, _) in winningHands:
            st.updateWinCount(table.hands[int(player[1])])
        st.updateWinningHandStrength(boardStrength, winner[0])

        table.reset()
        count +=1

    winChart = st.getWinCount()
    
    winPercentage = [[float(winChart[i][j])/iterations for i in range(len(winChart))] for j in range(len(winChart[i]))]
    handStrengthVSBoard = pd.DataFrame(st.getWinningHandStrength(),  columns=[rank.name for rank in Ranking], index=[rank.name for rank in Ranking])
    
    print("Strength of Board vs Strength of Winning Hand")
    print(handStrengthVSBoard)

    return winPercentage

