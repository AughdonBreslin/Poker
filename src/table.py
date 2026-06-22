from typing import List

from card import Card
from hand import Hand
from board import Board

class Table():
    def __init__(self, numPlayers : int = 6, buttonPosition : int = 0, hands : List[Hand] = [], board : List[Card] = []):
        if hands:
            self.numPlayers = len(hands)
        else:
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
        
        