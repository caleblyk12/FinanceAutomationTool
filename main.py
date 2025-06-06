import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

st.set_page_config(page_title='Finance Automation App', page_icon='💵', layout='wide')

category_file = 'categories.json'

#everytime page is loaded in, set uncategorized as a default categories in session_state
if "categories" not in st.session_state:
    st.session_state.categories = {
        "Uncategorized": []
    }

#then check if theres a preexisting cat list from last time. if have, replace session_state with those categories
if os.path.exists(category_file):
    with open(category_file, 'r') as f:
        st.session_state.categories = json.load(f)

# this is called everytime user adds a new category, which creates the file for first time setup and sets categories in the json
# if not first time setup, this simply overwrites whatever is in categories json with session_state categories
def save_categories():
    with open(category_file, 'w') as f: #if file doesnt yet exist, write mode will auto create it
        json.dump(st.session_state.categories, f)


def categorize_transactions(df): #called everytime transactions are loaded, as part of processing
    df["Category"] = "Uncategorized" #creates/overwrites column 'category', all rows will now have a value of 'uncategorized' by default

    #for key, value in dict.items() where sess state . categories is a dict, keys are the cat names, values are list of keywords
    for category, keywords in st.session_state.categories.items():
        if category == "Uncategorized" or not keywords:
            continue #will never categorize a transaction into uncategorized, or if theres no keywords

        lowered_keywords = [kw.lower().strip() for kw in keywords]

        for idx, row in df.iterrows(): #iterate through every row in df
            details = " ".join([
                str(row['Ref1']) if pd.notna(row['Ref1']) else "", #either convert to string form, or if na replace with empty string
                str(row['Ref2']) if pd.notna(row['Ref2']) else "",
                str(row['Ref3']) if pd.notna(row['Ref3']) else ""
            ]).lower().strip()

            if any(keyword in details for keyword in lowered_keywords): #loops through lowered keywords for this category, checks if any of the words are in details string
                df.at[idx, "Category"] = category
    
    return df


def load_transactions(file):
    try:
        df = pd.read_csv(file)

        #remove whitespace 
        df.columns = [col.strip() for col in df.columns]


        #remove commas, conv to float for processing
        df['Debit'] = pd.to_numeric(
            df['Debit'].str.replace(',', ''),  # Remove commas first
            errors='coerce'  # Convert blanks or other errors to NaN
        ).fillna(0)  # Replace NaN with 0
        df['Credit'] = pd.to_numeric(
            df['Credit'].str.replace(',', ''),  # Remove commas first
            errors='coerce'  # Convert blanks or other errors to NaN
        ).fillna(0)  # Replace NaN with 0


        #convert to datetime object for processing
        df['Date'] = pd.to_datetime(df['Date'], format="%d %b %Y")

        return categorize_transactions(df)
    
    except Exception as e:
        st.error(f'Error processing file: {str(e)}')
        return None


def add_kw_to_cat(category, keyword):
    keyword = keyword.strip()
    if keyword and keyword not in st.session_state.categories[category]:
        st.session_state.categories[category].append(keyword)
        save_categories()
        return True
    return False #no valid keyword given, or keyword alrd exists in cat


def main():
    st.title('Finance Automated Categorical Analysis Dashboard')

    uploaded_file = st.file_uploader("Upload your transaction CSV file", type=['csv'])

    if uploaded_file is not None:
        overall_df = load_transactions(uploaded_file)
        if overall_df is not None:

            debits_df = overall_df[
                overall_df['Debit'] > 0 #filter overall_df to include rows where inner statement is true
            ].copy() #create copy so it doesnt mutate original df

            credits_df = overall_df[
                overall_df['Credit'] > 0
            ].copy()

            tab1, tab2 = st.tabs(["Expenses (Debits)", "Income (Credits)"])
            with tab1:
                new_category = st.text_input('New Category Name')
                add_button = st.button('Add Category')

                if add_button and new_category:
                    if new_category not in st.session_state.categories:
                        st.session_state.categories[new_category] = []
                        save_categories()
                        st.rerun()

                st.write(debits_df)
            with tab2:
                st.write(credits_df)

main()