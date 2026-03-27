"""
Train RandomForest risk classification model

This script generates synthetic but realistic training data and trains a risk model.
The model classifies portfolios into LOW, MODERATE, or HIGH risk based on market features.

Labeling rules (deterministic):
- LOW: risk_score > 1.0, volatility < 0.10, high debt/cash allocation
- MODERATE: risk_score between 0.3-1.0, volatility 0.10-0.20, balanced allocation
- HIGH: risk_score < 0.3, volatility > 0.20, high equity/commodity allocation
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os


def generate_training_data(n_samples=1000):
    """Generate synthetic but realistic portfolio data"""
    np.random.seed(42)
    
    data = []
    
    for _ in range(n_samples):
        # Generate features with realistic correlations
        
        # Allocation must sum to ~1.0
        equity_alloc = np.random.beta(2, 5)  # Skewed towards lower values
        remaining = 1.0 - equity_alloc
        
        debt_alloc = np.random.beta(3, 3) * remaining
        remaining -= debt_alloc
        
        commodity_alloc = np.random.beta(2, 8) * remaining
        remaining -= commodity_alloc
        
        cash_alloc = remaining
        
        # Volatility based on allocation
        volatility = (
            equity_alloc * 0.30 +
            debt_alloc * 0.05 +
            commodity_alloc * 0.15 +
            cash_alloc * 0.01 +
            np.random.normal(0, 0.02)  # Small noise
        )
        volatility = max(0.01, min(0.50, volatility))
        
        # Returns: higher risk assets tend to have higher returns (but not always)
        base_return = (
            equity_alloc * np.random.normal(0.12, 0.15) +
            debt_alloc * np.random.normal(0.06, 0.05) +
            commodity_alloc * np.random.normal(0.08, 0.12) +
            cash_alloc * np.random.normal(0.04, 0.02)
        )
        total_return = base_return
        
        # Momentum (small contribution)
        momentum = np.random.normal(0, 0.05)
        
        # Concentration (HHI)
        weights = [equity_alloc, debt_alloc, commodity_alloc, cash_alloc]
        concentration_hhi = sum(w**2 for w in weights)
        
        # Drawdown based on volatility and concentration
        drawdown = volatility * concentration_hhi
        
        # Risk score
        risk_score = total_return / (volatility + 1e-6)
        
        # Determine label based on rules
        if risk_score > 1.0 and volatility < 0.10:
            label = "LOW"
        elif risk_score < 0.3 or volatility > 0.20:
            label = "HIGH"
        else:
            label = "MODERATE"
        
        # Add some noise to make it more realistic (10% label noise)
        if np.random.random() < 0.10:
            labels = ["LOW", "MODERATE", "HIGH"]
            labels.remove(label)
            label = np.random.choice(labels)
        
        data.append({
            "total_return": total_return,
            "volatility_proxy": volatility,
            "momentum_proxy": momentum,
            "drawdown_proxy": drawdown,
            "risk_score": risk_score,
            "equity_allocation": equity_alloc,
            "debt_allocation": debt_alloc,
            "commodity_allocation": commodity_alloc,
            "cash_allocation": cash_alloc,
            "concentration_hhi": concentration_hhi,
            "label": label
        })
    
    return pd.DataFrame(data)


def train_model():
    """Train and save the risk classification model"""
    print("Generating training data...")
    df = generate_training_data(n_samples=2000)
    
    print(f"Dataset shape: {df.shape}")
    print(f"\nLabel distribution:")
    print(df['label'].value_counts())
    
    # Feature columns (must match FeatureExtractor output order)
    feature_cols = [
        "total_return",
        "volatility_proxy",
        "momentum_proxy",
        "drawdown_proxy",
        "risk_score",
        "equity_allocation",
        "debt_allocation",
        "commodity_allocation",
        "cash_allocation",
        "concentration_hhi"
    ]
    
    X = df[feature_cols].values
    y = df['label'].values
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\nTraining set size: {len(X_train)}")
    print(f"Test set size: {len(X_test)}")
    
    # Train model
    print("\nTraining RandomForest model...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=42,
        class_weight='balanced'
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\nModel accuracy: {accuracy:.3f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Feature importance
    print("\nFeature Importance:")
    for feature, importance in zip(feature_cols, model.feature_importances_):
        print(f"  {feature}: {importance:.4f}")
    
    # Save model
    model_dir = os.path.join(os.path.dirname(__file__), "..", "ml")
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "risk_model.pkl")
    
    joblib.dump(model, model_path)
    print(f"\nModel saved to: {model_path}")
    
    # Save feature names for reference
    feature_names_path = os.path.join(model_dir, "feature_names.txt")
    with open(feature_names_path, 'w') as f:
        f.write('\n'.join(feature_cols))
    print(f"Feature names saved to: {feature_names_path}")


if __name__ == "__main__":
    train_model()
