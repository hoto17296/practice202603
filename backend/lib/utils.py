import re

from lib.logger import logger


def sanitize_string(text: str, remove_newlines: bool = False) -> str:
    """文字列に含まれている妙な文字コードを取り除く"""
    # 制御文字を取り除く
    text = re.sub(r"[\x00-\x09\x0B\x0C\x0E-\x1F\x7F-\x9F]", "", text)

    # 改行文字を取り除く
    if remove_newlines:
        text = re.sub(r"[\r\n]", "", text)

    # Python 3 はサロゲートペアを扱えないため Python で扱えるように変換する
    text_utf16_bytes = text.encode("utf-16", "surrogatepass")
    try:
        return text_utf16_bytes.decode("utf-16")
    except UnicodeDecodeError:
        # 稀に decode に失敗するケースがあるので、どの文字列が失敗したかわかるようにログに吐く
        logger.error(f"content: {text_utf16_bytes}")
        raise
