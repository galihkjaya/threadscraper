import re
import unicodedata


def clean_text(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""

    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"https?://\S+|www\.\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"#(\w+)", r"\1", text)
    text = _remove_emoji(text)
    text = re.sub(r"[\x00-\x1f\x7f-\x9f]", " ", text)
    text = re.sub(r"([!?.,])\1+", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def _remove_emoji(text: str) -> str:
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002500-\U00002BEF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001f926-\U0001f937"
        "\U00010000-\U0010ffff"
        "\u2640-\u2642"
        "\u2600-\u2B55"
        "\u200d"
        "\u23cf"
        "\u23e9"
        "\u231a"
        "\ufe0f"
        "\u3030"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub(" ", text)


def is_valid(text: str, min_length: int = 10) -> bool:

    if not text or len(text) < min_length:
        return False

    if not re.search(r"[a-zA-Z]", text):
        return False

    digit_ratio = sum(c.isdigit() for c in text) / len(text)
    if digit_ratio > 0.8:
        return False

    words = text.lower().split()
    if len(words) >= 4:
        unique_ratio = len(set(words)) / len(words)
        if unique_ratio < 0.3:
            return False

    return True


def is_indonesian(text: str) -> bool:
    """
    Heuristik sederhana untuk deteksi bahasa Indonesia.
    Tidak 100% akurat, tapi cukup untuk filter kasar.
    Kalau mau akurat, pakai langdetect: pip install langdetect
    """
    id_keywords = {
        "yang", "dan", "di", "ke", "dari", "ini", "itu", "dengan",
        "untuk", "tidak", "ada", "saya", "aku", "kamu", "mereka",
        "adalah", "juga", "sudah", "akan", "bisa", "lebih", "sangat",
        "kalau", "tapi", "karena", "seperti", "dalam", "aja", "gak",
        "udah", "emang", "banget", "dong", "sih", "lah", "nih", "yg",
    }
    words = set(text.lower().split())
    overlap = words & id_keywords
    return len(overlap) >= 1