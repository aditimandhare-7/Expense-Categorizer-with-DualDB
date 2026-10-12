import pickle

model_path = r"E:\expense-auto-categorizer\app\models\category_model.pkl"

with open(model_path, "rb") as f:
    vectorizer, model = pickle.load(f)

def predict_category(description, merchant):
    text = description + " " + merchant
    X = vectorizer.transform([text])
    return model.predict(X)[0]
