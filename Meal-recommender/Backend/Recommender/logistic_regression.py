from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, log_loss
from sklearn.utils.class_weight import compute_class_weight
import pandas as pd
from typing import List, Optional, Dict, Union
import numpy as np

class LogisticRegressionModel:
    def __init__(self):
        self.model = None
        self.preprocessor = None  # Will handle both scaling and encoding
        self.is_trained = False
        self.feature_columns = None
        self.label_encoders = {}
    
    def _create_preprocessor(self, X):
        """Create preprocessor for both numeric and categorical features."""
        numeric_features = X.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns.tolist()
        categorical_features = X.select_dtypes(exclude=['int64', 'float64', 'int32', 'float32']).columns.tolist()
        
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), numeric_features),
                ('cat', OneHotEncoder(drop='first', sparse_output=False), categorical_features)
            ],
            remainder='passthrough'
        )
        
        return preprocessor
    
    def train_model(self, df, feature_names: List[str], target_name: str, max_iter=1000):
        """Train the logistic regression model with the provided DataFrame."""

        print(f"Input df type: {type(df)}")
        
        # Validation checks
        if df.empty:
            raise ValueError("DataFrame is empty.")
        
        if target_name not in df.columns:
            raise ValueError(f"Target column '{target_name}' not found.")
        
        missing_features = [col for col in feature_names if col not in df.columns]
        if missing_features:
            raise ValueError(f"Missing feature columns: {missing_features}")
        
        # Store feature columns
        self.feature_columns = feature_names
        
        # Prepare data
        X = df[feature_names].copy()
        y = df[target_name].copy()
        
        # Handle missing values
        if X.isnull().any().any():
            print("Warning: Found missing values in features. Filling with appropriate defaults...")
            # Fill numeric with median, categorical with mode
            for col in X.columns:
                if X[col].dtype in ['int64', 'float64']:
                    X[col].fillna(X[col].median(), inplace=True)
                else:
                    X[col].fillna(X[col].mode().iloc[0] if not X[col].mode().empty else 'unknown', inplace=True)
        
        if y.isnull().any():
            print("Warning: Removing rows with missing target values...")
            mask = ~y.isnull()
            X = X[mask]
            y = y[mask]
        
        if len(X) == 0:
            raise ValueError("No valid training data after cleaning.")
        
        class_weights = compute_class_weight(
            class_weight='balanced',
            classes=y.unique(),
            y=y
        )

        class_weight_dict = {0: class_weights[0], 1: class_weights[1]}
        
        # Create and fit preprocessor
        self.preprocessor = self._create_preprocessor(X)
        X_processed = self.preprocessor.fit_transform(X)
        
        # Train model
        self.model = LogisticRegression(
            max_iter=max_iter,
            class_weight=class_weight_dict,
            random_state=42
        )
        self.model.fit(X_processed, y)
        self.is_trained = True

        # Log training details
        print(f"Model trained successfully on {len(X)} samples.")

    def train_model_with_sgd(self, df, feature_names: List[str], target_name: str, max_iter=1000, alpha=0.01):
        """Train the SGD classifier with the provided DataFrame."""
        
        print(f"Input df type: {type(df)}")
        
        # Validation checks
        if df.empty:
            raise ValueError("DataFrame is empty.")
        
        if target_name not in df.columns:
            raise ValueError(f"Target column '{target_name}' not found.")
        
        missing_features = [col for col in feature_names if col not in df.columns]
        if missing_features:
            raise ValueError(f"Missing feature columns: {missing_features}")
        
        # Store feature columns
        self.feature_columns = feature_names
        
        # Prepare data
        X = df[feature_names].copy()
        y = df[target_name].copy()
        
        # Handle missing values
        if X.isnull().any().any():
            print("Warning: Found missing values in features. Filling with appropriate defaults...")
            # Fill numeric with median, categorical with mode
            for col in X.columns:
                if X[col].dtype in ['int64', 'float64']:
                    X[col].fillna(X[col].median(), inplace=True)
                else:
                    X[col].fillna(X[col].mode().iloc[0] if not X[col].mode().empty else 'unknown', inplace=True)
        
        if y.isnull().any():
            print("Warning: Removing rows with missing target values...")
            mask = ~y.isnull()
            X = X[mask]
            y = y[mask]
        
        if len(X) == 0:
            raise ValueError("No valid training data after cleaning.")
        
        class_weights = compute_class_weight(
            class_weight='balanced',
            classes=y.unique(),
            y=y
        )

        class_weight_dict = {0: class_weights[0], 1: class_weights[1]}
        
        # Create and fit preprocessor
        self.preprocessor = self._create_preprocessor(X)
        X_processed = self.preprocessor.fit_transform(X)
        
        # Train model
        self.model = SGDClassifier(
            loss='log_loss',
            max_iter=max_iter,
            class_weight=class_weight_dict,
            random_state=42,
            learning_rate='optimal',
            eta0=alpha,
        )
        self.model.fit(X_processed, y)
        self.is_trained = True

        loss = log_loss(y, self.model.predict_proba(X_processed))
        print(f"Model trained successfully on {len(X)} samples with log loss: {loss:.4f} for learning rate {alpha}.")

    def train_and_evaluate(self, df, feature_names: List[str], target_name: str, 
                      test_size=0.2, max_iter=1000):
        """Train model and return evaluation metrics."""
        
        # Prepare data
        X = df[feature_names].copy()
        y = df[target_name].copy()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Train on training set
        train_df = pd.concat([X_train, y_train], axis=1)
        self.train_model(train_df, feature_names, target_name, max_iter=max_iter)
        
        # Evaluate on test set
        test_df = pd.concat([X_test, y_test], axis=1)
        predictions, probabilities = self.predict(test_df)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, predictions)
        report = classification_report(y_test, predictions)
        second_accuracy = self.model.score(self.preprocessor.transform(X_test), y_test)
        
        print(f"Test Accuracy: {accuracy:.3f}, Second Accuracy: {second_accuracy:.3f}")
        print("\nClassification Report:")
        print(report)
        print(self.analyze_feature_importance())
        
        return {
            'accuracy': accuracy,
            'predictions': predictions,
            'probabilities': probabilities,
            'actual': y_test.values
        }
    
    def _train_model_clean_data(self, df, feature_names: List[str], target_name: str, max_iter=1000):
        """Train model assuming data is already cleaned."""
        # Store feature columns
        self.feature_columns = feature_names
        
        # Prepare data (assuming it's already clean)
        X = df[feature_names].copy()
        y = df[target_name].copy()
        
        # Create and fit preprocessor
        self.preprocessor = self._create_preprocessor(X)
        X_processed = self.preprocessor.fit_transform(X)
        
        # Train model
        self.model.max_iter = max_iter
        self.model.fit(X_processed, y)
        self.is_trained = True

        print(f"Model trained successfully on {len(X)} samples.")

    def analyze_feature_importance(self):
        """Analyze feature contributions in the logistic regression model."""
        if not self.is_trained:
            print("Model not trained yet.")
            return
        
        # Get coefficients
        coefficients = self.model.coef_[0]  # For binary classification
        
        # Get feature names after preprocessing
        feature_names = self._get_feature_names_after_preprocessing()
        
        # Create coefficient dataframe
        coef_df = pd.DataFrame({
            'feature': feature_names,
            'coefficient': coefficients,
            'abs_coefficient': np.abs(coefficients)
        }).sort_values('abs_coefficient', ascending=False)
        
        print("Feature Importance (Logistic Regression Coefficients):")
        print("=" * 60)
        for _, row in coef_df.head(15).iterrows():  # Top 15 features
            direction = "↑" if row['coefficient'] > 0 else "↓"
            print(f"{row['feature']:25} {direction} {row['coefficient']:8.4f}")
        
        return coef_df

    def _get_feature_names_after_preprocessing(self):
        """Get feature names after one-hot encoding."""
        if self.preprocessor is None:
            return self.feature_columns
        
        # Get the feature names from the ColumnTransformer
        try:
            feature_names = self.preprocessor.get_feature_names_out()
            return feature_names
        except:
            # Fallback if get_feature_names_out doesn't work
            return [f"feature_{i}" for i in range(len(self.model.coef_[0]))]

    def predict(self, df):
        """Make predictions on new data."""
        if not self.is_trained:
            raise ValueError("Model has not been trained yet.")
        
        if self.feature_columns is None:
            raise ValueError("Feature columns not defined.")
        
        # Validate input
        missing_features = [col for col in self.feature_columns if col not in df.columns]
        if missing_features:
            raise ValueError(f"Missing feature columns for prediction: {missing_features}")
        
        X = df[self.feature_columns].copy()
        
        # Handle missing values (same logic as training)
        for col in X.columns:
            if X[col].dtype in ['int64', 'float64']:
                X[col].fillna(X[col].median(), inplace=True)
            else:
                X[col].fillna('unknown', inplace=True)
        
        # Transform and predict
        X_processed = self.preprocessor.transform(X)
        predictions = self.model.predict(X_processed)
        probabilities = self.model.predict_proba(X_processed)
        
        return predictions, probabilities[:, 1]  # Return probabilities for positive class
    
    def predict_with_conditional_weights(self, df, feature_columns, 
                                    feature_preferences: Optional[Dict[str, Dict[str, float]]] = None):
        """
        Make predictions with conditional feature weights based on specific feature values.
        
        Args:
            model: Trained sklearn LogisticRegression model
            preprocessor: Fitted sklearn preprocessor (ColumnTransformer)
            df: DataFrame with prediction data
            feature_columns: List of feature column names used in training
            feature_preferences: Dict mapping feature names to value-weight pairs
                            e.g., {
                                'type_of_meal': {'mexican': 1.5, 'italian': 1.2, 'fast_food': 0.8},
                                'has_dairy': {'True': 0.8},
                                'flavor_profile': {'sweet': 1.4, 'savory': 1.4}
                            }
                            Weights > 1 increase importance when value matches,
                            < 1 decrease importance when value matches
        
        Returns:
            tuple: (predictions, probabilities) where probabilities are for positive class
        """
        
        # Validate inputs
        if not hasattr(self.model, 'coef_'):
            raise ValueError("Model must be trained (have coefficients)")
        
        missing_features = [col for col in feature_columns if col not in df.columns]
        if missing_features:
            raise ValueError(f"Missing feature columns: {missing_features}")
        
        # Prepare data
        X = df[feature_columns].copy()
        
        # Handle missing values
        for col in X.columns:
            if X[col].dtype in ['int64', 'float64', 'int32', 'float32']:
                X[col].fillna(X[col].median(), inplace=True)
            else:
                X[col].fillna('unknown', inplace=True)
        
        # Transform data
        X_processed = self.preprocessor.transform(X)
        
        # If no preferences provided, use original model
        if feature_preferences is None or len(feature_preferences) == 0:
            predictions = self.model.predict(X_processed)
            probabilities = self.model.predict_proba(X_processed)
            return predictions, probabilities[:, 1]
        
        # Get feature names after preprocessing
        try:
            processed_feature_names = self.preprocessor.get_feature_names_out()
        except:
            processed_feature_names = [f"feature_{i}" for i in range(len(self.model.coef_[0]))]
        
        # Create row-specific weighted coefficients
        original_coef = self.model.coef_[0].copy()
        n_samples = len(X)
        n_features = len(original_coef)
        
        # Initialize coefficient matrix (one row per sample)
        weighted_coef_matrix = np.tile(original_coef, (n_samples, 1))
        
        # Apply conditional weights based on actual feature values
        for feature_name, value_weights in feature_preferences.items():
            if feature_name not in X.columns:
                print(f"Warning: Feature '{feature_name}' not found in data")
                continue
            
            feature_values = X[feature_name].values
            
            for target_value, weight in value_weights.items():
                # Find rows where feature matches target value
                if X[feature_name].dtype in ['object', 'category']:
                    # Categorical: exact match or contains
                    feature_series = X[feature_name]
                    mask = (feature_series == target_value) | \
                        (feature_series.astype(str).str.lower().str.contains(
                            str(target_value).lower(), na=False))
                else:
                    # Numerical: exact match
                    mask = (feature_values == target_value)
                
                matching_rows = np.where(mask)[0]
                
                if len(matching_rows) > 0:
                    # Find coefficient indices for this feature (handles one-hot encoding)
                    coef_indices = [i for i, name in enumerate(processed_feature_names) 
                                if feature_name.lower() in name.lower()]
                    
                    # Apply weight to matching rows and relevant coefficients
                    for row_idx in matching_rows:
                        for coef_idx in coef_indices:
                            weighted_coef_matrix[row_idx, coef_idx] *= weight
                    
                    print(f"Applied weight {weight} to {len(matching_rows)} rows where {feature_name}='{target_value}'")
        
        # Calculate predictions for each row with its specific weighted coefficients
        linear_predictions = np.sum(X_processed * weighted_coef_matrix, axis=1) + self.model.intercept_[0]
        
        # Apply sigmoid to get probabilities
        probabilities = 1 / (1 + np.exp(-linear_predictions))
        
        # Get binary predictions (threshold at 0.5)
        predictions = (probabilities > 0.5).astype(int)
        
        return predictions, probabilities
    
    def predict_with_simple_conditional_weights(self, df, feature_columns, 
                                          feature_preferences: Optional[Dict[str, Union[str, float]]] = None,
                                          default_weight: float = 5.5):
        """
        Simplified version: boost predictions when preferred values are present.
        
        Args:
            model: Trained sklearn LogisticRegression model
            preprocessor: Fitted sklearn preprocessor
            df: DataFrame with prediction data
            feature_columns: List of feature column names
            feature_preferences: Dict mapping feature names to preferred values
                            e.g., {'meal_type': 'mexican', 'flavor_profile': 'sweet'}
            default_weight: Weight to apply when preferred value is found (default: 1.5)
        
        Returns:
            tuple: (predictions, probabilities)
        """
        
        if feature_preferences is None:
            # Convert to the format expected by the main function
            return self.predict_with_conditional_weights(df, feature_columns, None)
        
        # Convert simple preferences to detailed format
        detailed_preferences = {}
        for feature, preferred_value in feature_preferences.items():
            detailed_preferences[feature] = {str(preferred_value): default_weight}
        
        return self.predict_with_conditional_weights(df, feature_columns, detailed_preferences)
    
    def predict_with_score_boost(self, df, feature_columns, 
                                    feature_preferences, boost_amount=0.4):
        """Make predictions with score boosting based on feature preferences.
        Args:
            df: DataFrame with prediction data
            feature_columns: List of feature column names used in training
            feature_preferences: Dict mapping feature names to value-weight pairs
                            e.g., {
                                'meal_type': {'mexican': 1.5, 'italian': 1.2, 'fast_food': 0.8},
                                'has_dairy': {'True': 0.8},
                                'flavor_profile': {'sweet': 1.4, 'savory': 1.4}
                            }
                            Weights > 1 increase importance when value matches,
                            < 1 decrease importance when value matches
                            boost_amount: Amount to boost or penalize probabilities (default: 0.4)
                            
            Returns:
            tuple: (predictions, boosted probabilities)"""
        
        # Get baseline predictions
        X = df[feature_columns].copy()
        
        # Handle missing values
        for col in X.columns:
            missing_count = X[col].isnull().sum()
            if missing_count > 0:
                print(f"Column {col} has {missing_count} missing values")
                
            if X[col].dtype in ['int64', 'float64', 'int32', 'float32']:
                X[col].fillna(X[col].median(), inplace=True)
            else:
                X[col].fillna('unknown', inplace=True)
        
        try:
            X_processed = self.preprocessor.transform(X)
        except Exception as e:
            print(f"ERROR in preprocessing: {e}")
            return None, None
        
        try:
            baseline_linear = X_processed @ self.model.coef_.T + self.model.intercept_
            baseline_probs = 1 / (1 + np.exp(-baseline_linear.flatten()))
        except Exception as e:
            print(f"ERROR in baseline prediction: {e}")
            return None, None
        
        if feature_preferences is None or len(feature_preferences) == 0:
            predictions = (baseline_probs > 0.5).astype(int)
            return predictions, baseline_probs
        
        # Apply fixed boosts
        boosted_probs = baseline_probs.copy()
        total_boosts_applied = 0
        
        for feature_name, preference_values in feature_preferences.items():
            if feature_name not in X.columns:
                print(f"ERROR: Feature '{feature_name}' not found in columns: {X.columns.tolist()}")
                continue
            
            feature_values = X[feature_name]
            
            # Handle both list and dict formats
            if isinstance(preference_values, list):
                value_weights = {str(val): 2.0 for val in preference_values}
            elif isinstance(preference_values, dict):
                value_weights = preference_values
            else:
                value_weights = {str(preference_values): 3.0}
            
            for target_value, weight in value_weights.items():
                # Find matching rows
                if X[feature_name].dtype in ['object', 'category']:
                    exact_matches = (feature_values == target_value)
                    contains_matches = feature_values.astype(str).str.lower().str.contains(
                        str(target_value).lower(), na=False)
                    mask = exact_matches | contains_matches
                else:
                    mask = (feature_values == target_value)
                
                matching_rows = np.where(mask)[0]
                
                if len(matching_rows) > 0:
                    
                    # Apply fixed boost based on weight
                    if weight > 1.0:
                        boost = boost_amount * (weight - 1.0)  # Positive boost
                        boosted_probs[matching_rows] += boost
                        total_boosts_applied += len(matching_rows)
                    elif weight < 1.0:
                        penalty = boost_amount * (1.0 - weight)  # Negative boost (penalty)
                        boosted_probs[matching_rows] -= penalty
                        total_boosts_applied += len(matching_rows)
        
        
        # Clip to valid probability range
        boosted_probs = np.clip(boosted_probs, 0, 1)
        predictions = (boosted_probs > 0.5).astype(int)
        
        return predictions, boosted_probs
    
    def predict_with_score_boost_simple(self, recommendation_features, 
                                   feature_columns, user_preference_features, boost_amount=0.4):
        """Simple wrapper that matches your calling convention."""
        
        return self.predict_with_score_boost(
            df=recommendation_features,
            feature_columns=feature_columns,
            feature_preferences=user_preference_features,
            boost_amount=boost_amount
        )

    def predict_proba(self, df):
        """Get prediction probabilities."""
        _, probabilities = self.predict(df)
        return probabilities[:, 1]  # Return probability of positive class
    