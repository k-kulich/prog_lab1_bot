from bot.utils.codes import ALPHABET, generate_tutor_code


def test_length():
    assert len(generate_tutor_code()) == 6


def test_alphabet():
    code = generate_tutor_code(20)
    assert all(ch in ALPHABET for ch in code)


def test_unique():
    codes = {generate_tutor_code() for _ in range(100)}
    assert len(codes) > 95