import pandas as pd
import gdown
import os

# === Step 1: Download only if files not present ===
order_items_file = "accenture_order_items.csv"
orders_file = "accenture_sales_order.csv"

gdown.download("https://drive.google.com/uc?id=1t4Wu-j7sGrHWFdgpcq6QSb8UXWSRIBED", order_items_file, quiet=False) if not os.path.exists(order_items_file) else None
gdown.download("https://drive.google.com/uc?id=1Y3NcEoLMn75wpaqL409oL3zRYxZx2Mt6", orders_file, quiet=False) if not os.path.exists(orders_file) else None

# === Step 2: Read CSVs with minimal memory ===
orders = pd.read_csv(orders_file, usecols=["id", "employee_id", "status"], low_memory=False)
order_items = pd.read_csv(order_items_file, usecols=["order_id", "product_id", "product_name"])

# === Step 3: Rename & merge only necessary parts ===
orders = orders.rename(columns={"id": "order_id_master"})
merged = order_items.merge(orders, left_on="order_id", right_on="order_id_master", how="inner")

# === Step 4: Filter to only 'delivered' orders ===
delivered = merged[merged["status"] == "delivered"]

# === Step 5: Clean up and drop unnecessary cols ===
df = delivered[["employee_id", "product_id", "product_name"]].copy()

# === Step 6: Group and clip interactions ===
interaction_df = (
    df.groupby(["employee_id", "product_id", "product_name"])
    .size()
    .reset_index(name="order_count")
)
interaction_df["order_count"] = interaction_df["order_count"].clip(upper=5)

# === Step 7: Drop blacklisted food items ===
# blacklist = ["Pav 1pcs"]
# interaction_df = interaction_df[~interaction_df["product_name"].isin(blacklist)]

# === Step 8: Save lean outputs ===
interaction_df.to_pickle("interaction_df.pkl")
interaction_df.to_csv("interaction_df.csv", index=False)

print("✅ Preprocessing done. Saved as interaction_df.pkl and .csv")
print("📊 Final shape:", interaction_df.shape)
