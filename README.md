# SpamGuard: End-to-End ML Spam Filter API

A full-stack machine learning project that classifies messages as spam or ham using an ML model exposed via a REST API.

---

## 🚀 Features

- Trained on real-world SMS spam dataset
- Exposes an API endpoint using FastAPI
- Containerized with Docker
- Deployable to Render, AWS, or HuggingFace Spaces
- (Optional) Gmail API integration to scan real emails
- (Optional) CI/CD automation with GitLab

---

## 📊 Model

- **Library:** scikit-learn
- **Vectorizer:** TfidfVectorizer
- **Model:** Multinomial Naive Bayes
- Dataset: [SMS Spam Collection](https://www.kaggle.com/datasets/uciml/sms-spam-collection-dataset)

