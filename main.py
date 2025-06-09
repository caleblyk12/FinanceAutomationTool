import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
import io

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


def categorize_transactions(df): #called everytime transactions are loaded, as part of processing to add category column
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

#initial cleaning: remove trailing commas from data and find header line index
def clean_file(file):

    #read byte file, convert into single string with /n in one line
    # and splitlines() converts that single line to a list of strings, and strips the /n at the end
    decoded = file.read().decode("utf-8").splitlines()


    header_identifiers = ['Transaction Date', 'Credit Amount', 'Debit Amount']
    header_index = None

    #dynamically look for header row index (start of data)
    for index, line in enumerate(decoded):
        if all(col in line for col in header_identifiers):
            header_index = index
            break

    if header_index is None:
        st.error("Could not find the column header in the uploaded file.")
        return None

    # Remove trailing commas only from data rows
    cleaned_lines = []
    for i, line in enumerate(decoded):
        if i > header_index:
            #stripping /n at the end is defensive coding, by right splitlines strips it before converting to list
            cleaned_lines.append(line.rstrip(',\n'))
        else:
            cleaned_lines.append(line)

    # Join cleaned lines and return as a file-like object, basically reversing original convertion to list of strings
    cleaned_file = io.StringIO("\n".join(cleaned_lines))
    return cleaned_file, header_index


def load_transactions(file): #all pre-processing here
    try:
        cleaned_file, header_index = clean_file(file)
        if cleaned_file is None:
            return None
        
        #skip rows prior to header
        df = pd.read_csv(cleaned_file, skiprows=header_index)


        #remove whitespace 
        df.columns = [col.strip() for col in df.columns]

        #rename cols, handle trailing commas in dbs statement with unnamed7 to category
        rename_map = {
            'Unnamed: 7': 'Category',
            'Debit Amount': 'Debit',
            'Credit Amount': 'Credit',
            'Transaction Ref1': 'Ref1',
            'Transaction Ref2': 'Ref2',
            'Transaction Ref3': 'Ref3',
            'Transaction Date': 'Date'
        }
        df.rename(columns=rename_map, inplace=True)


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

            st.session_state.debits_df = debits_df.copy()

            credits_df = overall_df[
                overall_df['Credit'] > 0
            ].copy()

            st.session_state.credits_df = credits_df.copy()

            tab1, tab2 = st.tabs(["Expenses (Debits)", "Income (Credits)"])



            ### EXPENSES PAGE ###
            with tab1:
                new_category = st.text_input('New Category Name')
                add_button = st.button('Add Category')

                if add_button and new_category:
                    if new_category not in st.session_state.categories:
                        st.session_state.categories[new_category] = []
                        save_categories()
                        st.rerun()

                st.subheader("Your expenses")

                edited_df = st.data_editor(
                    st.session_state.debits_df[["Date", "Debit", "Ref1", "Ref2", "Ref3", "Category"]], #select only these col

                    #column_config changes how UI views and interacts with data, not actually changing the df underlying data types
                    column_config={
                        "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
                        "Debit": st.column_config.NumberColumn("Debit", format="%.2f SGD"),
                        "Category": st.column_config.SelectboxColumn("Category", options=list(st.session_state.categories.keys())) #creates dropdown selection list from all the categories
                    },
                    hide_index=True,
                    use_container_width=True,
                    key="category_editor"
                )

                #Prepare to track keyword inputs for changed rows
                custom_keywords = {} #temporary dict, resets on every streamlit rerun and not saved in session_state
                st.markdown("---")
                st.markdown("### 🔍 Review and Add Keywords")

                for idx, row in edited_df.iterrows():
                    original_cat = st.session_state.debits_df.at[idx, "Category"]
                    new_cat = row["Category"]
                    if new_cat != original_cat: #if cat changed for the row, add box for kw input to be typed
                        st.markdown(f"**Row {idx + 1}**: `{row['Ref1']}` `{row['Ref2']}` `{row['Ref3']}` → Category changed to `{new_cat}`")

                        kw_input = st.text_input(
                            f"Choose a specific keyword/phrase/id to associate with `{new_cat}` for this row (must appear in ref1, 2 or 3):",
                            key=f"kw_input_{idx}"
                        )
                        if kw_input.strip():
                            custom_keywords[idx] = kw_input.strip() #Use row id as a key, new custom kw as value in the tempo dict

                #Save logic with optional keyword storage
                save_button = st.button('Apply Changes', type='primary')
                if save_button:
                    for idx, row in edited_df.iterrows():
                        new_cat = row["Category"]
                        old_cat = st.session_state.debits_df.at[idx, "Category"]

                        if new_cat != old_cat:
                            st.session_state.debits_df.at[idx, "Category"] = new_cat
                            if idx in custom_keywords: #if row id in temp dict as a key
                                added = add_kw_to_cat(new_cat, custom_keywords[idx]) #add value which is the kw to cat, returns true on success
                                if added:
                                    st.success(f"✅ Added keyword '{custom_keywords[idx]}' to category '{new_cat}'")
                                else:
                                    st.warning(f"⚠️ Keyword '{custom_keywords[idx]}' already exists in '{new_cat}' or was invalid.")
                       


                st.markdown("---")
                st.subheader('Expenses Summary and Visualisations')

                #reset_index converts the resultant pandas series into a clean dataframe with regularly numbered rows and cat as cols for visualisation
                #without it, you get a pandas series where cat is the index and values are the summed debit vals. Harder to throw into visualisation
                cat_totals = st.session_state.debits_df.groupby('Category')['Debit'].sum().reset_index()
                cat_totals = cat_totals.sort_values("Debit", ascending=False)

                st.dataframe(
                    cat_totals,
                    column_config={
                        "Debit": st.column_config.NumberColumn("Amount", format='%.2f SGD') #rename col and formatting in presentation layer to ui only. Underlying df is still "Debit"
                    },
                    use_container_width=True,
                    hide_index=True
                )

                fig1 = px.pie(
                    cat_totals,
                    values='Debit',
                    names='Category',
                    title='Expenses by Category'
                )

                fig2 = px.bar(
                    cat_totals,
                    y='Debit',
                    x='Category',
                    title='Expenses by Category'
                )

                st.plotly_chart(fig1, use_container_width=True)
                st.plotly_chart(fig2, use_container_width=False)




            ### INCOME PAGE ###
            with tab2:
                st.subheader('Income Summary')
                total_income = credits_df['Credit'].sum()
                st.metric('Total Income', f'{total_income:,.2f}, SGD')

                st.write(credits_df)

main()