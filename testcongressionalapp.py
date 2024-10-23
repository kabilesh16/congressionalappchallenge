import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Initialize session state for monthly data if it doesn't exist
if 'monthly_data' not in st.session_state:
    st.session_state['monthly_data'] = {}

if 'transactions' not in st.session_state:
    st.session_state['transactions'] = []

st.title("💰 Budget Buddy 💰")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Go to", ["Home", "Monthly Analytics", "Investment Planner", "Financial Reports"])

# Home Page (Default)
if page == "Home":
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

# Monthly Analytics Page
elif page == "Monthly Analytics":
    st.subheader("Monthly Analytics")

    # Function to generate analytics
    def generate_analytics():
        months = []
        incomes = []
        expenses = []

        for month_year, data in st.session_state['monthly_data'].items():
            months.append(month_year)
            incomes.append(data['Income'])
            total_expenses = data['Fixed Expenses'] + sum(data['Spending'].values())
            expenses.append(total_expenses)

        return months, incomes, expenses

    # Generate and plot the bar graph for income and expenses
    if st.session_state['monthly_data']:
        months, incomes, expenses = generate_analytics()

        fig, ax = plt.subplots()
        bar_width = 0.35
        index = range(len(months))

        bar1 = ax.bar(index, incomes, bar_width, label='Income')
        bar2 = ax.bar([i + bar_width for i in index], expenses, bar_width, label='Expenses')

        ax.set_xlabel('Month-Year')
        ax.set_ylabel('Amount')
        ax.set_title('Monthly Income and Expenses')
        ax.set_xticks([i + bar_width / 2 for i in index])
        ax.set_xticklabels(months)
        ax.legend()

        st.pyplot(fig)
    else:
        st.write("No data available to display.")

# Investment Planner Page
elif page == "Investment Planner":
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

# Financial Reports Page
elif page == "Financial Reports":
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
    sender_email = st.text_input("Your Email", value="johndoe@gmail.com")
    sender_password = st.text_input("Your Email Password", type='password')
    recipient_email = st.text_input("Recipient's Email", value="johndoe@gmail.com")
    subject = st.text_input("Email Subject", value="Financial Report")

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
