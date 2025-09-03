from cards import Card, Deck, Rank, Suit
from table import Board, Hand, Table
from evaluator import Ranking
from typing import List, Tuple

import stats as st
import evaluator as ev
import pandas as pd
import logging as log

log.basicConfig(level=log.DEBUG, filename="logfile", filemode="a+", format="%(asctime)-15s %(levelname)-8s %(message)s")

TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, JACK, QUEEN, KING, ACE = Rank.TWO, Rank.THREE, Rank.FOUR, Rank.FIVE, Rank.SIX, Rank.SEVEN, Rank.EIGHT, Rank.NINE, Rank.TEN, Rank.JACK, Rank.QUEEN, Rank.KING, Rank.ACE
CLUB, DIAMOND, HEART, SPADE = Suit.CLUB, Suit.DIAMOND, Suit.HEART, Suit.SPADE

def play(numPlayers, iterations):
    count = 0
    table = Table(numPlayers)

    while(count < iterations):
        # log.info(f"Hand Number {count}\n")
        # print(f"Hand Number {count}\n")

        table.commenceRound()
        # log.info(f"{table}\n")
        # print(table)

        hands = []
        boardStrength, _ = ev.determineHandStrength([], table.board.board)

        for i in range(numPlayers):
            hand = ev.determineHandStrength(table.hands[i].hand, table.board.board)
            hands.append(hand)
            # log.info(f"P{i}'s Strength: {str(hand)}")
            # print(f"P{i}'s Strength: {str(hand)}")
        # log.info("")
        # print("")

        winner : Tuple[Ranking, List[Card]] = max(hands)

        winningHands = [(f'P{i}', hand) for i, hand in enumerate(hands) if hand == winner]
        # log.info(f"Winner(s): {winningHands}\n")
        # print(f"Winner(s): {winningHands}\n")
        
        # Update stats
        for (player, _) in winningHands:
            st.updateWinCount(table.hands[int(player[1])])

        if boardStrength > winner[0]:
            print("SHOULD NOT HAPPEN")
            print(table)
            print("Board Strength:", boardStrength, "Winner:", winner)

        st.updateWinningHandStrength(boardStrength, winner[0])
        
        print("Hands Run:", count, end="\r")

        table.reset()
        count +=1

    winCounts = st.getWinCount()
    handStrengthVSBoard = st.getWinningHandStrength()

    return winCounts, handStrengthVSBoard

def main():
    winCounts, handStrengthVSBoard = play(2, 1000000)
    print(winCounts.to_string())
    print(handStrengthVSBoard.to_string())
    



if __name__ == "__main__":
    main()