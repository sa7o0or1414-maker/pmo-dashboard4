from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

from core.features import build_features

def train_delay_model(df):
    df = build_features(df)
    if df["is_delayed_actual"].nunique() < 2 or len(df) < 30:
        return None, None

    X = df[["progress", "budget", "days_to_deadline", "status"]]
    y = df["is_delayed_actual"]

    pre = ColumnTransformer([
        ("num", SimpleImputer(strategy="median"), ["progress", "budget", "days_to_deadline"]),
        ("cat", Pipeline([
            ("imp", SimpleImputer(strategy="most_frequent")),
            ("oh", OneHotEncoder(handle_unknown="ignore"))
        ]), ["status"])
    ])

    pipe = Pipeline([
        ("pre", pre),
        ("model", LogisticRegression(max_iter=300))
    ])

    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, stratify=y)
    pipe.fit(Xtr, ytr)

    auc = roc_auc_score(yte, pipe.predict_proba(Xte)[:, 1])
    return pipe, auc

def predict_delay(pipe, df):
    df = build_features(df)
    df["delay_risk"] = pipe.predict_proba(
        df[["progress", "budget", "days_to_deadline", "status"]]
    )[:, 1]
    return df
