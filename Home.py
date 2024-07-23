import streamlit as st
import pandas as pd
import requests
import xml.etree.ElementTree as ET
import streamlit.components.v1 as components
import xml.etree.ElementTree as ET

st.set_page_config(layout = "wide", 
                    page_title='Geographic Bias Tool',
                    page_icon="",
                    initial_sidebar_state="auto") 
pd.set_option('display.max_colwidth', None)

with st.sidebar:
    # st.image(path2, width=150)
    st.subheader("Geographic Bias Tool",anchor=None)  
    with st.expander('About'):  
        st.write('Note here')
        components.html(
"""
<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons Licence" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/80x15.png" /></a><br />This tool is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.
"""
)

dois = st.text_area('Enter DOIs here', help='DOIs will be without a hyperlink such as 10.1136/bmjgh-2023-013696')
if dois:
    # Split the input text into individual DOIs based on newline character
    doi_list = dois.split('\n')
    
    # Remove any empty strings that may result from extra newlines
    doi_list = [doi.strip() for doi in doi_list if doi.strip()]
    
    # Create a DataFrame
    df_dois = pd.DataFrame(doi_list, columns=["DOI"])
    
    # Display the DataFrame
    df_dois
else:
    st.write("Enter DOIs in the text area to see the DataFrame.")

dois = ["10.1136/bmjgh-2023-013696", "10.1097/jac.0b013e31822cbdfd", '10.1080/02684527.2022.2055936', '10.1126/scitranslmed.aad9460']  # Add more DOIs as needed

df_dois = pd.DataFrame(dois, columns=['doi'])

df_dois

submit = st.button('Calculate Citation Source Index')

