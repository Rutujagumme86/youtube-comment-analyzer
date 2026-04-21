import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

nltk.download('stopwords')

ps = PorterStemmer()
stop_words = set(stopwords.words('english'))

def clean_text(text):
    text = str(text)

    # HTML remove
    text = re.sub(r'<.*?>', '', text)

    # Lower
    text = text.lower()

    # URL remove
    text = re.sub(r"http\S+", "", text)

    # Only letters
    text = re.sub(r"[^a-zA-Z ]", "", text)

    words = text.split()

    # REMOVE STOPWORDS + SMALL WORDS
    words = [
        ps.stem(w) 
        for w in words 
        if w not in stop_words and len(w) > 3
    ]

    return " ".join(words)