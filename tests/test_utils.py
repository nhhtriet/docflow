from utils import clean_text

def test_clean_text():
    assert clean_text("ABC") == "abc"
