from card import Card, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, JACK, QUEEN, KING, ACE, CLUB, DIAMOND, HEART, SPADE
from hand import Hand
from board import Board

class TestBoard:
    def test_board_creation(self):
        board = Board()
        assert len(board) == 0
        assert len(board.deck) == 52
    
    def test_board_creation_with_cards(self):
        board = Board(board=[Card(ACE, SPADE), Card(KING, HEART)])
        assert len(board) == 2
        assert len(board.deck) == 50
        assert Card(ACE, SPADE) in board
        assert Card(KING, HEART) in board
        assert Card(ACE, SPADE) not in board.deck
        assert Card(KING, HEART) not in board.deck

    def test_board_creation_with_hands(self):
        hand1 = Hand([Card(ACE, SPADE), Card(KING, HEART)])
        hand2 = Hand([Card(QUEEN, DIAMOND), Card(JACK, CLUB)])
        board = Board(hands=[hand1, hand2])
        assert len(board) == 0
        assert len(board.deck) == 48
        assert Card(ACE, SPADE) not in board.deck
        assert Card(KING, HEART) not in board.deck
        assert Card(QUEEN, DIAMOND) not in board.deck
        assert Card(JACK, CLUB) not in board.deck

    def test_board_deal_to_board(self):
        board = Board()
        board.dealToBoard(3)
        assert len(board) == 3
        assert len(board.deck) == 49
        board.dealToBoard()
        assert len(board) == 4
        assert len(board.deck) == 48
        board.dealToBoard()
        assert len(board) == 5
        assert len(board.deck) == 47

    def test_board_clear_board(self):
        board = Board(board=[]) # Why do I need to specify board=[] here? 
        board.dealToBoard(5)
        assert len(board) == 5
        assert len(board.deck) == 47
        board.clearBoard()
        assert len(board) == 0
        assert len(board.deck) == 52