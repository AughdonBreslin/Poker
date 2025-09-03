from collections import Counter, deque
from enum import Enum
from typing import List, Deque, Tuple, Counter

from cards import Suit, Rank, Card
from table import Hand

TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, JACK, QUEEN, KING, ACE = Rank.TWO, Rank.THREE, Rank.FOUR, Rank.FIVE, Rank.SIX, Rank.SEVEN, Rank.EIGHT, Rank.NINE, Rank.TEN, Rank.JACK, Rank.QUEEN, Rank.KING, Rank.ACE
CLUB, DIAMOND, HEART, SPADE = Suit.CLUB, Suit.DIAMOND, Suit.HEART, Suit.SPADE

class Ranking(Enum):
    HIGHCARD = 1
    PAIR = 2
    TWOPAIR = 3
    TRIPS = 4
    STRAIGHT = 5
    FLUSH = 6
    BOAT = 7
    QUADS = 8
    STRAIGHTFLUSH = 9

    def __lt__(self, other):
        if type(self) == type(other):
            return self.value < other.value
        return NotImplemented
    
    def __repr__(self):
        return str(self.name)

class HandStrength:
    def __init__(self, ranking : Ranking, cards : List[Card]):
        self.ranking = ranking
        self.cards = cards

    def __lt__(self, other):
        if self.ranking != other.ranking:
            return self.ranking < other.ranking
        if len(self.cards) != len(other.cards):
            raise UserWarning("Different lengths of cards, self: %s, other: %s", self.cards, other.cards)
        
        for i in range(len(self.cards)):
            if self.cards[i].rank != other.cards[i].rank:
                return self.cards[i] < other.cards[i]
        return False

    def __eq__(self, other):
        if self.ranking != other.ranking:
            return False
        if len(self.cards) != len(other.cards):
            raise UserWarning("Different lengths of cards, self: %s, other: %s", self.cards, other.cards)
        for i in range(len(self.cards)):
            if self.cards[i].rank != other.cards[i].rank:
                return False
        return True
    
    def __repr__(self):
        return f"HS({self.ranking}, {self.cards})"

def findStraight(cards : List[Card]) -> List[Card]:
    straight : Deque[Card] = deque([], 5)
    for rank in (Rank.ACE, *Rank):
        card = next((card for card in cards if card.rank == rank), None)
        if card is not None:
            straight.appendleft(card)
        else:
            if len(straight) == 5:
                break
            straight.clear()
    if len(straight) == 5:
        return list(straight)
    return None

