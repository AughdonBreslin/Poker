from enum import Enum

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
    
    def __repr__(self) -> str:
        return self.value[0]
    
    def __hash__(self) -> int:
        return hash(self.value[0])
    
    def __lt__(self, other) -> bool:
        return self.value[1] < other.value[1]

    def __eq__(self, other) -> bool:
        return self.value[1] == other.value[1]
    
    @classmethod
    def from_str(cls, value) -> 'Rank':
        for rank in cls:
            if rank.value[0] == value:
                return rank
        raise ValueError(f"'{value}' is not a valid Rank.")
    
    @classmethod
    def from_int(cls, value) -> 'Rank':
        for rank in cls:
            if rank.value[1] == value:
                return rank
        raise ValueError(f"'{value}' is not a valid Rank.")

TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, JACK, QUEEN, KING, ACE = Rank.TWO, Rank.THREE, Rank.FOUR, Rank.FIVE, Rank.SIX, Rank.SEVEN, Rank.EIGHT, Rank.NINE, Rank.TEN, Rank.JACK, Rank.QUEEN, Rank.KING, Rank.ACE

class Suit(Enum):
    CLUB    = "c"
    DIAMOND = "d"
    HEART   = "h"
    SPADE   = "s"

    def __repr__(self) -> str:
        return self.value
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __lt__(self, other) -> bool:
        return ord(self.value) < ord(other.value)
    
    def __eq__(self, other) -> bool:
        return self.value == other.value

CLUB, DIAMOND, HEART, SPADE = Suit.CLUB, Suit.DIAMOND, Suit.HEART, Suit.SPADE

class Card:
    def __init__(self, *args):
        # Parse a string like "As" or "Td"
        if len(args) == 1 and isinstance(args[0], str) and len(args[0]) == 2:
            self.rank : Rank = Rank.from_str(args[0][0])
            self.suit : Suit = Suit(args[0][1])
        # Parse a Rank and Suit
        elif len(args) == 2 and isinstance(args[0], Rank) and isinstance(args[1], Suit):
            self.rank : Rank = args[0]
            self.suit : Suit = args[1]
        else:
            raise TypeError(f"'{args}' is not a valid Card.")
    
    def __repr__(self) -> str:
        return repr(self.rank) + repr(self.suit)

    def __hash__(self) -> int:
        return hash(str(self.rank) + str(self.suit))
    
    def __lt__(self, other) -> bool:
        if isinstance(other, Rank):
            return self.rank < other
        elif isinstance(other, Card):
            return self.rank < other.rank
        else:
            raise TypeError(f"Cannot compare Card with {type(other)}")

    def __eq__(self, other) -> bool:
        if isinstance(other, Rank):
            return self.rank == other
        elif isinstance(other, Suit):
            return self.suit == other
        elif isinstance(other, Card):
            return self.rank == other.rank and self.suit == other.suit
        else:
            raise TypeError(f"Cannot compare Card with {type(other)}")