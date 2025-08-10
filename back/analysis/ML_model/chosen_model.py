# import pandas as pd
# import numpy as np
# import joblib
# import os
# from sklearn.preprocessing import StandardScaler
# from xgboost import XGBClassifier
# # from google.colab import files

# # --- הגדרת נתיבים ---
# # הגדרת נתיבים דינמית כך שהסקריפט יעבוד מכל מקום
# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# MODEL_PATH = os.path.join(SCRIPT_DIR, 'final_xgb_model.pkl')
# SCALER_PATH = os.path.join(SCRIPT_DIR, 'scaler_xgb_model.pkl')
# # הנחה שקובץ הנתונים נמצא גם הוא באותה התיקייה
# DATA_PATH = os.path.join(SCRIPT_DIR, 'data_for_model_top31_features.csv')

# # --- אימון המודל ---

# # === טען את הדאטה
# try:
#     df = pd.read_csv(DATA_PATH)
# except FileNotFoundError:
#     print(f"Error: Data file not found at {DATA_PATH}")
#     # אם הקובץ לא נמצא, אין טעם להמשיך
#     exit()

# df.dropna(inplace=True)
# X = df.drop(columns=["Indicator"])
# y = df["Indicator"]

# # הסר מזהה זמן אם קיים
# if "half_day_key" in X.columns:
#     X = X.drop(columns=["half_day_key"])

# # === סקלינג
# scaler = StandardScaler()
# X_scaled = scaler.fit_transform(X)

# # === הגדרת מודל עם פרמטרים שנבחרו
# final_model = XGBClassifier(
#     learning_rate=0.01,
#     max_depth=5,
#     n_estimators=100,
#     use_label_encoder=False,
#     eval_metric='logloss',
#     tree_method='gpu_hist',
#     predictor='gpu_predictor'
# )

# # === אימון על כל הדאטה
# final_model.fit(X_scaled, y)

# # === שמירה
# joblib.dump(final_model, MODEL_PATH)
# joblib.dump(scaler, SCALER_PATH)
# print(f"Model saved successfully to: {MODEL_PATH}")
# print(f"Scaler saved successfully to: {SCALER_PATH}")


# # === הורדה (רלוונטי רק ל-Google Colab)
# # files.download(MODEL_PATH)
# # files.download(SCALER_PATH)


# # --- דוגמה לטעינה ושימוש ---
# # ניתן להריץ את החלק הזה בנפרד (למשל, ב-views.py) כדי לבצע תחזיות
# print("\n--- Loading model for prediction demo ---")
# try:
#     model = joblib.load(MODEL_PATH)
#     scaler = joblib.load(SCALER_PATH)
#     print("Model and scaler loaded successfully.")

#     # # כדי לבצע תחזית על מידע חדש (X_new), יש להסיר את ההערות מהשורות הבאות
#     # # ולוודא שהמשתנה X_new מוגדר ומכיל את הדאטה החדש באותו הפורמט
#     # X_new_scaled = scaler.transform(X_new)
#     # pred = model.predict(X_new_scaled)
#     # print(f"Prediction result: {pred}")

# except FileNotFoundError:
#     print("Error: Model or scaler file not found. Please run the training part of the script first.")
# except NameError:
#     print("To run a prediction, define a variable 'X_new' with the new data.")