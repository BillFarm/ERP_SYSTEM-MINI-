import streamlit as st
import pandas as pd
from datetime import datetime

# Προσπάθεια ανάγνωσης αρχείου CSV, αν δεν υπάρχει δημιουργείται κενό DataFrame
try:
    data = pd.read_csv("erp_data.csv")
except:
    data = pd.DataFrame(columns=[
        "Date", "Product", "Quantity", "Price", "Cost", "Total Sales", "Profit"
    ])

st.title("Mini ERP App")

# Μενού επιλογών
menu = ["Add Sale", "View Data", "Save Data", "Load Data"]
choice = st.sidebar.selectbox("Choose an option", menu)

if choice == "Add Sale":
    st.header("Add a Sale")
    product = st.text_input("Product:")
    quantity = st.number_input("Quantity:", min_value=1, value=1)
    price = st.number_input("Price:", min_value=0.0, value=0.0, step=0.01)
    cost = st.number_input("Cost:", min_value=0.0, value=0.0, step=0.01)

    if st.button("Add Sale"):
        total = quantity * price
        profit = total - cost
        date = datetime.now().strftime("%Y-%m-%d")

        new_row = {
            "Date": date,
            "Product": product,
            "Quantity": quantity,
            "Price": price,
            "Cost": cost,
            "Total Sales": total,
            "Profit": profit
        }

        new_row_df = pd.DataFrame([new_row], columns=data.columns)
        data = pd.concat([data, new_row_df], ignore_index=True)
        st.success(f"Sale added successfully: {product}")
        data.to_csv("erp_data.csv", index=False)

elif choice == "View Data":
    st.header("Sales Data")
    if data.empty:
        st.write("No data yet!")
    else:
        st.dataframe(data)

elif choice == "Save Data":
    data.to_csv("erp_data.csv", index=False)
    st.success("Data saved successfully!")

elif choice == "Load Data":
    try:
        data = pd.read_csv("erp_data.csv")
        st.success("Data loaded successfully!")
    except:
        st.error("Can't load file!")
