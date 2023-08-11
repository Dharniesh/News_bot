import streamlit as st
from gnews import GNews
import pandas as pd


st.markdown("<div style='text-align: center;'><h1>UK Finance News Aggregator</h1></div>", unsafe_allow_html=True)

# Style for the colored and centered notes
note_style = "<div style='text-align: center; color: #3366ff; font-size: 18px;'>Note: </div>"
note_style += "<div style='text-align: center; color: #3366ff; font-size: 18px;'>1. You can either enter the period or start and end dates.</div>"
note_style += "<div style='text-align: center; color: #3366ff; font-size: 18px;'>2. A greater volume of requests could lead to a temporary IP block.</div>"

# Display the note
st.markdown(note_style, unsafe_allow_html=True)
st.write("\n\n")  # Adding two lines of space

# ... Rest of your code ...

st.write("\n\n")  # Adding two lines of space
st.write("\n\n")  # Adding two lines of space
# Create a two-column layout
col1, col2 = st.columns(2)

# Get user inputs using Streamlit widgets in the first column
with col1:
    period_days = st.text_input("Days Before News Request (Leave blank to skip):")
    
    # Centered and bold "OR" text using HTML styling
    st.markdown("<div style='text-align: center; font-weight: bold;'>OR</div>", unsafe_allow_html=True)
    
    start_date_disabled = False
    end_date_disabled = False
    
    if period_days:
        start_date_disabled = True
        end_date_disabled = True
    
    start_date = st.date_input("Enter start date (Leave blank to skip):", key="start_date", disabled=start_date_disabled, value=None)
    if start_date_disabled:
        start_date = None
    
    end_date = st.date_input("Enter end date *:", key="end_date", disabled=end_date_disabled, value=None)
    if end_date_disabled:
        end_date = None

# Get user inputs using Streamlit widgets in the second column
with col2:
    exclude_websites = st.text_input("Enter websites URL to exclude  (Leave blank to skip):")
    max_results = st.text_input("News Count (default max = 100):")
    
    search_button_clicked = st.button("Search")

# Rest of your code...


# Rest of your code...
if search_button_clicked:
    # Check if period_days contains only numbers
    if period_days and not period_days.isdigit():
        st.warning("Please enter only numeric values for the period.")
        period_days = None

    # Check if start_date is before end_date and not the same day
    if start_date and end_date and start_date >= end_date:
        st.warning("Start date should be before end date and not the same day.")
        start_date = None
        end_date = None

    # Convert the max_results input to an integer, use default if empty
    max_results = int(max_results) if max_results else 100
    period = f"{period_days}d" if period_days else None

    # Convert the start_date and end_date inputs to tuples of integers (YYYY, M, D)
    formatted_start_date = (start_date.year, start_date.month, start_date.day) if start_date else None
    formatted_end_date = (end_date.year, end_date.month, end_date.day) if end_date else None

    # Create parameters dictionary
    parameters = {
        "language": "en",
        "country": "GB",
        "max_results": max_results,
        "period": period,
        "start_date": formatted_start_date,
        "end_date": formatted_end_date,
        "exclude_websites": exclude_websites
    }

    # Create the GNews object with the prepared parameters
    google_news = GNews(**parameters)
    results = google_news.get_news("UK Finance")

    # Create new lists to hold extracted data
    publisher_titles = []
    publisher_hrefs = []

    # Extract publisher details
    for result in results:
        publisher_info = result.get('publisher', {})
        publisher_titles.append(publisher_info.get('title', ''))
        publisher_hrefs.append(publisher_info.get('href', ''))

    # Add extracted data to the dictionary
    for i, result in enumerate(results):
        result['publisher_title'] = publisher_titles[i]
        result['publisher_href'] = publisher_hrefs[i]

    # Create a DataFrame from the list of dictionaries
    df = pd.DataFrame(results)

    # Display the results using Streamlit
    if search_button_clicked and df is not None:
        st.write("Search Results:")
        st.dataframe(df)
