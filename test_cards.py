from cards import Rank, Suit, Card, Deck
TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, JACK, QUEEN, KING, ACE = Rank.TWO, Rank.THREE, Rank.FOUR, Rank.FIVE, Rank.SIX, Rank.SEVEN, Rank.EIGHT, Rank.NINE, Rank.TEN, Rank.JACK, Rank.QUEEN, Rank.KING, Rank.ACE
CLUB, DIAMOND, HEART, SPADE = Suit.CLUB, Suit.DIAMOND, Suit.HEART, Suit.SPADE

# Instructions:
# Uses nose2, so
#  $pip install nose2, then
#  python -m nose2 in Player directory 

class TestCards:
    def test_rank_lt(self):
        assert TWO < THREE
        assert TEN < JACK

    def test_rank_eq(self):
        assert EIGHT == EIGHT
        assert ACE == ACE

    def test_rank_ne(self):
        assert QUEEN != KING
        assert FIVE != KING


    def test_suit_eq(self):
        assert CLUB == CLUB
        assert DIAMOND == DIAMOND

    def test_suit_ne(self):
        assert HEART != DIAMOND
        assert CLUB != SPADE
    
    def test_card_lt(self):
        assert Card(TWO, DIAMOND) < Card(THREE, SPADE)
        assert Card(ACE, SPADE) > Card(FOUR, HEART)

    def test_card_lt_same_rank(self):
        assert not (Card(FOUR, CLUB) < Card(FOUR, SPADE))
        assert not (Card(FOUR, CLUB) > Card(FOUR, SPADE))
        # not less than nor greater but not equal; the same but different
    
    def test_card_eq(self):
        assert Card(ACE, CLUB) == Card(ACE, CLUB)
        assert Card(KING, HEART) == Card(KING, HEART)
    
    def test_card_ne(self):
        assert Card(QUEEN, HEART) != Card(JACK, HEART)
        assert Card(NINE, DIAMOND) != Card(NINE, CLUB)
        # not less than but not equal; the same but different

    
    def test_deck(self):
        myDeck = Deck()
        assert len(myDeck) == 52
        assert len(myDeck.drawnCards) == 0
    
    def test_deck_draw(self):
        myDeck = Deck()
        myCard = myDeck.drawCard()
        assert len(myDeck) == 51
        assert len(myDeck.drawnCards) == 1
        assert myCard not in myDeck
    
    def test_deck_reset(self):
        myDeck = Deck()
        myDeck.drawCard()
        myDeck.drawCard()
        myDeck.drawCard()
        myDeck.reset()
        assert len(myDeck) == 52
        assert len(myDeck.drawnCards) == 0

