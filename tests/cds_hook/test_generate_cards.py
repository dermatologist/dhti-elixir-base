from src.dhti_elixir_base.cds_hook.generate_cards import add_card


def test_add_card_with_string():
    result = add_card("This is a test card")
    assert "cards" in result
    assert len(result["cards"]) == 1
    assert result["cards"][0].summary == "This is a test card"
