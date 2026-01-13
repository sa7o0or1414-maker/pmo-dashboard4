import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

from core.features import build_features


def train_delay_model(df_normalized: pd.DataFrame):
    """
    Trains a delay-risk model if enough labeled data exists.
    Uses is_delayed_actual as label.
    """
    df = build_features(df_normalized)

    y = df["is_delayed_actual"].astype(int)
    if y.nunique() < 2 or len(df) < 30:
        return None, None

    feature_cols = ["progress", "budget", "days_to_deadline", "municipality", "entity", "status"]
    X = df[feature_cols].copy()

    num_cols = ["progress", "budget", "days_to_deadline"]
    cat_cols = ["municipality", "entity", "status"]

    pre = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("imp", SimpleImputer(strategy="median"))]), num_cols),
            ("cat", Pipeline([
                ("imp", SimpleImputer(strategy="most_frequent")),
                ("oh", OneHotEncoder(handle_unknown="ignore"))
            ]), cat_cols),
        ]
    )

    model = LogisticRegression(max_iter=300)
    pipe = Pipeline([("pre", pre), ("model", model)])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    pipe.fit(X_train, y_train)

    auc = None
    try:
        proba = pipe.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(y_test, proba)
    except Exception:
        pass

    return pipe, auc


def predict_delay_risk(pipe, df_normalized: pd.DataFrame) -> pd.DataFrame:
    """
    Adds delay_risk + risk_bucket
    """
    df = build_features(df_normalized)
    feature_cols = ["progress", "budget", "days_to_deadline", "municipality", "entity", "status"]
    X = df[feature_cols].copy()

    proba = pipe.predict_proba(X)[:, 1]

    out = df_normalized.copy()
    out["delay_risk"] = proba
    out["risk_bucket"] = pd.cut(
        proba,
        bins=[-0.01, 0.33, 0.66, 1.01],
        labels=["Low", "Medium", "High"]
    )
    return out
