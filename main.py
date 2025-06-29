import os
import pandas as pd
import pickle
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from surprise import SVD, Dataset, Reader

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# === Constants ===
DATA_FILE = "interaction_df.pkl"
MODEL_FILE = "svd_model.pkl"

# === Load interaction data ===
if not os.path.exists(DATA_FILE):
    raise FileNotFoundError(f"❌ Required data file '{DATA_FILE}' is missing. Upload it to your Render repo.")
interaction_df = pd.read_pickle(DATA_FILE)
print("✅ interaction_df.pkl loaded")

# === Create product lookup dict ===
product_lookup = interaction_df.drop_duplicates('product_id').set_index('product_id')['product_name'].to_dict()

# === Load or train the model ===
if os.path.exists(MODEL_FILE):
    with open(MODEL_FILE, "rb") as f:
        model = pickle.load(f)
    print("✅ Loaded existing model from disk")
else:
    print("⚠️ Model not found – training new SVD model...")
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(interaction_df[['employee_id', 'product_id', 'order_count']], reader)
    trainset = data.build_full_trainset()
    model = SVD()
    model.fit(trainset)
    with open(MODEL_FILE, "wb") as f:
        pickle.dump(model, f)
    print("✅ Model trained and saved to svd_model.pkl")

# === Routes ===
@app.get("/", response_class=HTMLResponse)
async def form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/recommend", response_class=HTMLResponse)
async def recommend(request: Request, employee_id: int = Form(...)):
    ordered = interaction_df[interaction_df['employee_id'] == employee_id]
    ordered_product_ids = set(ordered['product_id'])
    repeat_items = ordered.sort_values('order_count', ascending=False).to_dict('records')

    recommendations = []
    for pid in interaction_df['product_id'].unique():
        if pid not in ordered_product_ids:
            pred = model.predict(employee_id, pid)
            recommendations.append((pid, pred.est))

    recommendations.sort(key=lambda x: x[1], reverse=True)
    reco_items = [{"name": product_lookup.get(pid, "Unknown"), "score": round(score, 2)}
                  for pid, score in recommendations[:5]]

    return templates.TemplateResponse("result.html", {
        "request": request,
        "employee_id": employee_id,
        "repeat_items": repeat_items,
        "recommendations": reco_items
    })
