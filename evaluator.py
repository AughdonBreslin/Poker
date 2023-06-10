from cards import Suit, Rank, Card
from collections import Counter, deque
from enum import Enum
from table import Board
from typing import List, Deque, Tuple, Counter

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

def findStraight(cards : List[Card]) -> (List[Card] | None):
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
    straight : List[Card] = findStraight(sorted_cards)
    if straight is not None:
        if all(straight[i].suit == straight[i+1].suit for i in range(4)):
            return Ranking.STRAIGHTFLUSH, straight

    # Check for four of a kind
    if 4 in ranks.values():
        quads : List[Card] = [card for card in sorted_cards if card.rank == [rank for rank, count in ranks.items() if count == 4][0]]
        kicker : Card = sorted_cards[0] if sorted_cards[0].rank != quads[0].rank else sorted_cards[4]
        return Ranking.QUADS, quads + [kicker]

    # Check for full house
    if len([count for count in ranks.values() if count == 3]) == 2:
        tripRanks : List[Rank] = sorted([rank for rank, count in ranks.items() if count == 3], reverse=True)
        higherTrips : List[Card] = [card for card in sorted_cards if card.rank == tripRanks[0]]
        counterfeitedTrips : List[Card] = [card for card in sorted_cards if card.rank == tripRanks[1]]
        return Ranking.BOAT, higherTrips + counterfeitedTrips[:2]
    if 3 in ranks.values() and 2 in ranks.values():
        trips : List[Card] = [card for card in sorted_cards if card.rank == next((rank for rank, count in ranks.items() if count == 3), None)]
        pairRank : Rank = next((rank for rank, count in ranks.items() if count == 2), None)
        pair : List[Card] = [card for card in cards if card.rank == pairRank]
        return Ranking.BOAT, trips + pair

    # Check for flush
    suitCount : Tuple[Suit, int] = suits.most_common(1)[0]
    if suitCount[1] >= 5:
        flush : List[Card] = [card for card in sorted_cards if card.suit == suitCount[0]]
        return Ranking.FLUSH, flush[:5]

    # Check for straight
    straight : List[Card] = findStraight(sorted_cards)
    if straight is not None:
        return Ranking.STRAIGHT, straight

    # Check for three of a kind
    if 3 in ranks.values():
        trips : List[Card] = [card for card in sorted_cards if card.rank == next(rank for rank, count in ranks.items() if count == 3)]
        firstKicker : Card = next((card for card in sorted_cards if card.rank != trips[0].rank), None)
        secondKicker : Card = next((card for card in sorted_cards if card.rank != trips[0].rank and card.rank != firstKicker.rank), None)
        return Ranking.TRIPS, trips + [firstKicker] + [secondKicker]

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
        return Ranking.TWOPAIR, firstPair + secondPair + [kicker]

    # Check for pair
    if 2 in ranks.values():
        pairRank : Rank = next((rank for rank, count in ranks.items() if count == 2), None)
        pair : List[Card] = [card for card in cards if card.rank == pairRank]
        firstKicker : Card = next((card for card in sorted_cards if card.rank != pairRank), None)
        secondKicker : Card = next((card for card in sorted_cards if card.rank != pairRank and card.rank != firstKicker.rank), None)
        thirdKicker : Card = next((card for card in sorted_cards if card.rank != pairRank and card.rank != firstKicker.rank and card.rank != secondKicker.rank), None)
        return Ranking.PAIR, pair + [firstKicker] + [secondKicker] + [thirdKicker]

    # Otherwise, return high card
    return Ranking.HIGHCARD, sorted_cards[:5]
