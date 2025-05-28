from matplotlib import pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd

def plot_model(X_test, y_test, y_pred, title="Model Predictions", xlabel="Features", ylabel="Target"):
    """
    Plot the model predictions against the actual values.
    """
    plt.figure(figsize=(10, 6))
    plt.scatter(y_test, y_pred, alpha=0.7)
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid()
    plt.show()

def plot_feature_analysis(df, X_test, y_test, y_pred, title="Feature Analysis", xlabel="Features", ylabel="Target", features=None, target='prep_time'):
    """Plot individual features vs target variable"""
    
    if features is None:
        return
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    # Plot each feature vs prep time
    for i, feature in enumerate(features):
        axes[i].scatter(df[feature], df[target], alpha=0.6, color='blue')
        axes[i].set_xlabel(feature)
        axes[i].set_ylabel(ylabel)
        axes[i].set_title(f"{feature} vs {target}")
        
        # Add trend line
        z = np.polyfit(df[feature], df[target], 1)
        p = np.poly1d(z)
        axes[i].plot(df[feature], p(df[feature]), "r--", alpha=0.8)
    
    # Use last subplot for predicted vs actual
    axes[5].scatter(y_test, y_pred, alpha=0.7, color='green')
    axes[5].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
    axes[5].set_xlabel(xlabel)
    axes[5].set_ylabel(ylabel)
    axes[5].set_title(title)
    
    plt.tight_layout()
    plt.show()

def plot_correlation_matrix(df, title="Feature Correlation Matrix", numeric_cols=None):
    """Show correlations between all features"""
    
    # Select numeric columns
    
    corr_matrix = df[numeric_cols].corr()
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
    plt.title(title)
    plt.show()

def convert_to_dataframe(features, columns=None):
    """
    Convert a list of feature dictionaries to a pandas DataFrame.
    """
    if not features:
        return pd.DataFrame()
    
    df = pd.DataFrame(features)
    
    if columns:
        df = df[columns]
    
    df.fillna(0, inplace=True)
    return df