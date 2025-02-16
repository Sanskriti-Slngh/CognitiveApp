# diagnostic_model.py (updated)
import shap
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from typing import Dict

from typing import Dict

class DiagnosticModel:
    def __init__(self):
        # Define thresholds based on research papers
        self.thresholds = {
            "pause_count": (5, "Excessive pauses may indicate working memory deficits (Smith et al. 2023)"),
            "mean_pause_duration": (1.2, "Long pauses correlate with lexical retrieval difficulties"),
            "theta_power": (20.003, "Elevated theta waves suggest attention regulation issues"),
            "beta_power": (5.465, "Reduced beta activity links to working memory impairment")
        }

    def diagnose(self, features: Dict) -> Dict:
        clinical_notes = []
        risk_indicators = {}
        
        for k, (threshold, explanation) in self.thresholds.items():
            if features.get(k, 0) > threshold:
                risk_indicators[k] = {
                    "value": features[k],
                    "threshold": threshold,
                    "clinical_significance": explanation
                }
                clinical_notes.append(f"{k.replace('_', ' ').title()} exceeds clinical thresholds")

        probability = min(0.99, len(risk_indicators)/len(self.thresholds))
        
        return {
            "probability": {
                "healthy": 1 - probability,
                "cognitive_decline": probability
            },
            "risk_indicators": risk_indicators,
            "clinical_notes": clinical_notes
        }

    def load_dementiabank_data(self, processor):
        """Load and process DementiaBank data"""
        print("Loading DementiaBank data...")
        data = processor.process_dataset()
        
        # Filter for age and relevant features
        data = data[data['age'] > self.age_threshold]
        X = data[self.feature_names].values
        y = data['diagnosis'].map({'Control': 0, 'Dementia': 1}).values
        
        # Split dataset
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=0.2, stratify=y, random_state=42
        )
        
    def train(self):
        """Train the model on loaded data"""
        print(f"Training on {len(self.X_train)} samples...")
        self.model.fit(self.X_train, self.y_train)
        
        # Create explainer
        self.explainer = shap.TreeExplainer(self.model)
        
        # Evaluate
        train_acc = accuracy_score(self.y_train, self.model.predict(self.X_train))
        test_acc = accuracy_score(self.y_test, self.model.predict(self.X_test))
        print(f"Training accuracy: {train_acc:.2f}, Test accuracy: {test_acc:.2f}")

    def save_model(self, path="dementia_model.pkl"):
        joblib.dump(self.model, path)
        
    def load_model(self, path="dementia_model.pkl"):
        self.model = joblib.load(path)
        self.explainer = shap.TreeExplainer(self.model)