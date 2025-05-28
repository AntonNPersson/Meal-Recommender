from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, SGDRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class MultipleLinearRegressionModel:
    def __init__(self):
        self.model = LinearRegression()
        self.scaler = StandardScaler()
        self.encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        
        # Store training info for predictions
        self.feature_columns = None
        self.category_columns = None
        self.is_trained = False
        
    def train_model(self, df, feature_names=['ingredient_count', 'instruction_length', 'prep_keyworks_count', 'fresh_ratio'], 
                   target_name='estimated_prep_time', categorical_column='category'):
        """
        Train the multiple linear regression model using the provided DataFrame.
        """
        if df.empty:
            print("DataFrame is empty. Cannot train model.")
            return
            
        # Check if columns exist
        missing_cols = [col for col in feature_names if col not in df.columns]
        if missing_cols:
            print(f"Missing columns: {missing_cols}")
            return
            
        if target_name not in df.columns:
            print(f"Target column '{target_name}' not found in DataFrame")
            return
       
        X = df[feature_names].copy()
        Y = df[target_name].copy()
        
        # Handle categorical variables
        if categorical_column in df.columns:
            category_dummies = pd.get_dummies(df[categorical_column], prefix='category')
            self.category_columns = category_dummies.columns.tolist()  # Store for predictions
            X = pd.concat([X, category_dummies], axis=1)
        else:
            self.category_columns = []
            
        # Store feature column names for predictions
        self.feature_columns = X.columns.tolist()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        self.is_trained = True
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"Model trained with MSE: {mse:.4f}, MAE: {mae:.4f}, R2: {r2:.4f}")
        
        # Feature importances
        feature_importances = self.model.coef_
        print("\nFeature Importances:")
        for name, importance in zip(self.feature_columns, feature_importances):
            print(f"{name}: {importance:.4f}")
            
        return X_test, y_test, y_pred
   
    def train_model_with_sgd(self, df, learning_rate=0.01, limit=1000, feature_names=['ingredient_count', 'instruction_length', 'prep_keyworks_count', 'fresh_ratio'], 
                            target_name='prep_time_target', categorical_column='category'):
        """
        Train the model using Stochastic Gradient Descent with a specified learning rate.
        """
        if df.empty:
            print("DataFrame is empty. Cannot train model.")
            return
            
        # Check if columns exist
        missing_cols = [col for col in feature_names if col not in df.columns]
        if missing_cols:
            print(f"Missing columns: {missing_cols}")
            return
            
        if target_name not in df.columns:
            print(f"Target column '{target_name}' not found in DataFrame")
            return
       
        X = df[feature_names].copy()
        Y = df[target_name].copy()
        
        # Handle categorical variables
        if categorical_column in df.columns:
            category_dummies = pd.get_dummies(df[categorical_column], prefix='category')
            self.category_columns = category_dummies.columns.tolist()
            X = pd.concat([X, category_dummies], axis=1)
        else:
            self.category_columns = []
            
        # Store feature column names for predictions
        self.feature_columns = X.columns.tolist()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Use SGD with learning rate (eta0 parameter)
        self.model = SGDRegressor(
            eta0=learning_rate,           # Learning rate
            learning_rate='constant',     # Keep learning rate constant
            max_iter=limit, 
            tol=1e-3,
            random_state=42
        )
        
        self.model.fit(X_train_scaled, y_train)
        self.is_trained = True
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"SGD Model trained with learning_rate={learning_rate}")
        print(f"MSE: {mse:.4f}, MAE: {mae:.4f}, R2: {r2:.4f}")
        
        # Feature importances
        feature_importances = self.model.coef_
        print("\nFeature Importances:")
        for name, importance in zip(self.feature_columns, feature_importances):
            print(f"{name}: {importance:.4f}")
            
        return X_test, y_test, y_pred
    
    def compare_learning_rates(self, df, feature_names, target_name, learning_rates=[0.0001, 0.001, 0.01]):
        """
        Fixed version that actually works
        """
        X = df[feature_names].copy()
        y = df[target_name].copy()
        
        # Remove any NaN values
        mask = ~(X.isnull().any(axis=1) | y.isnull())
        X = X[mask]
        y = y[mask]
        
        if len(X) == 0:
            print("No valid data after removing NaN values!")
            return
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features using a fresh scaler
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        
        plt.figure(figsize=(15, 10))
        
        for idx, lr in enumerate(learning_rates):
            print(f"Training with learning rate: {lr}")
            
            # Initialize weights and bias for this learning rate
            n_samples, n_features = X_train_scaled.shape
            weights = np.random.normal(0, 0.01, n_features)
            bias = 0
            cost_history = []
            
            # Convert y_train to numpy array to avoid pandas indexing issues
            y_train_array = y_train.values
            
            for epoch in range(100):  # More epochs to see convergence
                epoch_cost = 0
                
                # Shuffle data for this epoch
                indices = np.random.permutation(n_samples)
                X_shuffled = X_train_scaled[indices]
                y_shuffled = y_train_array[indices]
                
                for i in range(n_samples):
                    # Forward pass
                    prediction = np.dot(X_shuffled[i], weights) + bias
                    error = prediction - y_shuffled[i]
                    epoch_cost += error ** 2
                    
                    # Compute gradients
                    gradient_w = error * X_shuffled[i]
                    gradient_b = error
                    
                    # Update weights and bias
                    weights -= lr * gradient_w
                    bias -= lr * gradient_b
                
                # Calculate average cost for this epoch
                avg_cost = epoch_cost / n_samples
                cost_history.append(avg_cost)
                
                # Early stopping if cost becomes too large (diverging)
                if avg_cost > 1e10:
                    print(f"Learning rate {lr} diverged at epoch {epoch}")
                    break
            
            # Plot results
            plt.subplot(2, 3, idx + 1)
            plt.plot(cost_history)
            plt.title(f'Learning Rate = {lr}')
            plt.xlabel('Epoch')
            plt.ylabel('MSE')
            plt.grid(True)
            
            # Log scale subplot
            plt.subplot(2, 3, idx + 4)
            plt.plot(cost_history)
            plt.title(f'LR = {lr} (Log Scale)')
            plt.xlabel('Epoch')
            plt.ylabel('MSE')
            plt.yscale('log')
            plt.grid(True)
            
            # Print final cost
            if cost_history:
                print(f"Learning rate {lr}: Final cost = {cost_history[-1]:.4f}")
        
        plt.tight_layout()
        plt.show()
   
    def predict(self, features_dict):
        """
        Predict using the trained model for a single recipe or dictionary of features.
        
        Args:
            features_dict: Dictionary with feature values, e.g.:
                {
                    'ingredient_count': 8,
                    'instruction_length': 150,
                    'prep_keywords_count': 3,
                    'fresh_ratio': 0.4,
                    'category': 'Dessert'  # optional
                }
        """
        if not self.is_trained:
            print("Model is not trained yet. Call train_model() first.")
            return None
            
        # Convert single dict to DataFrame format
        if isinstance(features_dict, dict):
            # Create feature array in the same order as training
            feature_values = []
            
            # Add numerical features first
            numerical_features = [col for col in self.feature_columns if not col.startswith('category_')]
            for feature in numerical_features:
                if feature in features_dict:
                    feature_values.append(features_dict[feature])
                else:
                    print(f"Warning: Missing feature '{feature}', using 0")
                    feature_values.append(0)
            
            # Add category features
            category = features_dict.get('category', 'Unknown')
            for cat_col in self.category_columns:
                if cat_col == f'category_{category}':
                    feature_values.append(1)
                else:
                    feature_values.append(0)
            
            # Convert to array and reshape
            X = np.array(feature_values).reshape(1, -1)
        else:
            X = features_dict  # Assume it's already in correct format
       
        # Scale and predict
        X_scaled = self.scaler.transform(X)
        prediction = self.model.predict(X_scaled)
        
        return prediction[0] if len(prediction) == 1 else prediction
    
    def predict_dataframe(self, df, feature_names, categorical_column='category'):
        """
        Predict for multiple recipes in a DataFrame format.
        """
        if not self.is_trained:
            print("Model is not trained yet. Call train_model() first.")
            return None
            
        # Prepare features same way as training
        X = df[feature_names].copy()
        
        if categorical_column in df.columns:
            category_dummies = pd.get_dummies(df[categorical_column], prefix='category')
            # Ensure same columns as training
            for col in self.category_columns:
                if col not in category_dummies.columns:
                    category_dummies[col] = 0
            # Reorder columns to match training
            category_dummies = category_dummies[self.category_columns]
            X = pd.concat([X, category_dummies], axis=1)
        
        # Scale and predict
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        
        return predictions