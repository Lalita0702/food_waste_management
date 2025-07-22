
import streamlit as st
import sqlite3
import pandas as pd

# Connect to SQLite DB
conn = sqlite3.connect('food_waste.db')
cursor = conn.cursor()

# Title
st.title("🍱 Local Food Wastage Management System")

# Sidebar menu
menu = ["View Data", "Run Queries", "Add Food", "Update Food", "Delete Food"]
choice = st.sidebar.selectbox("Menu", menu)

# View Tables
if choice == "View Data":
    table = st.selectbox("Select Table", ["providers", "receivers", "food_listings", "claims"])
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    st.dataframe(df)

# SQL Queries
elif choice == "Run Queries":
    query = st.selectbox("Choose a Query", [
        "Providers per City", "Top Provider Type", "Food Types", "Completed vs Pending Claims"
    ])

    if query == "Providers per City":
        df = pd.read_sql_query("SELECT City, COUNT(*) AS Count FROM providers GROUP BY City", conn)
        st.dataframe(df)

    elif query == "Top Provider Type":
        df = pd.read_sql_query("""
        SELECT Provider_Type, SUM(Quantity) AS Total_Quantity 
        FROM food_listings GROUP BY Provider_Type 
        ORDER BY Total_Quantity DESC LIMIT 1
        """, conn)
        st.dataframe(df)

    elif query == "Food Types":
        df = pd.read_sql_query("SELECT Food_Type, COUNT(*) AS Count FROM food_listings GROUP BY Food_Type", conn)
        st.bar_chart(df.set_index('Food_Type'))

    elif query == "Completed vs Pending Claims":
        df = pd.read_sql_query("""
        SELECT Status, COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims) AS Percentage 
        FROM claims GROUP BY Status
        """, conn)
        st.dataframe(df)

# Add Food Entry
elif choice == "Add Food":
    st.subheader("Add New Food Listing")
    food_name = st.text_input("Food Name")
    quantity = st.number_input("Quantity", min_value=1)
    expiry = st.date_input("Expiry Date")
    provider_id = st.number_input("Provider ID", min_value=1)
    provider_type = st.text_input("Provider Type")
    location = st.text_input("Location")
    food_type = st.selectbox("Food Type", ["Vegetarian", "Non-Vegetarian", "Vegan"])
    meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks"])

    if st.button("Add Food"):
        cursor.execute("""
            INSERT INTO food_listings (Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (food_name, quantity, expiry, provider_id, provider_type, location, food_type, meal_type))
        conn.commit()
        st.success("✅ Food item added successfully!")

# Update Food Entry
elif choice == "Update Food":
    st.subheader("Update Food Listing")
    food_id = st.number_input("Enter Food ID to Update", min_value=1)
    new_qty = st.number_input("New Quantity", min_value=1)
    new_expiry = st.date_input("New Expiry Date")

    if st.button("Update"):
        cursor.execute("UPDATE food_listings SET Quantity = ?, Expiry_Date = ? WHERE Food_ID = ?", 
                       (new_qty, new_expiry, food_id))
        conn.commit()
        st.success("✅ Food listing updated successfully!")

# Delete Food Entry
elif choice == "Delete Food":
    st.subheader("Delete Food Entry")
    del_id = st.number_input("Enter Food ID to Delete", min_value=1)

    if st.button("Delete"):
        cursor.execute("DELETE FROM food_listings WHERE Food_ID = ?", (del_id,))
        conn.commit()
        st.success("❌ Food entry deleted.")
