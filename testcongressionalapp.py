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

# Stock Market Tab
# st.subheader("Stock Market Price Tracker")
# api_key = "NXARU2L1OVTKZ8UU"  # Replace with your Alpha Vantage API key
# ticker_symbol = st.text_input("Enter Stock Ticker Symbol (e.g., AAPL for Apple)")

# if st.button("Get Stock Price"):
#     if ticker_symbol:
#         url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker_symbol}&apikey={api_key}"
#         response = requests.get(url)
#         data = response.json()

#         if "Global Quote" in data:
#             stock_data = data["Global Quote"]
#             price = stock_data["05. price"]
#             st.success(f"The current price of {ticker_symbol} is ${price}.")
#         else:
#             st.error("Invalid ticker symbol or API error. Please check the symbol and try again.")
#     else:
#         st.error("Please enter a ticker symbol.")

# Create sidebar for different functionalities
page = st.sidebar.selectbox("Navigation", ["💵 Budget Planner", "📊 Expenses Tracker", "📈 Investment Planner", "📑 Reports", "📚 Resources", "❓ Help"])

# Budget Planner Tab
if page == "💵 Budget Planner":
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
elif page == "📊 Expenses Tracker":
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
elif page == "📈 Investment Planner":
    st.subheader("Investment Planner")

    # User inputs for investment details
    initial_investment = st.number_input("Initial Investment Amount", min_value=0.0, step=100.0, format="%.2f")
    target_amount = st.number_input("Target Investment Amount", min_value=0.0, step=100.0, format="%.2f")
    years_to_invest = st.number_input("Investment Duration (Years)", min_value=1, step=1)

    # Predefined stock categories
    conservative_stocks = ["JNJ (Johnson & Johnson)", "KO (Coca-Cola)", "PG (Procter & Gamble)", "PFE (Pfizer)", "MCD (McDonald's)"]
    moderate_stocks = ["AAPL (Apple)", "MSFT (Microsoft)", "GOOGL (Google)", "V (Visa)", "NFLX (Netflix)"]
    aggressive_stocks = ["TSLA (Tesla)", "NVDA (Nvidia)", "AMZN (Amazon)", "AMD (Advanced Micro Devices)", "SQ (Square)"]

    # Calculate annual return required to meet the target
    if initial_investment > 0 and target_amount > 0 and years_to_invest > 0:
        required_return = ((target_amount / initial_investment) ** (1 / years_to_invest)) - 1
        required_return_percentage = required_return * 100

        # Investment strategy based on required return
        if required_return_percentage < 5:
            strategy = "Conservative"
            suggested_stocks = conservative_stocks
        elif 5 <= required_return_percentage <= 10:
            strategy = "Moderate"
            suggested_stocks = moderate_stocks
        else:
            strategy = "Aggressive"
            suggested_stocks = aggressive_stocks

        # Display results
        st.write(f"To reach your target of **${target_amount}** in **{years_to_invest} years**, you need an annual return of **{required_return_percentage:.2f}%**.")
        st.write(f"**Suggested Investment Strategy:** {strategy}")

        # Visualization of investment growth
        future_values = [initial_investment * (1 + required_return) ** i for i in range(years_to_invest + 1)]
        st.line_chart(future_values)

        # Display suggested stocks below the graph
        st.write("### Suggested Stocks:")
        for stock in suggested_stocks:
            st.write(f"- {stock}")
    else:
        st.write("Please enter valid amounts and duration.")


# Savings Goals Tab
# elif page == "Savings Goals":
#     st.subheader("Savings Goals")

#     goal_name = st.text_input("Goal Name")
#     goal_amount = st.number_input("Goal Amount", min_value=0.0, step=100.0, format="%.2f")
#     current_amount = st.number_input("Current Amount Saved", min_value=0.0, step=100.0, format="%.2f")
#     goal_date = st.date_input("Target Date", datetime.now())

