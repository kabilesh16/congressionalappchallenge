#change to test branching in git

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Initialize the session state
if 'transactions' not in st.session_state:
    st.session_state['transactions'] = []
if 'savings_goals' not in st.session_state:
    st.session_state['savings_goals'] = []
if 'debts' not in st.session_state:
    st.session_state['debts'] = []

st.title("🌟 Personal Finance Manager 🌟")

# Create tabs for different functionalities
tabs = st.tabs(["Budget Planner", "Expenses Tracker", "Investment Planner", "Savings Goals", "Debt Tracker", "Reports", "Resources"])

# Budget Planner Tab
with tabs[0]:
    st.subheader("Budget Planner")

    # Income input
    st.markdown("### Enter Your Income")
    salary = st.number_input("Monthly Salary", min_value=0.0, step=100.0, format="%.2f")
    pay_frequency = st.selectbox("Payment Frequency", ["Monthly", "Bi-Weekly", "Weekly", "Annually"])

    # Fixed expenses input
    st.markdown("### Enter Your Fixed Expenses")
    rent = st.number_input("Rent/Mortgage", min_value=0.0, step=50.0, format="%.2f")
    utilities = st.number_input("Utilities", min_value=0.0, step=10.0, format="%.2f")
    groceries = st.number_input("Groceries", min_value=0.0, step=10.0, format="%.2f")
    other_fixed = st.number_input("Other Fixed Expenses", min_value=0.0, step=10.0, format="%.2f")

    # Calculate monthly income
    if pay_frequency == "Weekly":
        monthly_income = salary * 4
    elif pay_frequency == "Bi-Weekly":
        monthly_income = salary * 2
    elif pay_frequency == "Monthly":
        monthly_income = salary
    elif pay_frequency == "Annually":
        monthly_income = salary / 12

    # Calculate total fixed expenses and discretionary income
    total_fixed_expenses = rent + utilities + groceries + other_fixed
    discretionary_income = monthly_income - total_fixed_expenses

    # Display Budget Summary
    st.markdown("### Budget Summary")
    st.write(f"**Your Monthly Income:** ${monthly_income:.2f}")
    st.write(f"**Total Fixed Expenses:** ${total_fixed_expenses:.2f}")
    st.write(f"**Discretionary Income:** ${discretionary_income:.2f}")

    # Pie chart for budget visualization
    if total_fixed_expenses > 0 or discretionary_income > 0:
        budget_data = {"Fixed Expenses": total_fixed_expenses, "Discretionary Income": discretionary_income}
        fig, ax = plt.subplots()
        ax.pie(budget_data.values(), labels=budget_data.keys(), autopct='%1.1f%%', startangle=90)
        ax.axis("equal")
        st.pyplot(fig)
    else:
        st.write("Please enter valid income and expense amounts to visualize the budget.")

# Expenses Tracker Tab
with tabs[1]:
    st.subheader("Expenses Tracker")

    # Function to add transactions
    def add_transaction(date, category, amount, type):
        return {"Date": date, "Category": category, "Amount": amount, "Type": type}

    # Sidebar for adding transactions
    st.sidebar.header("Add Transaction")
    date = st.sidebar.date_input("Transaction Date", datetime.now())
    category = st.sidebar.selectbox("Category", ["Food", "Rent", "Utilities", "Entertainment", "Other"])
    amount = st.sidebar.number_input("Amount", min_value=0.0, step=0.01)
    transaction_type = st.sidebar.radio("Transaction Type", ["Income", "Expense"])

    if st.sidebar.button("Add Transaction"):
        new_transaction = add_transaction(date, category, amount, transaction_type)
        st.session_state["transactions"].append(new_transaction)
        st.sidebar.success("Transaction added!")

    # Display transactions
    st.markdown("### Transaction History")
    if st.session_state["transactions"]:
        df = pd.DataFrame(st.session_state["transactions"])
        st.dataframe(df)
    else:
        st.write("No transactions yet.")

# Investment Planner Tab
with tabs[2]:
    st.subheader("Investment Planner")

    # User inputs for investment details
    initial_investment = st.number_input("Initial Investment Amount", min_value=0.0, step=100.0, format="%.2f")
    target_amount = st.number_input("Target Investment Amount", min_value=0.0, step=100.0, format="%.2f")
    years_to_invest = st.number_input("Investment Duration (Years)", min_value=1, step=1)

    # Calculate annual return required to meet the target
    if initial_investment > 0 and target_amount > 0 and years_to_invest > 0:
        required_return = ((target_amount / initial_investment) ** (1 / years_to_invest)) - 1
        required_return_percentage = required_return * 100

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

        # Visualization of investment growth
        future_values = [initial_investment * (1 + required_return) ** i for i in range(years_to_invest + 1)]
        st.line_chart(future_values)
    else:
        st.write("Please enter valid amounts and duration.")

# Savings Goals Tab
with tabs[3]:
    st.subheader("Savings Goals")

    goal_name = st.text_input("Goal Name")
    goal_amount = st.number_input("Goal Amount", min_value=0.0, step=100.0, format="%.2f")
    current_amount = st.number_input("Current Amount Saved", min_value=0.0, step=100.0, format="%.2f")
    goal_date = st.date_input("Target Date", datetime.now())

    if st.button("Add Savings Goal"):
        new_goal = {"Name": goal_name, "Target Amount": goal_amount, "Current Amount": current_amount, "Target Date": goal_date}
        st.session_state["savings_goals"].append(new_goal)
        st.success("Savings goal added!")

    # Display savings goals
    st.markdown("### Your Savings Goals")
    if st.session_state["savings_goals"]:
        df_goals = pd.DataFrame(st.session_state["savings_goals"])
        st.dataframe(df_goals)
    else:
        st.write("No savings goals yet.")

# Debt Tracker Tab
with tabs[4]:
    st.subheader("Debt Tracker")

    debt_name = st.text_input("Debt Name")
    debt_amount = st.number_input("Total Debt Amount", min_value=0.0, step=100.0, format="%.2f")
    current_debt = st.number_input("Current Debt Amount", min_value=0.0, step=100.0, format="%.2f")

    if st.button("Add Debt"):
        new_debt = {"Name": debt_name, "Total Amount": debt_amount, "Current Amount": current_debt}
        st.session_state["debts"].append(new_debt)
        st.success("Debt added!")

    # Display debts
    st.markdown("### Your Debts")
    if st.session_state["debts"]:
        df_debts = pd.DataFrame(st.session_state["debts"])
        st.dataframe(df_debts)
    else:
        st.write("No debts yet.")

# Reports Tab
with tabs[5]:
    st.subheader("Reports")

    # Monthly Expense Report
    st.write("### Monthly Expense Report")
    if st.session_state["transactions"]:
        expense_df = pd.DataFrame(st.session_state["transactions"])
        expense_summary = expense_df[expense_df['Type'] == 'Expense'].groupby('Category')['Amount'].sum().reset_index()
        st.bar_chart(expense_summary.set_index('Category'))
    else:
        st.write("No expense data to report.")

# Resources Tab
with tabs[6]:
    st.subheader("Resources")
    st.write("### Financial Literacy Resources")
    st.markdown("""
    - [National Endowment for Financial Education](https://www.nefe.org/)
    - [Khan Academy: Personal Finance](https://www.khanacademy.org/college-careers-more/personal-finance)
    - [Mint: Budgeting Tips](https://mint.intuit.com/)
    """)

# Footer
st.write("Created by [Your Name]. All rights reserved.")
