from cards import Rank, Suit, Card, Deck
from table import Hand, Board, Table
TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, JACK, QUEEN, KING, ACE = Rank.TWO, Rank.THREE, Rank.FOUR, Rank.FIVE, Rank.SIX, Rank.SEVEN, Rank.EIGHT, Rank.NINE, Rank.TEN, Rank.JACK, Rank.QUEEN, Rank.KING, Rank.ACE
CLUB, DIAMOND, HEART, SPADE = Suit.CLUB, Suit.DIAMOND, Suit.HEART, Suit.SPADE

# Instructions:
# Uses nose2, so
#  $pip install nose2, then
#  python -m nose2 in Player directory 
#  python -m nose2 -v for verbose

class TestTable:
    def test_hand_repr(self):
        hand = Hand([Card(FOUR, SPADE), Card(FIVE, SPADE)])
        assert hash(hand) == hash('54s')

    def test_hand_len(self):
        hand = Hand([Card(FOUR, SPADE), Card(FIVE, SPADE)])
        assert len(hand) == 2

    def test_hand_lt_invalid(self):
        hand1 = Hand([Card(FOUR, CLUB)])
        hand2 = Hand([Card(FOUR, SPADE), Card(FIVE, SPADE)])
        try:
            hand1 < hand2
            assert False
        except UserWarning:
            assert True

    def test_hand_lt(self):
        hand1 = Hand([Card(ACE, SPADE), Card(KING, SPADE)])
        hand2 = Hand([Card(KING, CLUB), Card(KING, DIAMOND)])
        assert hand2 < hand1
        hand3 = Hand([Card(KING, HEART), Card(QUEEN, HEART)])
        assert hand2 > hand3
        hand4 = Hand([Card(KING, SPADE), Card(QUEEN, CLUB)])
        assert hand4 < hand3

    def test_hand_eq(self):
        hand1 = Hand([Card(ACE, SPADE), Card(KING, SPADE)])
        hand2 = Hand([Card(ACE, HEART), Card(KING, HEART)])
        assert hand1 == hand2
        hand3 = Hand([Card(TWO, SPADE), Card(THREE, HEART)])
        hand4 = Hand([Card(THREE, SPADE), Card(TWO, HEART)])
        assert hand3 == hand4

    def test_hand_ne(self):
        hand1 = Hand([Card(ACE, SPADE), Card(KING, CLUB)])
        hand2 = Hand([Card(ACE, HEART), Card(KING, HEART)])
        assert hand1 != hand2
        hand3 = Hand([Card(TWO, SPADE), Card(FOUR, HEART)])
        hand4 = Hand([Card(THREE, SPADE), Card(TWO, HEART)])
        assert hand3 != hand4

    def test_hand_suited(self):
        hand1 = Hand([Card(ACE, SPADE), Card(KING, SPADE)])
        assert hand1.isSuited()
        hand2 = Hand([Card(ACE, SPADE), Card(KING, CLUB)])
        assert not hand2.isSuited()
        
    def test_hand_append(self):
        hand = Hand([])
        assert len(hand) == 0
        card1 = Card(FOUR, CLUB)
        assert card1 not in hand
        hand.append(card1)
        assert len(hand) == 1
        assert card1 in hand
        card2 = Card(ACE, CLUB)
        assert card2 not in hand
        hand.append(card2)
        assert len(hand) == 2
        assert card2 in hand

    def test_board_deal(self):
        board = Board()
        board.dealToBoard(3)
        assert len(board) == 3
        assert len(board.deck) == 49
        board.dealToBoard()
        assert len(board) == 4
        assert len(board.deck) == 48
        assert board == board.deck.drawnCards

    def test_table_len(self):
        table = Table()
        assert len(table) == 6

    def test_table_len2(self):
        table = Table(4)
        assert len(table) == 4

    def test_table_deal(self):
        table = Table()
        table.dealToHands()
        for hand in table.hands:
            assert len(hand) == 2
        assert len(table.hands) == 6
        


        