#     if st.button("Add Savings Goal"):
#         new_goal = {"Name": goal_name, "Target Amount": goal_amount, "Current Amount": current_amount, "Target Date": goal_date}
#         st.session_state["savings_goals"].append(new_goal)
#         st.success("Savings goal added!")

#     # Display savings goals
#     st.markdown("### Your Savings Goals")
#     if st.session_state["savings_goals"]:
#         df_goals = pd.DataFrame(st.session_state["savings_goals"])
#         st.dataframe(df_goals)

#         # Show progress bars
#         for goal in st.session_state['savings_goals']:
#             progress = (goal['Current Amount'] / goal['Target Amount']) * 100 if goal['Target Amount'] > 0 else 0
#             st.progress(progress)

#     else:
#         st.write("No savings goals yet.")

# Debt Tracker Tab
# elif page == "Debt Tracker":
#     st.subheader("Debt Tracker")

#     debt_name = st.text_input("Debt Name")
#     debt_amount = st.number_input("Total Debt Amount", min_value=0.0, step=100.0, format="%.2f")
#     monthly_payment = st.number_input("Monthly Payment", min_value=0.0, step=50.0, format="%.2f")

#     if st.button("Add Debt"):
#         new_debt = {"Name": debt_name, "Total Amount": debt_amount, "Monthly Payment": monthly_payment}
#         st.session_state["debts"].append(new_debt)
#         st.success("Debt added!")

#     # Display debts
#     st.markdown("### Your Debts")
#     if st.session_state["debts"]:
#         df_debts = pd.DataFrame(st.session_state["debts"])
#         st.dataframe(df_debts)
#     else:
#         st.write("No debts yet.")

# Reports Tab

elif page == "📑 Reports":
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
elif page == "📚 Resources":
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

