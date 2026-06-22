from card import Card
from deck import Deck
from hand import Hand
from typing import List

class Board():
    def __init__(self, hands : List[Hand] = [], board : List[Card] = []):
        self.deck : Deck = Deck()
        self.board : List[Card] = board
        self.deck.remove(board)
        for hand in hands:
            self.deck.remove(hand)
        # TODO: self.pot

    def __repr__(self) -> str:
        return f'Board: {self.board}'
    
    def __contains__(self, card : Card) -> bool:
        return card in self.board
    
    def __len__(self) -> int:
        return len(self.board)
    
    def __eq__(self, other) -> bool:
        return self.board == other
    
    def dealToBoard(self, numCards : int = 1):
        for _ in range(numCards):
            card : Card = self.deck.drawCard()
            self.board.append(card)

    def clearBoard(self):
        self.board = []
        self.deck.reset()