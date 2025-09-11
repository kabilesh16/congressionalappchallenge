#link to yt video: https://www.youtube.com/watch?v=Wf6KHBkxePY
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import requests
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Initialize session state
for key in ["transactions", "savings_goals", "debts"]:
    if key not in st.session_state:
        st.session_state[key] = []

# Helper functions
def calculate_monthly_income(salary, frequency):
    return {"Weekly": salary * 4, "Bi-Weekly": salary * 2,
            "Monthly": salary, "Annually": salary / 12}.get(frequency, salary)

def plot_pie_chart(data, labels):
    fig, ax = plt.subplots()
    ax.pie(data, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    st.pyplot(fig)

def send_email(subject, body, recipient_email, sender_email, sender_password):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        return str(e)

def add_transaction(date, category, amount, type_):
    st.session_state["transactions"].append({
        "Date": date,
        "Category": category,
        "Amount": amount,
        "Type": type_
    })


# App Title and Navigation
st.title("💰 Budg3t Buddy 💰")
page = st.sidebar.selectbox("Navigation", ["Budget Planner", "Expenses Tracker", "Investment Planner", "Reports", "Resources"])

# Budget Planner
if page == "Budget Planner":
    st.subheader("Budget Planner")

    # Income
    st.markdown("### Enter Your Income")
    salary = st.number_input("Monthly Salary", min_value=0.0, step=100.0, format="%.2f")
    pay_frequency = st.selectbox("Payment Frequency", ["Monthly", "Bi-Weekly", "Weekly", "Annually"])
    monthly_income = calculate_monthly_income(salary, pay_frequency)

    # Fixed Expenses
    st.markdown("### Enter Your Fixed Expenses")
    rent = st.number_input("Rent/Mortgage", min_value=0.0, step=50.0, format="%.2f")
    utilities = st.number_input("Utilities", min_value=0.0, step=10.0, format="%.2f")
    groceries = st.number_input("Groceries", min_value=0.0, step=10.0, format="%.2f")
    other_fixed = st.number_input("Other Fixed Expenses", min_value=0.0, step=10.0, format="%.2f")

    total_fixed_expenses = rent + utilities + groceries + other_fixed
    discretionary_income = monthly_income - total_fixed_expenses

    # Display summary
    st.markdown("### Budget Summary")
    st.write(f"**Monthly Income:** ${monthly_income:.2f}")
    st.write(f"**Total Fixed Expenses:** ${total_fixed_expenses:.2f}")
    st.write(f"**Discretionary Income:** ${discretionary_income:.2f}")

    # Pie Chart
    if total_fixed_expenses > 0 or discretionary_income > 0:
        plot_pie_chart([total_fixed_expenses, discretionary_income], ["Fixed Expenses", "Discretionary Income"])
    else:
        st.write("Please enter valid income and expenses to visualize the budget.")

# Expenses Tracker
elif page == "Expenses Tracker":
    st.subheader("Expenses Tracker")

    st.sidebar.header("Add Transaction")
    date = st.sidebar.date_input("Transaction Date", datetime.now())
    category = st.sidebar.selectbox("Category", ["Food", "Rent", "Utilities", "Entertainment", "Other"])
    amount = st.sidebar.number_input("Amount", min_value=0.0, step=0.01)
    transaction_type = st.sidebar.radio("Transaction Type", ["Income", "Expense"])

    if st.sidebar.button("Add Transaction"):
        add_transaction(date, category, amount, transaction_type)
        st.sidebar.success("Transaction added!")

    st.markdown("### Transaction History")
    if st.session_state["transactions"]:
        df = pd.DataFrame(st.session_state["transactions"])
        st.dataframe(df)
    else:
        st.write("No transactions yet.")

# Investment Planner
elif page == "Investment Planner":
    st.subheader("Investment Planner")

    initial_investment = st.number_input("Initial Investment Amount", min_value=0.0, step=100.0, format="%.2f")
    target_amount = st.number_input("Target Investment Amount", min_value=0.0, step=100.0, format="%.2f")
    years_to_invest = st.number_input("Investment Duration (Years)", min_value=1, step=1)

    if initial_investment > 0 and target_amount > 0 and years_to_invest > 0:
        required_return = ((target_amount / initial_investment) ** (1 / years_to_invest)) - 1
        required_return_pct = required_return * 100
        strategy = ("Conservative" if required_return_pct < 5 else
                    "Moderate" if required_return_pct <= 10 else "Aggressive")
        st.write(f"To reach **${target_amount}** in **{years_to_invest} years**, you need an annual return of **{required_return_pct:.2f}%**.")
        st.write(f"**Suggested Investment Strategy:** {strategy}")

        future_values = [initial_investment * (1 + required_return) ** i for i in range(years_to_invest + 1)]
        st.line_chart(future_values)
    else:
        st.write("Please enter valid amounts and duration.")


# Reports
elif page == "Reports":
    st.subheader("Financial Reports")

    if st.session_state.get('transactions'):
        df = pd.DataFrame(st.session_state["transactions"])

        df['Date'] = pd.to_datetime(df['Date'])
        df['Month'] = df['Date'].dt.to_period('M')

        total_income = df[df['Type'] == "Income"]['Amount'].sum()
        total_expense = df[df['Type'] == "Expense"]['Amount'].sum()
        st.write(f"**Total Income:** ${total_income:.2f}")
        st.write(f"**Total Expenses:** ${total_expense:.2f}")
        st.write(f"**Net Savings:** ${total_income - total_expense:.2f}")

        monthly_summary = df.groupby(['Month', 'Type'])['Amount'].sum().unstack(fill_value=0)
        st.markdown("### Monthly Income vs Expenses")
        st.bar_chart(monthly_summary)

        # Prepare email body
        report_body = f"**Total Income:** ${total_income:.2f}\n**Total Expenses:** ${total_expense:.2f}\n**Net Savings:** ${total_income - total_expense:.2f}\n\n"
        for month, row in monthly_summary.iterrows():
            report_body += f"{month}: Income=${row.get('Income',0):.2f}, Expense=${row.get('Expense',0):.2f}\n"

        # Email section
        st.markdown("### Send Financial Report via Email")
        sender_email = st.text_input("Your Email", placeholder="sender@example.com")
        sender_password = st.text_input("Your Email Password", type='password')
        recipient_email = st.text_input("Recipient's Email", placeholder="recipient@example.com")
        subject = st.text_input("Email Subject", placeholder="Financial Report")

        if st.button("Send Email"):
            if sender_email and sender_password and recipient_email and subject:
                result = send_email(subject, report_body, recipient_email, sender_email, sender_password)
                st.success("Email sent successfully!" if result is True else f"Failed: {result}")
            else:
                st.error("Please fill all fields.")
    else:
        st.write("No transactions recorded yet.")


# Resources
elif page == "Resources":
    st.subheader("Resources")

    resources = {
        "YouTube Videos": [
            {"title": "The Basics of Investing", "url": "https://www.youtube.com/watch?v=3N5jBThA0fE",
             "description": "Introduction to investing in the stock market."},
            {"title": "Understanding Credit Scores", "url": "https://www.youtube.com/watch?v=yO1gQgMy8kE",
             "description": "Learn how credit scores work."},
            {"title": "Budgeting 101", "url": "https://www.youtube.com/watch?v=EovBWe-RDuc",
             "description": "Tips on creating and sticking to a budget."},
        ],
        "Online Courses": [
            {"title": "Financial Literacy Course by Khan Academy", "url": "https://www.khanacademy.org/college-careers-more/personal-finance",
             "description": "Free personal finance course."},
            {"title": "Investing Basics by Coursera", "url": "https://www.coursera.org/learn/investing-basics",
             "description": "Introductory investing course."}
        ]
    }

    for category, items in resources.items():
        st.markdown(f"#### {category}")
        for item in items:
            st.write(f"- [{item['title']}]({item['url']}) - {item['description']}")

    # Finance News
    news_api_key = "e1f0711db9a34f9fb14ee48b09907dd7"
    news_response = requests.get(f"https://newsapi.org/v2/everything?q=finance&apiKey={news_api_key}")
    news_data = news_response.json()
    if news_data.get("status") == "ok":
        st.markdown("### Latest Finance News Articles")
        for article in news_data["articles"]:
            st.subheader(article["title"])
            st.write(article["description"])
            st.write(f"[Read more]({article['url']})")
    else:
        st.error("Failed to fetch news articles.")



