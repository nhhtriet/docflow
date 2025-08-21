from extract_text import extract_text

def test_extract_text(tmp_path):
    file = tmp_path / "sample.txt"
    file.write_text("Hello")
    assert extract_text(str(file)) == "Hello"
