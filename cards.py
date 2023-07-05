from enum import Enum
import itertools as it
import random as r
from typing import List

class Rank(Enum):
    TWO   = "2", 2
    THREE = "3", 3
    FOUR  = "4", 4
    FIVE  = "5", 5
    SIX   = "6", 6
    SEVEN = "7", 7
    EIGHT = "8", 8
    NINE  = "9", 9
    TEN   = "T", 10
    JACK  = "J", 11
    QUEEN = "Q", 12
    KING  = "K", 13
    ACE   = "A", 14

    def __repr__(self):
        return self.value[0]
    
    def __hash__(self):
        return hash(self.value[0])
    
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value[1] < other.value[1]
        return NotImplemented

    def __eq__(self, other):
        return self.value[1] == other.value[1]
    
    def __ne__(self, other):
        return self.value[1] != other.value[1]

class Suit(Enum):
    CLUB    = "c"
    DIAMOND = "d"
    HEART   = "h"
    SPADE   = "s"

    def __repr__(self):
        return self.value
    
    def __hash__(self):
        return hash(self.value)
    
    def __eq__(self, other):
        return self.value == other.value
    
    def __ne__(self, other):
        return self.value != other.value

class Card:
    def __init__(self, rank : Rank, suit : Suit):
        self.rank : Rank = rank
        self.suit : Suit = suit
    
    def __repr__(self):
        return repr(self.rank) + repr(self.suit)

    def __hash__(self):
        return hash((self.rank, self.suit))
    
    def __lt__(self, other):
        return self.rank < other.rank

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit
    
    def __ne__(self, other):
        return self.rank != other.rank or self.suit != other.suit

    # def __add__(self, other):
    #     return self.rank + other.rank + 's' if self.suit == other.suit else self.rank + other.rank + 'o'

class Deck:
    def __init__(self):
        self.deck : List[Card] = list(Card(rank, suit) for rank, suit in it.product(Rank, Suit))
        self.drawnCards : List[Card] = []

    def __repr__(self):
        return [card for card in self.deck]
    
    def __str__(self):
        strDeck = '['
        for card in self.deck:
            strDeck += f'{card}, '
        strDeck = strDeck[:-2] + ']'
        return strDeck
    
    def __len__(self):
        return len(self.deck)

    def __iter__(self):
        self.depth = 0
        return self
    
    def __next__(self):
        if self.depth < len(self):
            self.cardToDraw = self.deck[self.depth]
            self.depth += 1
            return self.cardToDraw
        else:
            raise StopIteration

    def shuffle(self):
        r.shuffle(self.deck)

    def drawCard(self):
        card : Card = self.deck.pop(0)
        self.drawnCards.append(card)
        return card

    def reset(self):
        self.deck += self.drawnCards
        self.drawnCards = []
        self.shuffle()
