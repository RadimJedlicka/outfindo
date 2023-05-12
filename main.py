from typing import Dict, Union
from collections import Counter

import pandas as pd

from country_codes import country_codes


df = pd.read_csv('dealers.csv')

df['telephone'] = df['telephone'].astype('str')
df['email'] = df['email'].astype('str')  

list_of_emails = df['email'].to_list()


def extract_domain(email: str) -> str:
    """
    Extracts the domain from an email address.

    Args:
        email (str): The email address 
        from which to extract the domain.

    Returns:
        str: The domain extracted from the email address, 
        or the original email if it is empty or 'nan'.

    """
    if email and email != 'nan':
        domain = email.split('@')[-1]
        return domain
    return email

extracted_domains = [extract_domain(email) for email in list_of_emails]

counter = Counter(extracted_domains)
email_freq = counter.most_common()
email_freq = dict(email_freq)
email_freq.pop('nan')


def should_fill_website(
    domain: str, 
    email_freq: Dict[str, int],
    threshold: int, 
) -> bool:
    """
    Determines whether the website should be filled 
    based on the frequency of the domain in email addresses.

    Args:
        domain (str): The domain for which to check the frequency.
        threshold (int): The threshold value for the frequency.
        email_freq (Dict[str, int]): A dictionary 
            mapping domains to their corresponding frequency.

    Returns:
        bool: True if the frequency of the domain is below the threshold, 
              False otherwise.

    """
    return email_freq.get(domain, 0) < threshold


def fill_website(row: pd.Series) -> pd.Series:
    """
    Fill the 'web' column in a DataFrame row 
    based on the 'email' column.

    If the 'web' column is empty or 'nan' 
    and the 'email' column is not empty, 
    it extracts the domain from the email
    and checks if it should fill the 'web' column 
    based on the frequency threshold.

    Args:
        row (pd.Series): A row from the DataFrame 
            containing the 'email' and 'web' columns.

    Returns:
        pd.Series: The modified row with the 'web' column filled if applicable.

    """
    email = row['email']
    web = row['web']
    
    if pd.isna(web) and email and email != 'nan':
        domain = extract_domain(email)
        if should_fill_website(domain, email_freq, threshold=100):
            row['web'] = f'www.{domain}'
    return row


def normalize_phone_number(
    row: pd.Series, 
    country_codes: Dict[str, str]
) -> Union[str, pd.Series]:
    """
    Normalize the phone number in a DataFrame row 
    based on the country code dictionary.

    Args:
        row (pd.Series): A row from the DataFrame 
        containing the 'country' and 'telephone' columns.
        
        country_codes (Dict[str, str]): A dictionary mapping 
        country names to their respective country codes.

    Returns:
        Union[str, pd.Series]: The normalized phone number, 
        including the international prefix if applicable, 
        or the original phone number if the country 
        is not found in the country codes dictionary.
    """
    
    country = row['country']
    
    if country in country_codes:
        country_code = country_codes[country]
        normalized_number = ''.join(filter(str.isdigit, row['telephone']))
        
        if normalized_number.startswith(country_code.strip('+')):
            return f"+{normalized_number[:2]} {normalized_number[2:]}"
        
        normalized_number = f"{country_code} {normalized_number}"
        return normalized_number
    else:
        return row['telephone']


def add_chain_col(df: pd.DataFrame) -> pd.DataFrame:
    """
    Expand the data in the DataFrame by adding a 'chain' 
    column for eshops selling multiple brands.

    For eshops that appear multiple times in the DataFrame, 
    indicating they sell products from multiple brands,
    the 'chain' column will have the same value for all rows 
    corresponding to the same dealer. If there are no
    duplicates, the 'chain' column will be left blank.

    Args:
        df (pd.DataFrame): The DataFrame containing the dealer data.

    Returns:
        pd.DataFrame: The modified DataFrame with the 'chain' column added.

    """
    # Check for duplicates based on the 'eshop' column
    duplicates = df.duplicated(subset=['eshop'], keep=False)
    
    # Create a new 'chain' column and fill it with the eshop name for duplicates
    df['chain'] = df.loc[duplicates, 'eshop'].copy()
    
    # Forward-fill the 'chain' column to propagate the eshop name for all duplicate rows
    # df['chain'].fillna(method='ffill', inplace=True)
    
    return df

df['telephone'] = df.apply(normalize_phone_number, args=(country_codes,), axis=1)
df = df.apply(fill_website, axis=1)
df = add_chain_col(df)

if __name__ == '__main__':
    df.to_csv('output.csv')