def determineHandStrength(hand : List[Card], board : List[Card]) -> Tuple[Ranking, List[Card]]:
    cards = hand + board

    # Sort the cards by rank
    sorted_cards : List[Card] = sorted(cards, key=lambda x: x.rank, reverse=True)
    ranks : Counter(Rank, int) = Counter([card.rank for card in sorted_cards])
    suits : Counter(Suit, int) = Counter([card.suit for card in sorted_cards])

    # Check for straight flush
    suitCount : Tuple[Suit, int] = suits.most_common(1)[0]
    if suitCount[1] >= 5:
            flush : List[Card] = [card for card in sorted_cards if card.suit == suitCount[0]]
            straight : List[Card] = findStraight(flush)
            if straight is not None:
                return HandStrength(Ranking.STRAIGHTFLUSH, straight)
            # If flush but no straight, impossible to have quads or boat, so return flush
            return HandStrength(Ranking.FLUSH, flush[:5])

    # Check for quads
    if 4 in ranks.values():
        quads : List[Card] = [card for card in sorted_cards if card.rank == [rank for rank, count in ranks.items() if count == 4][0]]
        kicker : Card = sorted_cards[0] if sorted_cards[0].rank != quads[0].rank else sorted_cards[4]
        return HandStrength(Ranking.QUADS, quads + [kicker])

    # Check for boat
    if len([count for count in ranks.values() if count == 3]) == 2:
        tripRanks : List[Rank] = sorted([rank for rank, count in ranks.items() if count == 3], reverse=True)
        higherTrips : List[Card] = [card for card in sorted_cards if card.rank == tripRanks[0]]
        counterfeitedTrips : List[Card] = [card for card in sorted_cards if card.rank == tripRanks[1]]
        return HandStrength(Ranking.BOAT, higherTrips + counterfeitedTrips[:2])
    if 3 in ranks.values() and 2 in ranks.values():
        trips : List[Card] = [card for card in sorted_cards if card.rank == next((rank for rank, count in ranks.items() if count == 3), None)]
        pairRank : Rank = next((rank for rank, count in ranks.items() if count == 2), None)
        pair : List[Card] = [card for card in cards if card.rank == pairRank]
        return HandStrength(Ranking.BOAT, trips + pair)

    # Flush has already been accounted for

    # Check for straight
    straight : List[Card] = findStraight(sorted_cards)
    if straight is not None:
        return HandStrength(Ranking.STRAIGHT, straight)

    # Check for three of a kind
    if 3 in ranks.values():
        trips : List[Card] = [card for card in sorted_cards if card.rank == next(rank for rank, count in ranks.items() if count == 3)]
        firstKicker : Card = next((card for card in sorted_cards if card.rank != trips[0].rank), None)
        secondKicker : Card = next((card for card in sorted_cards if card.rank != trips[0].rank and card.rank != firstKicker.rank), None)
        return HandStrength(Ranking.TRIPS, trips + [firstKicker] + [secondKicker])

    # Check for two pair
    if len([count for count in ranks.values() if count == 2]) >= 2:
        pairsRanks : List[Rank] = sorted([rank for rank, count in ranks.items() if count == 2], reverse=True)[:2]
        firstPair : List[Card] = [card for card in sorted_cards if card.rank == pairsRanks[0]]
        secondPair : List[Card] = [card for card in sorted_cards if card.rank == pairsRanks[1]]
        kicker : Card = None
        if sorted_cards[0].rank != pairsRanks[0]:
            kicker = sorted_cards[0]
        elif sorted_cards[2].rank != pairsRanks[1]:
            kicker = sorted_cards[2]
        else:
            kicker = sorted_cards[4]
        return HandStrength(Ranking.TWOPAIR, firstPair + secondPair + [kicker])

    # Check for pair
    if 2 in ranks.values():
        pairRank : Rank = next((rank for rank, count in ranks.items() if count == 2), None)
        pair : List[Card] = [card for card in cards if card.rank == pairRank]
        firstKicker : Card = next((card for card in sorted_cards if card.rank != pairRank), None)
        secondKicker : Card = next((card for card in sorted_cards if card.rank != pairRank and card.rank != firstKicker.rank), None)
        thirdKicker : Card = next((card for card in sorted_cards if card.rank != pairRank and card.rank != firstKicker.rank and card.rank != secondKicker.rank), None)
        return HandStrength(Ranking.PAIR, pair + [firstKicker] + [secondKicker] + [thirdKicker])

    # Otherwise, return high card
    return HandStrength(Ranking.HIGHCARD, sorted_cards[:5])

if __name__ == "__main__":
    hands = [
        Hand([Card(FOUR, HEART), Card(SIX, CLUB)]),
        Hand([Card(TWO, HEART), Card(NINE, HEART)]),
        Hand([Card(EIGHT, DIAMOND), Card(ACE, CLUB)]),
        Hand([Card(EIGHT, SPADE), Card(NINE, CLUB)]),
        Hand([Card(THREE, SPADE), Card(KING, DIAMOND)]),
        Hand([Card(FOUR, SPADE), Card(EIGHT, CLUB)]),
    ]
    board = [
        Card(THREE, HEART),
        Card(ACE, DIAMOND),
        Card('Jh'),
        Card('9d')
    ]
    river = Card('9s')
    print(hands[1].hand)
    hs1 = determineHandStrength(hands[1].hand, board + [river])
    hs2 = determineHandStrength(hands[3].hand, board + [river])

    print(hs1, hs2, hs1 > hs2, hs1 < hs2, hs1 == hs2)