elif page == "❓ Help":
    st.title("🔍 Help - Explore Financial Topics")
    st.write("Welcome to the financial help page! Enter a financial topic below to find definitions, articles, resources, and videos.")

    # Text input for the user to enter their search query
    query = st.text_input("Search for a financial topic...", placeholder="e.g., stock market, cryptocurrency")

    # Button to trigger the search
    if st.button("Search"):
        if query:
            # Call the Wikipedia API to fetch definitions and articles
            search_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={query}&limit=10&namespace=0&format=json"
            response = requests.get(search_url)

            if response.status_code == 200:
                data = response.json()

                # Extract results
                titles = data[1]  # Titles of the search results
                descriptions = data[2]  # Descriptions
                urls = data[3]  # URLs to the articles

                if titles:
                    st.header("📝 Search Results")
                    for title, description, url in zip(titles, descriptions, urls):
                        # Create a card-like layout for each result
                        with st.container():
                            st.markdown(f"### {title}", unsafe_allow_html=True)
                            st.write(description)  # Plain description without italics
                            st.markdown(f"[Read more]({url})", unsafe_allow_html=True)

                            # Add an image related to the topic if available
                            img_search_url = f"https://en.wikipedia.org/w/api.php?action=query&titles={title}&prop=pageimages&format=json"
                            img_response = requests.get(img_search_url)
                            if img_response.status_code == 200:
                                img_data = img_response.json()
                                page_id = next(iter(img_data['query']['pages']))
                                if 'thumbnail' in img_data['query']['pages'][page_id]:
                                    img_url = img_data['query']['pages'][page_id]['thumbnail']['source']
                                    # Add image with a black outline using HTML
                                    st.markdown(
                                        f'<div style="border: 2px solid black; display: inline-block; padding: 5px;">'
                                        f'<img src="{img_url}" width="150" /></div>',
                                        unsafe_allow_html=True
                                    )

                            # Add a separator line for better organization
                            st.markdown("---")  # Horizontal line for separation

                    # Call YouTube API for related videos
                    st.header("🎥 Related YouTube Videos")
                    youtube_api_key = 'AIzaSyAeroON9fDsu6_vZeskqV6fs0N_HXkDJ0s'  # Your YouTube API key
                    youtube_search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&key={youtube_api_key}&maxResults=5&type=video"
                    youtube_response = requests.get(youtube_search_url)

                    if youtube_response.status_code == 200:
                        youtube_data = youtube_response.json()
                        video_items = youtube_data.get('items', [])
                        if video_items:
                            for item in video_items:
                                video_title = item['snippet']['title']
                                video_id = item['id']['videoId']
                                video_url = f"https://www.youtube.com/watch?v={video_id}"
                                st.markdown(f"**{video_title}**  \n[Watch Video]({video_url})", unsafe_allow_html=True)
                        else:
                            st.write("🚫 No related videos found.")
                    else:
                        st.error("⚠️ Error fetching data from YouTube API.")

                else:
                    st.write("🚫 No results found for your query.")
            else:
                st.error("⚠️ Error fetching data from Wikipedia API.")
        else:
            st.warning("⚠️ Please enter a topic to search.")

    # Suggested topics section
    st.sidebar.header("Suggested Topics")
    suggested_topics = ["Stock Market", "Cryptocurrency", "Inflation", "Interest Rates", "Investment Strategies"]

    # Placeholder to store selected topic
    selected_topic = st.sidebar.radio("Select a topic:", suggested_topics)

    # Update the text input with the selected topic
    if selected_topic:
        st.session_state.query = selected_topic  # Store the selected topic in session state
        query = st.session_state.query  # Update the query variable

        # Trigger the search automatically
        if st.button("Search Topic"):
            if query:
                # Call the Wikipedia API to fetch definitions and articles
                search_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={query}&limit=10&namespace=0&format=json"
                response = requests.get(search_url)

                if response.status_code == 200:
                    data = response.json()

                    # Extract results
                    titles = data[1]  # Titles of the search results
                    descriptions = data[2]  # Descriptions
                    urls = data[3]  # URLs to the articles

                    if titles:
                        st.header("📝 Search Results")
                        for title, description, url in zip(titles, descriptions, urls):
                            # Create a card-like layout for each result
                            with st.container():
                                st.markdown(f"### {title}", unsafe_allow_html=True)
                                st.write(description)  # Plain description without italics
                                st.markdown(f"[Read more]({url})", unsafe_allow_html=True)

                                # Add an image related to the topic if available
                                img_search_url = f"https://en.wikipedia.org/w/api.php?action=query&titles={title}&prop=pageimages&format=json"
                                img_response = requests.get(img_search_url)
                                if img_response.status_code == 200:
                                    img_data = img_response.json()
                                    page_id = next(iter(img_data['query']['pages']))
                                    if 'thumbnail' in img_data['query']['pages'][page_id]:
                                        img_url = img_data['query']['pages'][page_id]['thumbnail']['source']
                                        # Add image with a black outline using HTML
                                        st.markdown(
                                            f'<div style="border: 2px solid black; display: inline-block; padding: 5px;">'
                                            f'<img src="{img_url}" width="150" /></div>',
                                            unsafe_allow_html=True
                                        )

                                st.markdown("---")  # Horizontal line for separation

                        # Call YouTube API for related videos
                        st.header("🎥 Related YouTube Videos")
                        youtube_api_key = 'AIzaSyAeroON9fDsu6_vZeskqV6fs0N_HXkDJ0s'  # Your YouTube API key
                        youtube_search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&key={youtube_api_key}&maxResults=5&type=video"
                        youtube_response = requests.get(youtube_search_url)

                        if youtube_response.status_code == 200:
                            youtube_data = youtube_response.json()
                            video_items = youtube_data.get('items', [])
                            if video_items:
                                for item in video_items:
                                    video_title = item['snippet']['title']
                                    video_id = item['id']['videoId']
                                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                                    st.markdown(f"**{video_title}**  \n[Watch Video]({video_url})", unsafe_allow_html=True)
                            else:
                                st.write("🚫 No related videos found.")
                        else:
                            st.error("⚠️ Error fetching data from YouTube API.")

                    else:
                        st.write("🚫 No results found for your query.")
                else:
                    st.error("⚠️ Error fetching data from Wikipedia API.")
            else:
                st.warning("⚠️ Please enter a topic to search.")


