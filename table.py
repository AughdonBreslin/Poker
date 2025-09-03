from cards import Card, Deck
from typing import List

from cards import Rank, Suit
TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, JACK, QUEEN, KING, ACE = Rank.TWO, Rank.THREE, Rank.FOUR, Rank.FIVE, Rank.SIX, Rank.SEVEN, Rank.EIGHT, Rank.NINE, Rank.TEN, Rank.JACK, Rank.QUEEN, Rank.KING, Rank.ACE
CLUB, DIAMOND, HEART, SPADE = Suit.CLUB, Suit.DIAMOND, Suit.HEART, Suit.SPADE

class Hand():
    def __init__(self, hand : str | List[Card]):
        if isinstance(hand, str):
            self.hand = sorted([Card(hand[i:i+2]) for i in range(0, len(hand), 2)])
        else:
            self.hand = sorted(hand)
    
    def __repr__(self):        
        ranks = repr(self.hand[1].rank) + repr(self.hand[0].rank)
        if self.hand[0].rank == self.hand[1].rank:
            return ranks
        return ranks + 's' if self.isSuited() else ranks + 'o'
    
    def __str__(self):
        return f'[{self.hand[0]}, {self.hand[1]}]'
    
    def __hash__(self):
        return hash(repr(self))

    def __len__(self):
        return len(self.hand)
    
    def __lt__(self, other):
        if len(self) != 2:
            raise UserWarning("Invalid hand length for NLH.")
        
        if (self.hand[0].rank < other.hand[0].rank or
            self.hand[1].rank < other.hand[1].rank):
            return True
        if (self.isSuited() or
            not self.isSuited() and not other.isSuited()):
            return False
        # if not self.isSuited() and other.isSuited():
        return True
    
    def __eq__(self, other):
        return (self.hand[0].rank == other.hand[0].rank and 
                self.hand[1].rank == other.hand[1].rank and 
                self.isSuited() == other.isSuited())
    
    def __ne__(self, other):
        return (self.hand[0].rank != other.hand[0].rank or 
                self.hand[1].rank != other.hand[1].rank or 
                self.isSuited() != other.isSuited())

    def __iter__(self):
        self.depth = 0
        return self
    
    def __next__(self):
        if self.depth < len(self):
            self.card = self.hand[self.depth]
            self.depth += 1
            return self.card
        else:
            raise StopIteration
        
    def isSuited(self):
        return self.hand[0].suit == self.hand[1].suit
    
    def append(self, card : Card):
        self.hand.append(card)
        self.hand = sorted(self.hand)

class Board():
    def __init__(self, hands : List[Hand] = [], board : List[Card] = []):
        self.deck = Deck()
        self.board = board
        self.deck.remove(board)
        for hand in hands:
            self.deck.remove(hand.hand)
        # TODO: self.pot

    def __repr__(self):
        return f'Board: {self.board}'
    
    def __len__(self):
        return len(self.board)
    
    def __eq__(self, other):
        return self.board == other
    
    def dealToBoard(self, numCards : int = 1):
        for _ in range(numCards):
            card : Card = self.deck.drawCard()
            self.board.append(card)

    def clearBoard(self):
        self.board = []
        self.deck.reset()

class Table():
    def __init__(self, numPlayers : int = 6, buttonPosition : int = 0, hands : List[Hand] = [], board : List[Card] = []):
        self.numPlayers = numPlayers
        self.button = buttonPosition
        self.hands = hands or [Hand([]) for _ in range(self.numPlayers)]
        self.board = Board(hands, board)

    def __str__(self):
        playerHands = [f"P{i}'s Hand: {hand}" for i, hand in enumerate(self.hands)]
        return '\n'.join(playerHands + [str(self.board)])
    
    def __len__(self):
        return self.numPlayers
    
    def addPlayer(self):
        # TODO: addPlayer
        self.numPlayers += 1
        self.hands.append(Hand([]))

    def removePlayer(self):
        # TODO: removePlayer
        self.numPlayers -= 1
        self.hands.pop()

    def dealToHands(self):
        curPlayer : int = (self.button + 1) % self.numPlayers
        for _ in range(2*self.numPlayers):
            card : Card = self.board.deck.drawCard()
            self.hands[curPlayer].append(card)
            curPlayer = (curPlayer + 1) % self.numPlayers

    def givePlayerHand(self, player : int, hand : Hand):
        if player > len(self.hands):
            raise UserWarning("Player does not exist.")
        if self.hands[player] != Hand([]):
            raise UserWarning("Player already has hand.")
        for card in hand:
            if card not in self.board.deck.drawnCards:
                raise UserWarning("Card not in deck.")
            self.board.deck.drawnCards.remove(card)
        self.hands[player] = hand

    def commenceRound(self):
        self.dealToHands()

        # wait
        self.board.dealToBoard(3)
        # wait
        self.board.dealToBoard()
        # wait
        self.board.dealToBoard()
        # wait
    
    def simulateRound(self, hands : List[Hand] = None, board : List[Card] = None):
        for i in range(len(hands)):
            self.givePlayerHand(i, hands[i])
        
        self.board.board = board

    def reset(self):
        self.board.clearBoard()
        for hand in self.hands:
            hand.hand = []
    
    def moveButton(self):
        self.button = (1 + self.button) % self.numPlayers
        
        