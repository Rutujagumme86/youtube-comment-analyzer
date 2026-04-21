import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from preprocess import clean_text

# Load dataset
df = pd.read_csv("data/YoutubeCommentsDataSet.csv")

# IMPORTANT: column name adjust if needed
df.columns = df.columns.str.lower()

# Try to find comment column
if 'comment' not in df.columns:
    df.rename(columns={df.columns[0]: 'comment'}, inplace=True)

df['comment'] = df['comment'].astype(str).apply(clean_text)

# Create labels (basic logic - upgrade later)
df['sentiment'] = df['comment'].apply(
    lambda x: 1 if 'good' in x or 'great' in x or 'love' in x else 0
)

tfidf = TfidfVectorizer(max_features=5000)
X = tfidf.fit_transform(df['comment'])
y = df['sentiment']

model = LogisticRegression()
model.fit(X, y)

joblib.dump(model, "model.pkl")
joblib.dump(tfidf, "vectorizer.pkl")

print("Model trained successfully ✅")