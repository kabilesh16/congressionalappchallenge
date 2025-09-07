import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import plotly.express as px
import requests  # Importing requests for API calls
import base64
import smtplib
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Initialize the session state
if 'transactions' not in st.session_state:
    st.session_state['transactions'] = []
if 'savings_goals' not in st.session_state:
    st.session_state['savings_goals'] = []
if 'debts' not in st.session_state:
    st.session_state['debts'] = []

st.title("💰 Budg3t Buddy 💰")



# Create sidebar for different functionalities
page = st.sidebar.selectbox("Navigation", ["Budget Planner", "Expenses Tracker", "Investment Planner", "Reports", "Resources"])

# Budget Planner Tab
if page == "Budget Planner":
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
elif page == "Expenses Tracker":
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
elif page == "Investment Planner":
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



# Reports Tab

elif page == "Reports":
    st.subheader("Financial Reports")

    # Example report logic (can be expanded)
    if st.session_state.get('transactions'):
        total_income = sum([t['Amount'] for t in st.session_state['transactions'] if t['Type'] == "Income"])
        total_expense = sum([t['Amount'] for t in st.session_state['transactions'] if t['Type'] == "Expense"])
        st.write(f"**Total Income:** ${total_income:.2f}")
        st.write(f"**Total Expenses:** ${total_expense:.2f}")
        st.write(f"**Net Savings:** ${total_income - total_expense:.2f}")

        # Monthly Analysis
        monthly_income_data = {}
        monthly_expense_data = {}

        for transaction in st.session_state['transactions']:
            month = transaction['Date'].strftime("%Y-%m")  # Group by month
            if transaction['Type'] == "Income":
                if month not in monthly_income_data:
                    monthly_income_data[month] = 0
                monthly_income_data[month] += transaction['Amount']
            else:
                if month not in monthly_expense_data:
                    monthly_expense_data[month] = 0
                monthly_expense_data[month] += transaction['Amount']

        # Calculate changes and advice
        income_changes = {}
        expense_changes = {}

        income_months = list(monthly_income_data.keys())
        expense_months = list(monthly_expense_data.keys())

        for i in range(1, len(income_months)):
            current_month = income_months[i]
            previous_month = income_months[i - 1]
            change = monthly_income_data[current_month] - monthly_income_data[previous_month]
            income_changes[current_month] = change

        for i in range(1, len(expense_months)):
            current_month = expense_months[i]
            previous_month = expense_months[i - 1]
            change = monthly_expense_data[current_month] - monthly_expense_data[previous_month]
            expense_changes[current_month] = change

        # Display Income Changes
        st.markdown("### Monthly Income Changes")
        for month, change in income_changes.items():
            direction = "increased" if change > 0 else "decreased"
            advice = "Consider increasing your income streams or reviewing salary expectations." if change < 0 else "Great job on increasing your income!"
            st.write(f"In {month}, your income {direction} by **${abs(change):.2f}**. {advice}")

        # Display Expense Changes
        st.markdown("### Monthly Expense Changes")
        for month, change in expense_changes.items():
            direction = "increased" if change > 0 else "decreased"
            advice = "Review your spending habits in this category to identify areas for reduction." if change > 0 else "Excellent job on reducing your expenses!"
            st.write(f"In {month}, your expenses {direction} by **${abs(change):.2f}**. {advice}")

        # Prepare the email body
        report_body = f"**Total Income:** ${total_income:.2f}\n**Total Expenses:** ${total_expense:.2f}\n**Net Savings:** ${total_income - total_expense:.2f}\n\n"
        report_body += "### Monthly Income Changes\n"
        for month, change in income_changes.items():
            direction = "increased" if change > 0 else "decreased"
            report_body += f"In {month}, your income {direction} by **${abs(change):.2f}**.\n"

        report_body += "### Monthly Expense Changes\n"
        for month, change in expense_changes.items():
            direction = "increased" if change > 0 else "decreased"
            report_body += f"In {month}, your expenses {direction} by **${abs(change):.2f}**.\n"

        # Prepare data for bar graph
        all_months = sorted(set(monthly_income_data.keys()).union(monthly_expense_data.keys()))
        income_values = [monthly_income_data.get(month, 0) for month in all_months]
        expense_values = [monthly_expense_data.get(month, 0) for month in all_months]

        # Create a DataFrame for plotting
        df_report = pd.DataFrame({
            'Month': all_months,
            'Income': income_values,
            'Expense': expense_values
        })

        # Bar graph for monthly income and expenses
        st.markdown("### Monthly Income vs Expenses")
        fig = px.bar(df_report, x='Month', y=['Income', 'Expense'], title='Monthly Income vs Expenses',
                     labels={'value':'Amount', 'Month':'Month'}, barmode='group')
        st.plotly_chart(fig)

    else:
        st.write("No transactions recorded yet.")

    # Function to send email
    def send_email(subject, body, recipient_email, sender_email, sender_password):
        try:
            # Set up the server
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()  # Enable security
            server.login(sender_email, sender_password)  # Login to your email account

            # Create the email
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            # Send the email
            server.send_message(msg)
            server.quit()  # Close the server
            return True
        except Exception as e:
            return str(e)  # Return the error message if any

    # Email Sending Functionality
    st.markdown("### Send Financial Report via Email")
    sender_email = st.text_input("Your Email", placeholder="sender@example.com")
    sender_password = st.text_input("Your Email Password", type='password', placeholder="Enter your email password")
    recipient_email = st.text_input("Recipient's Email", placeholder="recipient@example.com")
    subject = st.text_input("Email Subject", placeholder="Subject of your email")

    if st.button("Send Email"):
        # Check if all fields are filled and if report_body is defined and not empty
        if sender_email and sender_password and recipient_email and subject and 'report_body' in locals() and report_body:
            result = send_email(subject, report_body, recipient_email, sender_email, sender_password)
            if result is True:
                st.success("Email sent successfully!")
            else:
                st.error(f"Failed to send email: {result}")
        else:
            st.error("Please fill out all fields and ensure there is a report to send.")


