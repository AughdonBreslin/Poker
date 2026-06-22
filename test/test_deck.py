import itertools as it

from card import Rank, Suit, Card, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, JACK, QUEEN, KING, ACE, CLUB, DIAMOND, HEART, SPADE
from deck import Deck

class TestDeck:
    def test_deck_creation(self):
        deck = Deck()
        assert len(deck) == 52
        unique_cards = set(deck.deck)
        assert len(unique_cards) == 52  # Ensure all cards are unique

    def test_deck_str_repr(self):
        deck = Deck()
        str_deck = str(deck)
        repr_deck = repr(deck)
        assert isinstance(str_deck, str)
        assert isinstance(repr_deck, str)
        assert len(str_deck) < len(repr_deck)

    def test_deck_eq(self):
        deck1 = Deck()
        deck2 = Deck()
        for i, card in enumerate(list(Card(rank, suit) for rank, suit in it.product(Rank, Suit))):
            deck1[i] = card
            deck2[i] = card
        assert deck1 == deck2
        deck1.drawCard()
        assert deck1 != deck2
        deck2.drawCard()
        assert deck1 == deck2

    def test_deck_len(self):
        deck = Deck()
        assert len(deck) == 52
        deck.drawCard()
        assert len(deck) == 51

    def test_deck_iteration(self):
        deck = Deck()
        count = 0
        for _ in deck:
            count += 1
        assert count == 52
    
    def test_contains(self):
        deck = Deck()
        card = Card(ACE, SPADE)
        assert card in deck
        card = deck.drawCard()
        assert card not in deck

    def test_shuffle(self):
        deck1 = Deck()
        deck2 = Deck()
        deck1.shuffle()
        assert deck1.deck != deck2.deck  # I pray to see the day this fails

    def test_draw_card(self):
        deck = Deck()
        initial_length = len(deck)
        card = deck.drawCard()
        assert isinstance(card, Card)
        assert len(deck) == initial_length - 1
        assert card in deck.drawnCards
        assert card not in deck

    def test_reset(self):
        deck = Deck()
        drawn_cards = [deck.drawCard() for _ in range(5)]
        assert len(deck) == 47
        deck.reset()
        assert len(deck) == 52
        for card in drawn_cards:
            assert card not in deck.drawnCards
            assert card in deck

    def test_remove_cards(self):
        deck = Deck()
        assert len(deck) == 52
        cards = [Card(ACE, SPADE), Card(KING, HEART), Card(TEN, CLUB)]
        deck.remove(cards)
        assert len(deck) == 52 - 3
        for card in cards:
            assert card not in deck
            assert card in deck.drawnCards