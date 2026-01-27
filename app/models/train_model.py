



# Step 0️⃣: Imports
import pandas as pd               # For loading CSV and handling DataFrames
import numpy as np                # For numerical operations
from sklearn.ensemble import RandomForestClassifier  # Our ML model
from sklearn.metrics import accuracy_score, classification_report  # Evaluation
import joblib                     # For saving the trained model
import os                         # For path management

# Step 1️⃣: Define paths
DATA_PATH = r"C:\Users\mjsiv\Desktop\ai_finance_project\data\processed\market_features.csv"
MODEL_PATH = r"C:\Users\mjsiv\Desktop\ai_finance_project\models\model_rf.pkl"                # Where we save the trained model

# Step 2️⃣: Load features
features = pd.read_csv(DATA_PATH, index_col=0, parse_dates=True)
print("Features loaded ✅")
print("Columns:", features.columns)

# Step 3️⃣: Create target column
# Target = 1 if SPY goes up tomorrow, 0 otherwise
returns_col = "SPY_daily_return"
features["target"] = (features[returns_col].shift(-1) > 0).astype(int)

# Step 4️⃣: Drop any rows with NaNs
features = features.dropna()
print("Shape after dropping NaNs:", features.shape)

# Step 5️⃣: Separate X (features) and y (target)
X = features.drop(columns=["target"])  # All columns except target
y = features["target"]                 # Target column

# Step 6️⃣: Time-series train/test split (no shuffling!)
split = int(len(features) * 0.8)
X_train, X_test = X.iloc[:split], X.iloc[split:]
y_train, y_test = y.iloc[:split], y.iloc[split:]

print(f"Training samples: {len(X_train)}, Testing samples: {len(X_test)}")

# Step 7️⃣: Train Random Forest classifier
model = RandomForestClassifier(
    n_estimators=100,  # Number of trees
    max_depth=5,       # Max depth to avoid overfitting
    random_state=42    # For reproducibility
)
model.fit(X_train, y_train)
print("Model trained ✅")

# Step 8️⃣: Evaluate model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print("\n📊 Model Performance:")
print("Accuracy:", accuracy)
print(classification_report(y_test, y_pred))

# Step 9️⃣: Save trained model
# Will be used later for generating trading signals
os.makedirs("../models", exist_ok=True)
joblib.dump(model, MODEL_PATH)
print(f"\n✅ Model saved to {MODEL_PATH}")
