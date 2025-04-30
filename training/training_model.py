import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import joblib

df = pd.read_csv('data/spam_ham_dataset.csv')

# Clean up / select necessary columns
df = df[['label', 'text']]  # or use 'label_num' if you'd rather predict 0/1

# Drop rows with missing values
df = df.dropna()

# Stratified split
X_train, X_test, y_train, y_test = train_test_split(
    df['text'], df['label'], test_size=0.2, stratify=df['label'], random_state=42
)

print("Train distribution:")
print(y_train.value_counts(normalize=True))

print("Test distribution:")
print(y_test.value_counts(normalize=True))


# Vectorize text
vectorizer = TfidfVectorizer()
X_train_vec = vectorizer.fit_transform(X_train)

# Train model
model = MultinomialNB()
model.fit(X_train_vec, y_train)

# Save model and vectorizer
joblib.dump(model, 'app/model.pkl')
joblib.dump(vectorizer, 'app/vectorizer.pkl')