import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import joblib

# Load dataset
df = pd.read_csv("uk_room_rental_dataset.csv")
df = df.drop(columns=['occupant_age'])

# Preprocess
df['bills_included'] = df['bills_included'].astype(int)
df['short_term'] = df['short_term'].astype(int)
df['is_en_suite'] = df['is_en_suite'].astype(int)

categorical_cols = [
    'postcode', 'rent_type', 'property_type', 'room_size',
    'room_furnishing', 'share_occupation', 'room_for',
    'share_gender', 'household_option', 'property_preference',
    'property_habit', 'room_suitable_for'
]
df = pd.get_dummies(df, columns=categorical_cols)

X = df.drop('rate', axis=1)
y = df['rate']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestRegressor()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print("MAE: £", round(mean_absolute_error(y_test, y_pred), 2))

# Save the model
joblib.dump(model, 'rental_price_model.pkl')
print("Model saved as rental_price_model.pkl")
