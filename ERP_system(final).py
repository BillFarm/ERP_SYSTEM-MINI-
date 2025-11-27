import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime
import os

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if os.path.exists("users.csv"):
        return pd.read_csv("users.csv")
    return pd.DataFrame(columns=["username","password"])

def save_users(df):
    df.to_csv("users.csv", index=False)

def register_user(username, password):
    users = load_users()
    if username in users["username"].values:
        return False
    new_user = pd.DataFrame([[username, hash_password(password)]], columns=["username","password"])
    users = pd.concat([users, new_user], ignore_index=True)
    save_users(users)
    return True

def login_user(username, password):
    users = load_users()
    if username in users["username"].values:
        return users.loc[users["username"]==username, "password"].values[0] == hash_password(password)
    return False

def user_filename(username):
    return f"erp_{username}.csv"

def load_user_data(username):
    fn = user_filename(username)
    if os.path.exists(fn):
        df = pd.read_csv(fn)
        if "Cost" in df.columns:
            df = df.rename(columns={"Cost":"Cost per Unit"})
        return df
    return pd.DataFrame(columns=["Date","Product","Quantity","Price","Cost per Unit","Total Cost","Total Sales","Profit"])

def save_user_data(username, df):
    df.to_csv(user_filename(username), index=False)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "data" not in st.session_state:
    st.session_state.data = None

if not st.session_state.logged_in:
    st.title("Mini ERP App - Login / Register")
    action = st.selectbox("Action", ["Login","Register"])
    with st.form(key="auth_form"):
        if action == "Register":
            new_user = st.text_input("New username")
            new_pass = st.text_input("New password", type="password")
            submitted = st.form_submit_button("Create account")
            if submitted and new_user and new_pass:
                if register_user(new_user, new_pass):
                    st.success("User created. Please log in.")
                else:
                    st.error("Username already exists.")
        else:
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted and username and password:
                if login_user(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.data = load_user_data(username)
                else:
                    st.error("Invalid credentials")
    st.stop()

st.title(f"Mini ERP App - {st.session_state.username}")
data = st.session_state.data if st.session_state.data is not None else load_user_data(st.session_state.username)

menu = ["Add Sale","View Data","Save Data","Load Data","Sales Chart","Logout"]
choice = st.selectbox("Choose an option", menu)

if choice == "Logout":
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.data = None
    st.experimental_rerun()

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
        new_row = pd.DataFrame([{
            "Date": date,
            "Product": product,
            "Quantity": quantity,
            "Price": price,
            "Cost per Unit": cost_per_unit,
            "Total Cost": total_cost,
            "Total Sales": total_sales,
            "Profit": profit
        }])
        data = pd.concat([data, new_row], ignore_index=True)
        st.session_state.data = data
        save_user_data(st.session_state.username, data)
        st.success(f"Sale added: {product}")

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
                st.session_state.data = data
                save_user_data(st.session_state.username, data)
                st.success("Row updated successfully!")
        if st.checkbox("Delete selected row"):
            if st.button("Delete Row"):
                data = data.drop(row_index).reset_index(drop=True)
                st.session_state.data = data
                save_user_data(st.session_state.username, data)
                st.success("Row deleted successfully!")

elif choice == "Save Data":
    save_user_data(st.session_state.username, data)
    st.success("Data saved successfully!")

elif choice == "Load Data":
    st.session_state.data = load_user_data(st.session_state.username)
    st.success("Data loaded successfully!")

elif choice == "Sales Chart":
    st.header("Total Sales per Product")
    if data.empty:
        st.write("No data to display!")
    else:
        chart_data = data.groupby("Product")["Total Sales"].sum().reset_index()
        st.bar_chart(chart_data.set_index("Product"))
