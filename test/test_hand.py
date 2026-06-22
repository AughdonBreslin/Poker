
from card import Card, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, JACK, QUEEN, KING, ACE, CLUB, DIAMOND, HEART, SPADE
from hand import Hand

class TestHand:
    def test_hand_creation_list(self):
        hand = Hand([Card(ACE, SPADE), Card(KING, HEART)])
        assert len(hand) == 2
        assert Card(ACE, SPADE) == hand[0]
        assert Card(KING, HEART) == hand[1]

    def test_hand_creation_str(self):
        hand = Hand("AsKhQdJcTs")
        print("HERE 3", hand, len(hand))
        assert len(hand) == 5
        assert Card(ACE, SPADE) == hand[0]
        assert Card(KING, HEART) == hand[1]
        assert Card(QUEEN, DIAMOND) == hand[2]
        assert Card(JACK, CLUB) == hand[3]
        assert Card(TEN, SPADE) == hand[4]

    def test_hand_invalid_creation_list(self):
        try:
            hand = Hand([Card(ACE, SPADE), "Kh"])
            assert False, "Expected TypeError for invalid card in list"
        except TypeError:
            pass

    def test_hand_invalid_creation_str(self):
        try:
            hand = Hand("AsK")
            assert False, "Expected TypeError for invalid card string"
        except TypeError:
            pass

    def test_hand_str_repr(self):
        hand = Hand([Card(ACE, SPADE), Card(KING, HEART)])
        str_hand = str(hand)
        repr_hand = repr(hand)
        assert isinstance(str_hand, str)
        assert isinstance(repr_hand, str)
        assert len(str_hand) < len(repr_hand)

    def test_hand_eq(self):
        hand1 = Hand([Card(ACE, SPADE), Card(KING, HEART)])
        hand2 = Hand([Card(ACE, SPADE), Card(KING, HEART)])
        assert hand1 == hand2
        hand1.append(Card(QUEEN, DIAMOND))
        assert hand1 != hand2
        hand2.append(Card(QUEEN, DIAMOND))
        assert hand1 == hand2

    def test_hand_len(self):
        hand = Hand([Card(ACE, SPADE), Card(KING, HEART)])
        assert len(hand) == 2
        hand.append(Card(QUEEN, DIAMOND))
        assert len(hand) == 3

    def test_hand_iteration(self):
        hand = Hand([Card(ACE, SPADE), Card(KING, HEART)])
        count = 0
        for _ in hand:
            count += 1
        assert count == 2
    
    def test_contains(self):
        hand = Hand([Card(ACE, SPADE), Card(KING, HEART)])
        card = Card(ACE, SPADE)
        assert card in hand
        card = Card(QUEEN, DIAMOND)
        assert card not in hand
    
    def test_is_suited(self):
        hand = Hand([Card(ACE, SPADE), Card(KING, SPADE)])
        assert hand.isSuited()
        hand = Hand([Card(ACE, SPADE), Card(KING, HEART)])
        assert not hand.isSuited()

    def test_append(self):
        hand = Hand([Card(ACE, SPADE)])
        hand.append(Card(KING, HEART))
        assert len(hand) == 2
        assert Card(KING, HEART) in hand
        assert hand[0] == Card(ACE, SPADE)