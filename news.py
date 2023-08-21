import streamlit as st
from gnews import GNews
import pandas as pd
import openai
import time
import openai
import requests
from bs4 import BeautifulSoup

openai.api_key=st.secrets['openai_api']

def ask_GPT(news):
    prompt = f"""
    Your objective is to create a summary of a news webpage given by presenting\
    the most crucial information in bullet points.
    
    Summarize the News below, delimited by triple
    backticks.
    
    News: ```{news}```
    """
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        temperature=0,
        max_tokens=4096,
        messages=[
            {"role": "user", "content": prompt }
        ]
    )
    #total_tokens = completion["usage"]["total_tokens"]
    #print("Total Tokens:", total_tokens)
    return completion.choices[0].message.content

st.markdown("<div style='text-align: center;'><h1>News Search App</h1></div>", unsafe_allow_html=True)

# Style for the colored and centered note
note_style = "<div style='text-align: center; color: #3366ff; font-size: 18px;'>Note: You can either enter the period or start and end dates.</div>"

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
    max_results = st.text_input("News Count (default = 1):")
    
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
    max_results = int(max_results) if max_results else 1
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
    if not max_results or int(max_results) > 20:
        st.warning("Please enter a value less than or equal to 20 for max_results.")
    else:
        
        news_list = ["Uk Lending", "Uk loan interest rates", "uk unsecured loans, Uk economy"]
        results = []
        for j in news_list:
            results_k = google_news.get_news(j)
            results.extend(results_k)
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

    cgpt_text=[]
    txt_summ=[]
    for i, URL in enumerate(df['url']):  # Added enumeration to get the index 'i'
        try:
            r = requests.get(URL)
            r.raise_for_status()  # Check for request success
            soup = BeautifulSoup(r.text, 'html.parser')
            results = soup.find_all(['h1', 'p'])
            text = [result.get_text() for result in results]  # Use get_text() instead of result.text
            news_article = ' '.join(text)
            cgpt_text.append(news_article)
            summary_txt = ask_GPT(news_article)
            txt_summ.append(summary_txt)
            print(news_article)
            print('------------------------------------------------------------')
            # Add the title to the DataFrame
            df.loc[i, 'summary_title'] = df.loc[i, 'title']
            time.sleep(5)
            temp_var = 1
        except Exception as e:
            print(f"Error processing URL: {URL}\nError message: {e}")
            temp_var = 0

    # Store the summaries and titles in a .txt file
        with open('summaries.txt', 'w', encoding='utf-8') as file:
            for i, URL in enumerate(df['url']):
                try:
                    r = requests.get(URL)
                    r.raise_for_status()
                    soup = BeautifulSoup(r.text, 'html.parser')
                    results = soup.find_all(['h1', 'p'])
                    text = [result.get_text() for result in results]
                    news_article = ' '.join(text)
                    cgpt_text.append(news_article)
                    summary_txt = ask_GPT(news_article)
                    txt_summ.append(summary_txt)
        
                    # Add the title to the DataFrame
                    df.loc[i, 'summary_title'] = df.loc[i, 'title']
        
                    # Write the summary to the file
                    file.write(f"Title: {df['title'][i]}\n")
                    file.write(f"URL: {URL}\n")
                    file.write(f"Summary: {summary_txt}\n\n")
                    
                    print(news_article)
                    print('------------------------------------------------------------')
        
                    time.sleep(5)
        
                except requests.exceptions.RequestException as e:
                    error_message = str(e)
                    file.write(f"Failed URL: {URL}\n")
                    file.write(f"Error message: {error_message}\n\n")
                    print(f"Error processing URL: {URL}\nError message: {error_message}")



    with open('summaries.txt', 'r', encoding='utf-8') as file:
        file_contents = file.read()

    # Add a download button
    st.download_button(
        label="Download Summaries",
        data=file_contents,
        file_name='summaries.txt',
        mime='text/plain',
    )
