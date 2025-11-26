import streamlit as st
import pandas as pd
from datetime import datetime

try:
    data = pd.read_csv("erp_data.csv")
    if "Cost" in data.columns:
        data = data.rename(columns={"Cost": "Cost per Unit"})
except:
    data = pd.DataFrame(columns=[
        "Date", "Product", "Quantity", "Price",
        "Cost per Unit", "Total Cost", "Total Sales", "Profit"
    ])

st.title("Mini ERP App")

menu = ["Add Sale", "View Data", "Save Data", "Load Data", "Sales Chart"]
choice = st.sidebar.selectbox("Choose an option", menu)

if choice == "Add Sale":
    st.header("Add a Sale")
    product = st.text_input("Product:")
    quantity = st.number_input("Quantity:", min_value=1, value=1)
    price = st.number_input("Price:", min_value=0.0, value=0.0, step=0.01)
    cost_per_unit = st.number_input("Cost per Unit:", min_value=0.0, value=0.0, step=0.01)

    if st.button("Add Sale"):
        total_sales = quantity * price
        total_cost = quantity * cost_per_unit
        profit = total_sales - total_cost
        date = datetime.now().strftime("%Y-%m-%d")

        new_row = {
            "Date": date,
            "Product": product,
            "Quantity": quantity,
            "Price": price,
            "Cost per Unit": cost_per_unit,
            "Total Cost": total_cost,
            "Total Sales": total_sales,
            "Profit": profit
        }

        new_row_df = pd.DataFrame([new_row], columns=data.columns)
        data = pd.concat([data, new_row_df], ignore_index=True)
        data.to_csv("erp_data.csv", index=False)
        st.success(f"Sale added successfully: {product}")

elif choice == "View Data":
    st.header("Sales Data")
    if data.empty:
        st.write("No data yet!")
    else:
        st.dataframe(data)
        row_index = st.number_input("Select row index to edit/delete:", min_value=0, max_value=len(data)-1, step=1)

        if st.checkbox("Edit selected row"):
            row = data.loc[row_index]
            new_product = st.text_input("Product:", value=row["Product"])
            new_quantity = st.number_input("Quantity:", min_value=1, value=int(row["Quantity"]))
            new_price = st.number_input("Price:", min_value=0.0, value=float(row["Price"]), step=0.01)
            new_cost = st.number_input("Cost per Unit:", min_value=0.0, value=float(row["Cost per Unit"]), step=0.01)

            if st.button("Update Row"):
                data.at[row_index, "Product"] = new_product
                data.at[row_index, "Quantity"] = new_quantity
                data.at[row_index, "Price"] = new_price
                data.at[row_index, "Cost per Unit"] = new_cost
                data.at[row_index, "Total Sales"] = new_quantity * new_price
                data.at[row_index, "Total Cost"] = new_quantity * new_cost
                data.at[row_index, "Profit"] = data.at[row_index, "Total Sales"] - data.at[row_index, "Total Cost"]
                data.to_csv("erp_data.csv", index=False)
                st.success("Row updated successfully!")

        if st.checkbox("Delete selected row"):
            if st.button("Delete Row"):
                data = data.drop(row_index).reset_index(drop=True)
                data.to_csv("erp_data.csv", index=False)
                st.success("Row deleted successfully!")

elif choice == "Save Data":
    data.to_csv("erp_data.csv", index=False)
    st.success("Data saved successfully!")

elif choice == "Load Data":
    try:
        data = pd.read_csv("erp_data.csv")
        if "Cost" in data.columns:
            data = data.rename(columns={"Cost": "Cost per Unit"})
        st.success("Data loaded successfully!")
    except:
        st.error("Can't load file!")

elif choice == "Sales Chart":
    st.header("Total Sales per Product")
    if data.empty:
        st.write("No data to display!")
    else:
        chart_data = data.groupby("Product")["Total Sales"].sum().reset_index()
        st.bar_chart(chart_data.set_index("Product"))