if submit:
    ## OPENALEX DATA RETRIEVAL
    def fetch_authorship_info_and_count(doi):
        url = f"https://api.openalex.org/works/doi:{doi}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            title = data.get('title', '')
            authorship_info = data.get('authorships', [])
            author_count = len(authorship_info)
            return title, authorship_info, author_count
        else:
            return '', [], 0

    # Function to fetch author details using author ID
    def fetch_author_details(author_id):
        response = requests.get(author_id)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return None

    # Fetch authorship information for each DOI and store it in a new DataFrame
    authorship_data = []

    for doi in df_dois['doi']:
        title, authorship_info, author_count = fetch_authorship_info_and_count(doi)
        for author in authorship_info:
            country_codes = author.get('countries', [])
            source = 'article page'
            if not country_codes:
                country_codes = ['']
                source = 'found through author page'
            for country_code in country_codes:
                author_record = {
                    'doi': doi,
                    'title': title,
                    'author_position': author.get('author_position', ''),
                    'author_name': author.get('author', {}).get('display_name', ''),
                    'author_id': author.get('author', {}).get('id', ''),
                    'Country Code 2': country_code,
                    'source': source,
                    'author_count': author_count
                }
                authorship_data.append(author_record)

    df_authorships = pd.DataFrame(authorship_data)

    # Remove duplicate rows
    df_authorships = df_authorships.drop_duplicates()

    # Add 'api.' between 'https://' and 'openalex' in the 'author_id' column
    df_authorships['author_id'] = df_authorships['author_id'].apply(lambda x: x.replace('https://', 'https://api.') if x else x)

    # Function to update country_code if missing and mark the source
    def update_country_code(row):
        if not row['Country Code 2'] and row['author_id']:
            author_details = fetch_author_details(row['author_id'])
            if author_details:
                affiliations = author_details.get('affiliations', [])
                if affiliations:
                    country_code = affiliations[0].get('institution', {}).get('country_code', '')
                    if country_code:
                        row['Country Code 2'] = country_code
                        row['source'] = 'author profile page'
        return row

    # Update country codes for rows where country_code is missing
    df_authorships = df_authorships.apply(update_country_code, axis=1)



    ## WORLD BANK API
    # Add 'api.' between 'https://' and 'openalex' in the 'author_id' column
    df_authorships['author_id'] = df_authorships['author_id'].apply(lambda x: x.replace('https://', 'https://api.') if x else x)

    # Function to update country_code if missing and mark the source
    def update_country_code(row):
        if not row['Country Code 2'] and row['author_id']:
            author_details = fetch_author_details(row['author_id'])
            if author_details:
                affiliations = author_details.get('affiliations', [])
                if affiliations:
                    country_code = affiliations[0].get('institution', {}).get('country_code', '')
                    if country_code:
                        row['Country Code 2'] = country_code
                        row['source'] = 'author profile page'
        return row

    # Update country codes for rows where country_code is missing
    df_authorships = df_authorships.apply(update_country_code, axis=1)

    # world_bank_api_url = "https://api.worldbank.org/v2/country/?per_page=1000"
    # response = requests.get(world_bank_api_url)
    # root = ET.fromstring(response.content)

    # # Extract relevant data and store it in a list
    # country_data = []
    # for country in root.findall(".//{http://www.worldbank.org}country"):
    #     country_id = country.get('id')
    #     iso2Code = country.find("{http://www.worldbank.org}iso2Code").text
    #     name = country.find("{http://www.worldbank.org}name").text
    #     income_level = country.find("{http://www.worldbank.org}incomeLevel").text
        
    #     country_record = {
    #         'Country Code 3': country_id,
    #         'Country Code 2': iso2Code,
    #         'name': name,
    #         'incomeLevel': income_level
    #     }
    #     country_data.append(country_record)

    # # Create a DataFrame from the list
    # df_countries = pd.DataFrame(country_data)
    df_countries = pd.read_csv('world_bank_api_results.csv')

    ## GNI CALCULATIONS
    df = pd.read_csv(
        'API_NY.GNP.PCAP.CD_DS2_en_csv_v2_1519779.csv',
        skiprows=4,  # Example: skipping the first 4 rows if they are not needed
        delimiter=',',  # Adjust delimiter if it's not a comma
    )
    df = df.drop(columns=['Indicator Name', 'Indicator Code'])

    # Melt the DataFrame to make it long-form
    df_melted = df.melt(id_vars=['Country Name', 'Country Code'], var_name='Year', value_name='GNI')
    df_melted = df_melted.rename(columns={'Country Code':'Country Code 3'})
    # Drop rows with missing GNI values
    df_melted = df_melted.dropna(subset=['GNI'])

    # Convert 'Year' to integer
    df_melted['Year'] = df_melted['Year'].astype(int)

    # Sort by 'Country Name' and 'Year' to get the latest GNI for each country
    df_sorted = df_melted.sort_values(by=['Country Name', 'Year'], ascending=[True, False])

    # Drop duplicates to keep the most recent GNI for each country
    df_most_recent = df_sorted.drop_duplicates(subset=['Country Name'])

    # Select the desired columns
    df_result = df_most_recent[['Country Name', 'Country Code 3', 'Year', 'GNI']].reset_index(drop=True)
    df_result = pd.merge(df_result, df_countries, on='Country Code 3', how='left')
    df_result = df_result[df_result['incomeLevel']!='Aggregates'].reset_index(drop=True)
    df_result = df_result.sort_values(by='GNI', ascending=True).reset_index(drop=True)
    df_result.index = df_result.index + 1
    df_result = df_result.rename_axis('Rank').reset_index()

    df_authorships = pd.merge(df_authorships, df_result, on='Country Code 2', how='left')


    df_authorships['author_weighting'] = 1 / df_authorships['author_count']
    df_authorships['author_weighting_score'] = df_authorships['Rank']*df_authorships['author_weighting']
    df_authorships['all_authors'] = df_authorships.groupby('doi')['author_name'].transform(lambda x: ' | '.join(x))
    df_authorships['Countries'] = df_authorships.groupby('doi')['Country Name'].transform(lambda x: ' | '.join(x))


    ## CSI CALCULATION
    country_count = df_result['Country Code 3'].nunique()

    df_authorships_mean_rank = df_authorships.groupby('doi')['Rank'].mean()
    csi = round(df_authorships_mean_rank/country_count, 2)

    df_authorships = df_authorships.merge(csi.rename('Citation Source Index'), on='doi', how='left')
    average_rank = df_authorships['Rank'].mean()
    country_count = df_result['Country Code 3'].nunique()
    citation_source_index = average_rank / country_count
    st.write(f'Citation Source Index: {round(citation_source_index, 2)}')
    df_final = df_authorships[['Citation Source Index', 'doi', 'title', 'all_authors', 'Countries']].drop_duplicates().reset_index(drop=True)
    df_final