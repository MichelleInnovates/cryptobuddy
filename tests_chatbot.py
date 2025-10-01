from app import chatbot_logic


def test_sustainable():
    assert "eco-friendly" in chatbot_logic("Which coin is most sustainable?")


def test_trending():
    out = chatbot_logic("Which crypto is trending?")
    assert "Bitcoin" in out or "Cardano" in out


def test_bitcoin():
    out = chatbot_logic("Tell me about Bitcoin")
    assert "Bitcoin is" in out and "sustainability" in out


if __name__ == "__main__":
    # Run simple assertions without pytest
    test_sustainable()
    test_trending()
    test_bitcoin()
    print("All chatbot_logic tests passed.") 