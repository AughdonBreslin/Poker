from card import Rank, Suit, Card, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, JACK, QUEEN, KING, ACE, CLUB, DIAMOND, HEART, SPADE

class TestRank:
    def test_str_representation(self):
        assert repr(TWO) == "2"
        assert repr(ACE) == "A"
        assert repr(JACK) == "J"
    
    def test_hash(self):
        assert hash(TWO) == hash("2")
        assert hash(ACE) == hash("A")
    
    def test_comparison(self):
        assert TWO < THREE
        assert ACE > KING
        assert JACK == JACK
        assert QUEEN != KING
    
    def test_from_str(self):
        assert Rank.from_str("2") == TWO
        assert Rank.from_str("A") == ACE
        try:
            Rank.from_str("X")
            assert False, "Expected ValueError"
        except ValueError:
            pass
    
    def test_from_int(self):
        assert Rank.from_int(2) == TWO
        assert Rank.from_int(14) == ACE
        try:
            Rank.from_int(15)
            assert False, "Expected ValueError"
        except ValueError:
            pass

class TestSuit:
    def test_str_representation(self):
        assert repr(CLUB) == "c"
        assert repr(HEART) == "h"
    
    def test_hash(self):
        assert hash(CLUB) == hash("c")
        assert hash(HEART) == hash("h")
    
    def test_equality(self):
        assert CLUB == CLUB
        assert CLUB != DIAMOND

class TestCard:
    def test_creation(self):
        card = Card(ACE, SPADE)
        assert card.rank == ACE
        assert card.suit == SPADE
        card = Card('Th')
        assert card.rank == TEN
        assert card.suit == HEART

    def test_invalid_creation(self):
        try:
            card = Card(ACE)
            assert False, "Expected TypeError"
        except TypeError:
            pass
        try:
            card = Card('A')
            assert False, "Expected TypeError"
        except TypeError:
            pass

    def test_str_representation(self):
        card = Card(ACE, SPADE)
        assert repr(card) == "As"
        card = Card(TEN, HEART)
        assert repr(card) == "Th"

    def test_hash(self):
        card1 = Card(ACE, SPADE)
        card2 = Card(ACE, SPADE)
        card3 = Card(KING, HEART)
        assert hash(card1) == hash(card2)
        assert hash(card1) != hash(card3)

    def test_equality(self):
        card1 = Card(ACE, SPADE)
        card2 = Card(ACE, SPADE)
        card3 = Card(ACE, HEART)
        assert card1 == card2
        assert card1 != card3
        assert not card1 < card3
