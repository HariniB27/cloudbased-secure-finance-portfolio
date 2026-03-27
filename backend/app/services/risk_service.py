import joblib
import os
from sqlalchemy.orm import Session
from typing import Optional
from app.models.asset import Asset
from app.schemas.portfolio import RiskPrediction
from app.ml.feature_extractor import FeatureExtractor


class RiskService:
    """Service for ML-based risk prediction"""
    
    _model = None
    _model_path = os.path.join(os.path.dirname(__file__), "..", "ml", "risk_model.pkl")
    
    @classmethod
    def load_model(cls):
        """Load the trained risk model"""
        if cls._model is None:
            if not os.path.exists(cls._model_path):
                raise FileNotFoundError(
                    f"Risk model not found at {cls._model_path}. "
                    "Please run 'python scripts/train_model.py' to train the model first."
                )
            
            try:
                cls._model = joblib.load(cls._model_path)
                print(f"✅ Risk model loaded successfully from {cls._model_path}")
            except Exception as e:
                raise RuntimeError(f"Failed to load risk model: {str(e)}")
        
        return cls._model
    
    @staticmethod
    def predict_risk(db: Session, user_id: int) -> RiskPrediction:
        """
        Predict portfolio risk level using ML model
        
        Args:
            db: Database session
            user_id: User ID to predict risk for
            
        Returns:
            RiskPrediction with risk_label, confidence, and features_used
        """
        # Get user's assets from database (includes updated current_value)
        assets = db.query(Asset).filter(Asset.user_id == user_id).all()
        
        # Handle empty portfolio
        if not assets:
            return RiskPrediction(
                risk_label="UNKNOWN",
                confidence=0.0,
                features_used={},
                message="No assets in portfolio. Add assets to see risk analysis."
            )
        
        # Load ML model
        try:
            model = RiskService.load_model()
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return RiskPrediction(
                risk_label="UNKNOWN",
                confidence=0.0,
                features_used={},
                message="Risk model not available. Please contact support."
            )
        
        # Extract features from portfolio
        try:
            features_dict = FeatureExtractor.calculate_features(assets)
            feature_vector = FeatureExtractor.get_feature_vector(assets)
        except Exception as e:
            print(f"Error extracting features: {str(e)}")
            return RiskPrediction(
                risk_label="UNKNOWN",
                confidence=0.0,
                features_used={},
                message=f"Error analyzing portfolio: {str(e)}"
            )
        
        # Make prediction
        try:
            prediction = model.predict(feature_vector)[0]
            probabilities = model.predict_proba(feature_vector)[0]
            
            # Get confidence for predicted class
            class_index = list(model.classes_).index(prediction)
            confidence = probabilities[class_index]
            
            return RiskPrediction(
                risk_label=prediction,
                confidence=round(float(confidence), 3),
                features_used=features_dict
            )
        
        except Exception as e:
            print(f"Error making prediction: {str(e)}")
            return RiskPrediction(
                risk_label="UNKNOWN",
                confidence=0.0,
                features_used=features_dict,  # Still return features for debugging
                message=f"Prediction failed: {str(e)}"
            )
    
    @staticmethod
    def get_risk_details(db: Session, user_id: int) -> dict:
        """
        Get detailed risk breakdown with explanations
        
        Returns:
            Dictionary with risk analysis details
        """
        prediction = RiskService.predict_risk(db, user_id)
        
        if prediction.risk_label == "UNKNOWN":
            return {
                "risk_label": "UNKNOWN",
                "confidence": 0.0,
                "message": prediction.message,
                "recommendations": []
            }
        
        features = prediction.features_used
        
        # Generate risk insights based on features
        insights = []
        recommendations = []
        
        # Volatility insights
        volatility = features.get('volatility_proxy', 0)
        if volatility > 0.25:
            insights.append("High volatility detected in portfolio")
            recommendations.append("Consider adding more stable assets like debt or gold")
        elif volatility < 0.1:
            insights.append("Low volatility - stable portfolio")
        
        # Return insights
        equity_pct = features.get('equity_allocation', 0) * 100
        if equity_pct > 70:
            insights.append(f"Heavy equity allocation ({equity_pct:.1f}%)")
            recommendations.append("Consider diversifying into debt or commodities")
        
        # Concentration insights
        hhi = features.get('concentration_hhi', 0)
        if hhi > 0.5:
            insights.append("Portfolio is highly concentrated")
            recommendations.append("Add more assets to improve diversification")
        
        return {
            "risk_label": prediction.risk_label,
            "confidence": prediction.confidence,
            "features": features,
            "insights": insights,
            "recommendations": recommendations
        }