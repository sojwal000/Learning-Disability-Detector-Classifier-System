"""
ML Model Training and Management
Handles training, versioning, and persistence of ML models
"""
import os
import json
import pickle
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import joblib

# Model storage paths
MODEL_DIR = "app/ml/models"
os.makedirs(MODEL_DIR, exist_ok=True)

class ModelTrainer:
    """Train and manage ML models for learning disability detection"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.model_metadata = {}
        
    def train_sklearn_classifier(
        self,
        X: np.ndarray,
        y: np.ndarray,
        model_type: str = "random_forest",
        model_name: str = "dyslexia_classifier",
        test_size: float = 0.2
    ) -> Dict:
        """
        Train a scikit-learn classifier
        
        Args:
            X: Feature matrix
            y: Target labels
            model_type: Type of model (random_forest, gradient_boosting)
            model_name: Name for saving the model
            test_size: Proportion of test set
            
        Returns:
            Dictionary with training results and metrics
        """
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Initialize model
        if model_type == "random_forest":
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1
            )
        elif model_type == "gradient_boosting":
            model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Train model
        print(f"Training {model_type} model...")
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Cross-validation
        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
        
        # Get feature importance
        feature_importance = None
        if hasattr(model, 'feature_importances_'):
            feature_importance = model.feature_importances_.tolist()
        
        # Create metadata
        metadata = {
            "model_name": model_name,
            "model_type": model_type,
            "framework": "sklearn",
            "trained_at": datetime.utcnow().isoformat(),
            "accuracy": float(accuracy),
            "cv_mean_accuracy": float(cv_scores.mean()),
            "cv_std_accuracy": float(cv_scores.std()),
            "n_samples_train": len(X_train),
            "n_samples_test": len(X_test),
            "n_features": X.shape[1],
            "classes": list(set(y)),
            "feature_importance": feature_importance,
            "classification_report": classification_report(y_test, y_pred, output_dict=True),
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist()
        }
        
        # Save model and scaler
        version = self._get_next_version(model_name)
        model_path = os.path.join(MODEL_DIR, f"{model_name}_v{version}.pkl")
        scaler_path = os.path.join(MODEL_DIR, f"{model_name}_scaler_v{version}.pkl")
        metadata_path = os.path.join(MODEL_DIR, f"{model_name}_metadata_v{version}.json")
        
        joblib.dump(model, model_path)
        joblib.dump(scaler, scaler_path)
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Store in memory
        self.models[model_name] = model
        self.scalers[model_name] = scaler
        self.model_metadata[model_name] = metadata
        
        print(f"Model saved: {model_path}")
        print(f"Accuracy: {accuracy:.4f}")
        print(f"CV Score: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        
        return {
            "model_path": model_path,
            "scaler_path": scaler_path,
            "metadata": metadata,
            "version": version
        }
    
    def train_neural_network(
        self,
        X: np.ndarray,
        y: np.ndarray,
        model_name: str = "dyslexia_nn",
        epochs: int = 50,
        batch_size: int = 32,
        test_size: float = 0.2
    ) -> Dict:
        """
        Train a neural network using TensorFlow/Keras
        
        Args:
            X: Feature matrix
            y: Target labels
            model_name: Name for saving the model
            epochs: Number of training epochs
            batch_size: Batch size for training
            test_size: Proportion of test set
            
        Returns:
            Dictionary with training results and metrics
        """
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Convert labels to categorical
        n_classes = len(set(y))
        y_train_cat = keras.utils.to_categorical(y_train, n_classes)
        y_test_cat = keras.utils.to_categorical(y_test, n_classes)
        
        # Build model
        model = keras.Sequential([
            layers.Dense(128, activation='relu', input_shape=(X.shape[1],)),
            layers.Dropout(0.3),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(32, activation='relu'),
            layers.Dense(n_classes, activation='softmax')
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # Train model
        print(f"Training neural network...")
        history = model.fit(
            X_train_scaled, y_train_cat,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.2,
            verbose=1
        )
        
        # Evaluate
        test_loss, test_accuracy = model.evaluate(X_test_scaled, y_test_cat, verbose=0)
        
        # Create metadata
        metadata = {
            "model_name": model_name,
            "model_type": "neural_network",
            "framework": "tensorflow",
            "trained_at": datetime.utcnow().isoformat(),
            "accuracy": float(test_accuracy),
            "loss": float(test_loss),
            "epochs": epochs,
            "batch_size": batch_size,
            "n_samples_train": len(X_train),
            "n_samples_test": len(X_test),
            "n_features": X.shape[1],
            "n_classes": n_classes,
            "history": {
                "accuracy": [float(x) for x in history.history['accuracy']],
                "val_accuracy": [float(x) for x in history.history['val_accuracy']],
                "loss": [float(x) for x in history.history['loss']],
                "val_loss": [float(x) for x in history.history['val_loss']]
            }
        }
        
        # Save model and scaler
        version = self._get_next_version(model_name)
        model_path = os.path.join(MODEL_DIR, f"{model_name}_v{version}.h5")
        scaler_path = os.path.join(MODEL_DIR, f"{model_name}_scaler_v{version}.pkl")
        metadata_path = os.path.join(MODEL_DIR, f"{model_name}_metadata_v{version}.json")
        
        model.save(model_path)
        joblib.dump(scaler, scaler_path)
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Store in memory
        self.models[model_name] = model
        self.scalers[model_name] = scaler
        self.model_metadata[model_name] = metadata
        
        print(f"Model saved: {model_path}")
        print(f"Test Accuracy: {test_accuracy:.4f}")
        print(f"Test Loss: {test_loss:.4f}")
        
        return {
            "model_path": model_path,
            "scaler_path": scaler_path,
            "metadata": metadata,
            "version": version
        }
    
    def load_model(self, model_name: str, version: Optional[int] = None) -> Tuple:
        """
        Load a trained model and its scaler
        
        Args:
            model_name: Name of the model
            version: Specific version to load (default: latest)
            
        Returns:
            Tuple of (model, scaler, metadata)
        """
        if version is None:
            version = self._get_latest_version(model_name)
        
        model_path = os.path.join(MODEL_DIR, f"{model_name}_v{version}.pkl")
        h5_path = os.path.join(MODEL_DIR, f"{model_name}_v{version}.h5")
        scaler_path = os.path.join(MODEL_DIR, f"{model_name}_scaler_v{version}.pkl")
        metadata_path = os.path.join(MODEL_DIR, f"{model_name}_metadata_v{version}.json")
        
        # Load metadata
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        # Load scaler
        scaler = joblib.load(scaler_path)
        
        # Load model (check if sklearn or tensorflow)
        if os.path.exists(model_path):
            model = joblib.load(model_path)
        elif os.path.exists(h5_path):
            model = keras.models.load_model(h5_path)
        else:
            raise FileNotFoundError(f"Model not found: {model_name}")
        
        self.models[model_name] = model
        self.scalers[model_name] = scaler
        self.model_metadata[model_name] = metadata
        
        return model, scaler, metadata
    
    def predict(self, model_name: str, features: np.ndarray) -> Dict:
        """
        Make predictions using a trained model
        
        Args:
            model_name: Name of the model
            features: Feature array
            
        Returns:
            Dictionary with predictions and confidence scores
        """
        if model_name not in self.models:
            self.load_model(model_name)
        
        model = self.models[model_name]
        scaler = self.scalers[model_name]
        
        # Scale features
        features_scaled = scaler.transform(features.reshape(1, -1))
        
        # Predict
        if hasattr(model, 'predict_proba'):
            # Sklearn model
            prediction = model.predict(features_scaled)[0]
            probabilities = model.predict_proba(features_scaled)[0]
            confidence = float(max(probabilities))
        else:
            # Neural network
            probabilities = model.predict(features_scaled, verbose=0)[0]
            prediction = np.argmax(probabilities)
            confidence = float(probabilities[prediction])
        
        return {
            "prediction": int(prediction),
            "confidence": confidence,
            "probabilities": probabilities.tolist()
        }
    
    def get_model_performance(self, model_name: str, version: Optional[int] = None) -> Dict:
        """Get performance metrics for a model"""
        if version is None:
            version = self._get_latest_version(model_name)
        
        metadata_path = os.path.join(MODEL_DIR, f"{model_name}_metadata_v{version}.json")
        
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        return metadata
    
    def list_models(self) -> List[Dict]:
        """List all available models with their versions"""
        models = {}
        
        for filename in os.listdir(MODEL_DIR):
            if filename.endswith('_metadata.json'):
                with open(os.path.join(MODEL_DIR, filename), 'r') as f:
                    metadata = json.load(f)
                    model_name = metadata['model_name']
                    
                    if model_name not in models:
                        models[model_name] = []
                    
                    models[model_name].append(metadata)
        
        return [
            {
                "model_name": name,
                "versions": sorted(versions, key=lambda x: x['trained_at'], reverse=True)
            }
            for name, versions in models.items()
        ]
    
    def _get_next_version(self, model_name: str) -> int:
        """Get the next version number for a model"""
        latest = self._get_latest_version(model_name)
        return latest + 1 if latest is not None else 1
    
    def _get_latest_version(self, model_name: str) -> Optional[int]:
        """Get the latest version number for a model"""
        versions = []
        
        for filename in os.listdir(MODEL_DIR):
            if filename.startswith(model_name) and 'metadata' in filename:
                # Extract version from filename like "model_v1_metadata.json"
                version = int(filename.split('_v')[1].split('_')[0])
                versions.append(version)
        
        return max(versions) if versions else None


# Global model trainer instance
model_trainer = ModelTrainer()
