from collections import Counter
from typing import List

from card import Card, Suit

class Hand():
    def __init__(self, hand : str | List[Card]):
        if isinstance(hand, str):
            hand = [Card(hand[i:i+2]) for i in range(0, len(hand), 2)]
        self.hand : List[Card] = sorted(hand, reverse=True)
    
    def __repr__(self) -> str:
        strHand = 'Hand: ['
        for card in self.hand:
            strHand += f'{card}, '
        strHand = strHand[:-2] + ']'
        return strHand
    
    def __str__(self) -> str:
        ranks = ''
        for card in self.hand:
            ranks += repr(card.rank)
        if not self.hand or all(card.rank == self.hand[0].rank for card in self.hand):
            return ranks
        return ranks + 's' if self.isSuited() else ranks + 'o'
    
    def __hash__(self) -> int:
        return hash(repr(self))

    def __lt__(self, other) -> bool:
        if len(self) != len(other):
            raise UserWarning("Different lengths of hands, self: %s, other: %s", self.hand, other.hand)
        for i in range(len(self.hand)-1, -1, -1):
            if self.hand[i] != other.hand[i]:
                return self.hand[i] < other.hand[i]
        # Design decision: AKo < AKs
        if not self.isSuited() and other.isSuited():
            return True
        return False
    
    def __eq__(self, other) -> bool:
        if len(self) != len(other):
            return False
        # Design decision: AcKs == AhKd? No, not same hand, just equal strength. Consistent with Card.__eq__
        for card in self.hand:
            if card not in other.hand:
                return False
        return True

    def __len__(self) -> int:
        return len(self.hand)
    
    def __getitem__(self, index : int) -> Card:
        return self.hand[index]
    
    def __setitem__(self, index : int, card : Card):
        self.hand[index] = card

    def __iter__(self) -> 'Hand':
        self.depth = 0
        return self
    
    def __next__(self) -> Card:
        if self.depth < len(self):
            self.card = self.hand[self.depth]
            self.depth += 1
            return self.card
        else:
            raise StopIteration
    
    def __contains__(self, card) -> bool:
        return card in self.hand
        
    def isSuited(self) -> bool:
        if len(self.hand) > len(Suit):
            return True
        suits = [card.suit for card in self.hand]
        return Counter(suits).most_common()[0][1] > 1
    
    def append(self, card : Card):
        self.hand.append(card)
        self.hand = sorted(self.hand, reverse=True)