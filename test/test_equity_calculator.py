from card import Card
from equity_calculator import (
    equity,
    equity_legacy,
    flop_equity,
    flop_equity_analysis,
    flop_equity_legacy,
    preflop_equity,
    preflop_equity_legacy,
    turn_equity,
    turn_equity_analysis,
    turn_equity_legacy,
)
from hand import Hand
from table import Table


class TestEquityCalculator:
    def test_turn_equity_matches_legacy(self):
        table = Table(
            hands=[Hand('AhKh'), Hand('QdQs')],
            board=[Card('As'), Card('Qc'), Card('2d'), Card('3h')],
        )

        equities, outs = turn_equity(table)
        legacy_equities, legacy_outs = turn_equity_legacy(table)

        assert equities == legacy_equities
        assert outs == legacy_outs

    def test_flop_equity_matches_legacy(self):
        table = Table(
            hands=[Hand('AhKh'), Hand('QdQs')],
            board=[Card('As'), Card('Qc'), Card('2d')],
        )

        equities, outs = flop_equity(table)
        legacy_equities, legacy_outs = flop_equity_legacy(table)

        assert equities == legacy_equities
        assert outs == legacy_outs

    def test_preflop_equity_matches_legacy(self):
        table = Table(
            hands=[Hand('AsAh'), Hand('KdKh')],
            board=[],
        )

        equities, outs = preflop_equity(table)
        legacy_equities, legacy_outs = preflop_equity_legacy(table)

        assert equities == legacy_equities
        assert outs == legacy_outs

    def test_equity_dispatch_matches_legacy_dispatch(self):
        table = Table(
            hands=[Hand('AhKh'), Hand('QdQs')],
            board=[Card('As'), Card('Qc'), Card('2d'), Card('3h')],
        )

        assert equity(table) == equity_legacy(table)

    def test_turn_analysis_equities_match_turn_equity(self):
        table = Table(
            hands=[Hand('AhKh'), Hand('QdQs')],
            board=[Card('As'), Card('Qc'), Card('2d'), Card('3h')],
        )

        equities, outs = turn_equity(table)
        analysis = turn_equity_analysis(table)

        assert analysis['equities'] == equities
        assert analysis['outs'] == outs

    def test_flop_analysis_equities_match_flop_equity(self):
        table = Table(
            hands=[Hand('AhKh'), Hand('QdQs')],
            board=[Card('As'), Card('Qc'), Card('2d')],
        )

        equities, outs = flop_equity(table)
        analysis = flop_equity_analysis(table)

        assert analysis['equities'] == equities
        assert analysis['outs'] == outs