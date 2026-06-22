import itertools as it
import random as r
from typing import List

from card import Rank, Suit, Card

class Deck:
    def __init__(self):
        self.deck : List[Card] = list(Card(rank, suit) for rank, suit in it.product(Rank, Suit))
        self.shuffle()
        self.drawnCards : List[Card] = []

    def __repr__(self) -> str:
        strDeck = 'Deck: ['
        for card in self.deck:
            strDeck += f'{card}, '
        strDeck = strDeck[:-2] + ']'
        return strDeck
    
    def __str__(self) -> str:
        return f'Deck({len(self)})'
    
    def __eq__(self, other) -> bool:
        # Design decision: order matters
        return self.deck == other.deck and self.drawnCards == other.drawnCards

    def __len__(self) -> int:
        return len(self.deck)
    
    def __getitem__(self, index : int) -> Card:
        return self.deck[index]
    
    def __setitem__(self, index : int, card : Card):
        self.deck[index] = card

    def __iter__(self) -> 'Deck':
        self.depth = 0
        return self
    
    def __next__(self) -> Card:
        if self.depth < len(self):
            self.cardToDraw = self.deck[self.depth]
            self.depth += 1
            return self.cardToDraw
        else:
            raise StopIteration
        
    def __contains__(self, card : Card) -> bool:
        return card in self.deck

    def shuffle(self):
        r.shuffle(self.deck)

    def drawCard(self) -> Card:
        card : Card = self.deck.pop(0)
        self.drawnCards.append(card)
        return card

    def reset(self):
        self.deck += self.drawnCards
        self.drawnCards = []
        self.shuffle()
    
    def remove(self, cards : Card | List[Card]):
        if isinstance(cards, Card):
            cards = [cards]
        for card in cards:
            self.deck.remove(card)
            self.drawnCards.append(card)