# Resources Tab
elif page == "Resources":
    st.subheader("Resources")
    st.write("Links to financial literacy resources and tools will be available here.")

    # List of resources (YouTube videos or tutorials)
    resources = {
        "YouTube Videos": [
            {
                "title": "The Basics of Investing",
                "url": "https://www.youtube.com/watch?v=3N5jBThA0fE",
                "description": "A comprehensive introduction to investing in the stock market."
            },
            {
                "title": "Understanding Credit Scores",
                "url": "https://www.youtube.com/watch?v=yO1gQgMy8kE",
                "description": "Learn how credit scores work and how to improve them."
            },
            {
                "title": "Budgeting 101",
                "url": "https://www.youtube.com/watch?v=EovBWe-RDuc",
                "description": "Essential tips on how to create and stick to a budget."
            },
        ],
        "Online Courses": [
            {
                "title": "Financial Literacy Course by Khan Academy",
                "url": "https://www.khanacademy.org/college-careers-more/personal-finance",
                "description": "A free course covering various aspects of personal finance."
            },
            {
                "title": "Investing Basics by Coursera",
                "url": "https://www.coursera.org/learn/investing-basics",
                "description": "An introductory course to investing concepts."
            }
        ]
    }

    # Display resources
    for category, items in resources.items():
        st.markdown(f"#### {category}")
        for item in items:
            st.write(f"- [{item['title']}]({item['url']}) - {item['description']}")

    # Add News API integration
    news_api_key = "e1f0711db9a34f9fb14ee48b09907dd7"  # Your News API key
    news_url = f"https://newsapi.org/v2/everything?q=finance&apiKey={news_api_key}"  # Fetching finance-related news
    news_response = requests.get(news_url)
    news_data = news_response.json()

    if news_data["status"] == "ok":
        st.markdown("### Latest Finance News Articles")
        for article in news_data["articles"]:
            st.subheader(article["title"])
            st.write(article["description"])
            st.write(f"[Read more]({article['url']})")
    else:
        st.error("Failed to fetch news articles.")
