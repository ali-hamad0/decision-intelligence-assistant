import re

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()

_NEGATION_WORDS = {
    "no", "not", "never", "nobody", "nothing", "neither",
    "dont", "don't", "doesn't", "didn't", "won't", "can't",
    "cannot", "couldn't", "shouldn't", "wouldn't",
}


def extract_features(text: str) -> dict[str, float]:
    scores = _analyzer.polarity_scores(text)
    words = text.lower().split()

    return {
        "text_length": float(len(text)),
        "exclamation_count": float(text.count("!")),
        "uppercase_ratio": sum(1 for c in text if c.isupper()) / max(len(text), 1),
        "multiple_punctuation": float(len(re.findall(r"[!?]{2,}", text))),
        "sentiment_compound": scores["compound"],
        "sentiment_neg": scores["neg"],
        "negation_count": float(sum(1 for w in words if w in _NEGATION_WORDS)),
    }
