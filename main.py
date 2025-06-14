from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import joblib
import pandas as pd
import os

class NurseResponse(BaseModel):
    NurseID: int
    FName: str
    LName: str
    PhoneNumber: int
    Email: str
    Experience: int
    Specialty: str
    City: str
    Street: str
    AverageRating: float
    ReviewCount: float
    Comment: str
    Score: float

app = FastAPI(title="نظام ترشيح الممرضين")

@app.get("/nurses/{city}", response_model=List[NurseResponse])
async def get_nurses_by_city(city: str):
    try:
        # تأكد من وجود الملف
        print("📁 الملفات الحالية:", os.listdir())

        # تحميل البيانات
        df = joblib.load("nurse_data.pkl")

        # التأكد من الأعمدة
        expected_columns = {"City", "Score"}
        if not expected_columns.issubset(df.columns):
            raise HTTPException(status_code=500, detail="⚠️ الأعمدة المطلوبة غير موجودة في البيانات.")

        # تنظيف المدينة
        city_normalized = city.strip().lower()
        df = df[df['City'].notna()].copy()
        df["City_clean"] = df["City"].astype(str).str.strip().str.lower()
        filtered = df[df["City_clean"] == city_normalized].sort_values("Score", ascending=False)

        if filtered.empty:
            raise HTTPException(status_code=404, detail=f"❌ لا يوجد ممرضين في المدينة: {city}")

        return filtered.drop(columns=["City_clean"]).to_dict("records")

    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="⚠️ ملف البيانات غير موجود.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"⚠️ خطأ داخلي في السيرفر: {str(e)}")
