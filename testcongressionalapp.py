import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Initialize session state for monthly data if it doesn't exist
if 'monthly_data' not in st.session_state:
    st.session_state['monthly_data'] = {}

st.title("🌟 Personal Finance Manager 🌟")

# Month and Year Selection
st.subheader("Monthly Financial Overview")
selected_month = st.selectbox("Select Month", [f"{i:02d}" for i in range(1, 13)])
selected_year = st.number_input("Select Year", min_value=2000, max_value=2100, value=datetime.now().year)

# Input for current funds
current_funds = st.number_input("Current Funds", min_value=0.0, step=100.0, format="%.2f")

# Input for income
income = st.number_input("Expected Income for the Month", min_value=0.0, step=100.0, format="%.2f")

# Input for fixed expenses
fixed_expenses = st.number_input("Total Fixed Expenses", min_value=0.0, step=100.0, format="%.2f")

# Input for discretionary spending categories
eating_out_budget = st.number_input("Budget for Eating Out", min_value=0.0, step=10.0, format="%.2f")
entertainment_budget = st.number_input("Budget for Entertainment", min_value=0.0, step=10.0, format="%.2f")

if st.button("Submit Monthly Overview"):
    # Store monthly data
    month_year_key = f"{selected_year}-{selected_month}"
    st.session_state['monthly_data'][month_year_key] = {
        "Current Funds": current_funds,
        "Income": income,
        "Fixed Expenses": fixed_expenses,
        "Eating Out Budget": eating_out_budget,
        "Entertainment Budget": entertainment_budget,
        "Spending": {"Eating Out": 0.0, "Entertainment": 0.0},
    }
    st.success(f"Monthly Overview for {month_year_key} saved!")

# Expense Tracking Section
st.subheader("Track Your Spending")

# Input for expense category
category = st.selectbox("Expense Category", ["Eating Out", "Entertainment", "Other"])
amount_spent = st.number_input("Amount Spent", min_value=0.0, step=0.01)

if st.button("Add Expense"):
    # Update spending based on category
    month_year_key = f"{selected_year}-{selected_month}"
    if month_year_key in st.session_state['monthly_data']:
        st.session_state['monthly_data'][month_year_key]["Spending"][category] += amount_spent
        st.success(f"Added ${amount_spent:.2f} to {category}.")
        
        # Check for budget overages
        if category == "Eating Out" and st.session_state['monthly_data'][month_year_key]["Spending"][category] > eating_out_budget:
            st.warning(f"Alert: You have exceeded your eating out budget by ${st.session_state['monthly_data'][month_year_key]['Spending'][category] - eating_out_budget:.2f}!")
        elif category == "Entertainment" and st.session_state['monthly_data'][month_year_key]["Spending"][category] > entertainment_budget:
            st.warning(f"Alert: You have exceeded your entertainment budget by ${st.session_state['monthly_data'][month_year_key]['Spending'][category] - entertainment_budget:.2f}!")

# Analytics Section
st.subheader("Monthly Analytics")

# Function to generate analytics
def generate_analytics(current_month_key):
    previous_month = (datetime.strptime(current_month_key, "%Y-%m") - pd.DateOffset(months=1)).strftime("%Y-%m")
    
    if previous_month in st.session_state['monthly_data']:
        current_spending = st.session_state['monthly_data'][current_month_key]["Spending"]
        previous_spending = st.session_state['monthly_data'][previous_month]["Spending"]

        for category in current_spending.keys():
            current_amount = current_spending[category]
            previous_amount = previous_spending[category]
            if current_amount > previous_amount:
                st.warning(f"In {current_month_key}, you are spending **more** on {category} by ${current_amount - previous_amount:.2f}.")
            elif current_amount < previous_amount:
                st.success(f"In {current_month_key}, you are spending **less** on {category} by ${previous_amount - current_amount:.2f}.")
            else:
                st.info(f"Your spending on {category} is **the same** as last month.")

if st.button("Analyze Current Month"):
    current_month_key = f"{selected_year}-{selected_month}"
    generate_analytics(current_month_key)

# Display Monthly Data
st.subheader("Monthly Data Overview")
if st.session_state['monthly_data']:
    df_monthly_data = pd.DataFrame.from_dict(st.session_state['monthly_data'], orient='index')
    st.dataframe(df_monthly_data)
else:
    st.write("No monthly data available.")

# Pie Chart for Expense Breakdown
st.subheader("Expense Breakdown")
# Define current_month_key for pie chart section
current_month_key = f"{selected_year}-{selected_month}"
if 'Spending' in st.session_state['monthly_data'].get(current_month_key, {}):
    spending_data = st.session_state['monthly_data'][current_month_key]["Spending"]
    if sum(spending_data.values()) > 0:
        fig, ax = plt.subplots()
        ax.pie(spending_data.values(), labels=spending_data.keys(), autopct='%1.1f%%', startangle=90)
        ax.axis("equal")
        st.pyplot(fig)
    else:
        st.write("No spending data available for this month.")

# Investment Calculator
st.subheader("Investment Planner")

# User inputs for investment details
target_amount = st.number_input("Target Investment Amount", min_value=0.0, step=100.0, format="%.2f")
initial_investment = st.number_input("Initial Investment Amount", min_value=0.0, step=100.0, format="%.2f")
years_to_invest = st.number_input("Investment Duration (Years)", min_value=1, step=1)

# Calculate annual return required to meet the target
if initial_investment > 0 and target_amount > 0 and years_to_invest > 0:
    required_return = ((target_amount / initial_investment) ** (1 / years_to_invest)) - 1
    required_return_percentage = required_return * 100

    # Discretionary Income Calculation
    discretionary_income = income - fixed_expenses

    # Investment strategy based on required return
    if required_return_percentage < 5:
        strategy = "Conservative"
    elif 5 <= required_return_percentage <= 10:
        strategy = "Moderate"
    else:
        strategy = "Aggressive"

    # Display results
    st.write(f"To reach your target of **${target_amount}** in **{years_to_invest} years**, you need an annual return of **{required_return_percentage:.2f}%**.")
    st.write(f"**Suggested Investment Strategy:** {strategy}")
    st.write(f"Your discretionary income is **${discretionary_income:.2f}**.")

    # Visualization of investment growth
    future_values = [initial_investment * (1 + required_return) ** i for i in range(years_to_invest + 1)]
    st.line_chart(future_values)
else:
    st.write("Please enter valid amounts and duration for investment.")

# Footer
st.write("Created by [Your Name]. All rights reserved.")
