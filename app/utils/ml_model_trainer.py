import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle
import os

def train_model():
    csv_path = r"E:\expense-auto-categorizer\sample_expenses.csv"

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV not found at {csv_path}")

    df = pd.read_csv(csv_path)

    df["text"] = df["description"].astype(str) + " " + df["merchant"].astype(str)

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(df["text"])
    y = df["category"]

    model = MultinomialNB()
    model.fit(X, y)

    model_path = r"E:\expense-auto-categorizer\app\models\category_model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump((vectorizer, model), f)

    print(f"✅ Model trained and saved at {model_path}")

if __name__ == "__main__":
    train_model()
