"""The main parser for our project."""

import pandas as pd

import logging
from datetime import datetime
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import numpy as np


logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
file_handler = logging.FileHandler('message.log')
fomatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

logger.setLevel(logging.INFO)

console_handler.setFormatter(fomatter)
file_handler.setFormatter(fomatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)


def read_file_subset(filepath, subset=[]):
    """reads the given CSV and returns a dataframe

        Input: 
            - Filepath : path to the file
            - subset : LIST of column names that you want to keep (default is all)
        Output:
            - Dataframe with your csv read, data is NOT cleaned

    """

    # read the file
    try:
        df = pd.read_csv(filepath)
        logger.info(f"Read csv file {filepath} into pandas dataframe")
    except pd.errors.EmptyDataError as e:
        logger.warning(f"File is empty. Error message: {e}")
        return None
    except pd.errors.ParserError as e:
        logger.warning(f"Error parsing the CSV file. Error message: {e}")
        raise RuntimeError("Something went wrong with the parsing, try again e:",e)
    except FileNotFoundError as e:
        logger.warning(f"File not found. Error message: {e}")
        raise FileNotFoundError("Filepath wrong e:",e)
    except Exception as e:
        logger.error(f"An unexpected error occurred. Error message: {e}")
        exit(-1) # quit now, we need to fix this

    # extract subset of data we want to work with if any
    if not subset:
        return df
    else:
        return df[subset]




# this is something we can't fully automate and would need code changes, this is because
# it takes input from a human to decide what types we want to store everything in the DB
def clean_data(df):
    """Cleans the given Dataframe
    
    -Converts numerical entries to Int/Float
    - decide if there are too many NaN entries and if we need to drop a col, or do we fill
    - removes duplicate rows, strip whitespace and standardize text
    
    """
    # Our subset in THIS dataset
    # age (int) ,monthly_income (float ),daily_internet_hours(float),smartphone_usage_years(float),social_media_hours(float),
    # online_payment_trust_score(float),tech_savvy_score(float),monthly_online_orders(int),monthly_store_visits(int),
    # avg_online_spend(float),shopping_preference(string)
    #

    # DROP things here
    #print(df.tail())
    df = df.replace("", np.nan)
    invalid_entries = df[df.duplicated(keep='first') | df.isnull().any(axis=1)]
    na_rows = df[df.isnull().any(axis=1)]
    logger.info(f"na rows: {na_rows}")
    df.dropna(inplace=True) # drop rows with any NaN values

    dupe_rows = df[df.duplicated(keep='first')]
    logger.info(f"dupe rows: {dupe_rows}")
    df.drop_duplicates(inplace=True) # drop duplicate rows


    # type conversions
    df["age"] = df["age"].astype(int)
    df["monthly_income"] = df["monthly_income"].astype(float)
    df["daily_internet_hours"] = df["daily_internet_hours"].astype(float)
    df["smartphone_usage_years"] = df["smartphone_usage_years"].astype(float)
    df["social_media_hours"] = df["social_media_hours"].astype(float)
    df["online_payment_trust_score"] = df["online_payment_trust_score"].astype(float)
    df["tech_savvy_score"] = df["tech_savvy_score"].astype(float)
    df["monthly_online_orders"] = df["monthly_online_orders"].astype(int)
    df["monthly_store_visits"] = df["monthly_store_visits"].astype(int)
    df["avg_online_spend"] = df["avg_online_spend"].astype(float)
    df["shopping_preference"] = df["shopping_preference"].astype(str)

    # string standardizing
    df["shopping_preference"] = df["shopping_preference"].apply(lambda x : x.strip().lower())

    # type conversions
    invalid_entries["age"] = invalid_entries["age"].astype(int)
    invalid_entries["monthly_income"] = invalid_entries["monthly_income"].astype(float)
    invalid_entries["daily_internet_hours"] = invalid_entries["daily_internet_hours"].astype(float)
    invalid_entries["smartphone_usage_years"] = invalid_entries["smartphone_usage_years"].astype(float)
    invalid_entries["social_media_hours"] = invalid_entries["social_media_hours"].astype(float)
    invalid_entries["online_payment_trust_score"] = invalid_entries["online_payment_trust_score"].astype(float)
    invalid_entries["tech_savvy_score"] = invalid_entries["tech_savvy_score"].astype(float)
    invalid_entries["monthly_online_orders"] = invalid_entries["monthly_online_orders"].astype(int)
    invalid_entries["monthly_store_visits"] = invalid_entries["monthly_store_visits"].astype(int)
    invalid_entries["avg_online_spend"] = invalid_entries["avg_online_spend"].astype(float)
    invalid_entries["shopping_preference"] = invalid_entries["shopping_preference"].astype(str)
    
    # string standardizing
    invalid_entries["shopping_preference"] = invalid_entries["shopping_preference"].apply(lambda x : x.strip().lower())

    return (df, invalid_entries)



def add_id_feature(df):
    "Adds a unique id to each row"
    arr = list(range(df.shape[0]))
    df["id"] = arr
    
    return df


# preprocessing that's specific to our dataset, this would need to be changed
def preprocessing(df):
    # preprocessing all the tables
    df = add_id_feature(df)
    shopping_mapper = {"store":1, "online":2, "hybrid" : 3}
    # change to our id
    df["shopping_preference"] = df["shopping_preference"].apply(lambda x : shopping_mapper[x])

    # the id refers to customers.id (which is a foreign key to every other table besides customers)
    customers_table = df[["id","age","monthly_income"]]
    technology_usage_table = df[["id","daily_internet_hours","smartphone_usage_years"]]
    social_behavior_table = df[["id","social_media_hours", "online_payment_trust_score", "tech_savvy_score"]]
    shopping_behavior_table = df[["id","monthly_online_orders", "monthly_store_visits", "avg_online_spend","shopping_preference"]]
    shopping_preference_table = df[["shopping_preference"]]

    return {
        "customers": customers_table,
        "technology_usage":technology_usage_table,
        "social_behavior":social_behavior_table,
        "shopping_behavior": shopping_behavior_table,
        "shopping_preference":shopping_preference_table
    }

def upload_to_db():
    print("UPLOAD TO DB START")
    load_dotenv()
    FILEPATH = os.getenv("FILEPATH")
    # print("FILEPATH:",FILEPATH)
    # read the filepath
    subset = [
        'age', 'monthly_income', 'daily_internet_hours', 'smartphone_usage_years', 'social_media_hours', 'online_payment_trust_score',
        'tech_savvy_score', 'monthly_online_orders', 'monthly_store_visits', 'avg_online_spend', 'shopping_preference'
    ]
    # print("I am reading the file")
    logger.info("I am reading the file")
    df = pd.DataFrame() # empty df
    try:
        df = read_file_subset(FILEPATH, subset)
    except FileNotFoundError as e:
        print(f"Error locating file: {e}")
        logger.error("Error locating file: ",e)
    except RuntimeError as e:
        print(f"Runtime error: {e}")
        logger.error("Runtime error: ",e)

    if df.empty:
        # print("ERROR df is empty")
        logger.error("DF IS EMPTY AFTER READ")
        return
    # clean data
    # print("I am cleaning the data")
    df, invalid_entries = clean_data(df)
    # print(f"\n\ninvalid_entries: {invalid_entries}\n\n")

    # preprocess the data and format it for our tables
    # print("I am pre-processing")
    processed_dataframes = preprocessing(df)

    # make engine
    # print("I am making engine")
    CONNECTION_STRING = os.getenv("CONNECTION_STRING")
    engine = create_engine(CONNECTION_STRING)

    # use engine to call createtables.sql
    with engine.connect() as con:
        with open("./src/SQL/CreateTables.sql") as file:
            # print("i am reading the file")
            query = text(file.read()) # translate it to sqlalchemy text
            con.execute(query)
        con.commit()
        # print("I am in the engine")
        # insert our entries for each table

    #============== INSERTING ENTRIES INTO TABLES ==============
        # print("Populating Customers table...")
        logger.info("Populating Customers table...")
        customers = processed_dataframes["customers"]
        # use paramaterized query string (prvents sql injection)
        customers_query = text("""INSERT INTO customers(customer_id, age, monthly_income) VALUES(:customer_id,:age,:monthly_income);""")

        for _, entry in customers.iterrows():

            # this dict stories how our sql interacts with our param query string
            parameters = {
                "customer_id":int(entry["id"]),
                "age":int(entry["age"]),
                "monthly_income":float(entry["monthly_income"])
            }

            con.execute(customers_query,parameters)
        con.commit() # commit changes to table

        
        # # this comes next after customers b/c there are other FK references to this I think   
        # print("Populating Shopping Preference...")
        logger.info("Populating Shopping Preference...")
        shopping_preferance = processed_dataframes["shopping_preference"]
        shopping_mapper2 = {1: "store", 2: "hybrid", 3: "online"}
        shopping_preferance.drop_duplicates(inplace=True) # drops duplicate shopping preferances, we only want 3 entries in this table (store, online, hybrid)
        sql = text("""INSERT INTO shopping_preference(shopping_preference_id, preference_name)
        VALUES(:id, :preference_name)""")
        for _, entry in shopping_preferance.iterrows():
            parameters = {
                "id": int(entry["shopping_preference"]),
                "preference_name": shopping_mapper2[int(entry["shopping_preference"])]
            }
            con.execute(sql, parameters)
        con.commit()

        # print("Populating Technology_Usage table...")
        logger.info("Populating Technology_Usage table...")
        technology_usage = processed_dataframes["technology_usage"]
        technology_usage_query = text("""
                                      INSERT INTO technology_usage(
                                      customer_id, daily_internet_hours, smartphone_usage_years)
                                      VALUES(
                                      :technology_usage_id, :daily_internet_hours, :smartphone_usage_years);""")
        
        for _, entry in technology_usage.iterrows():
            parameters = {
                "technology_usage_id" : int(entry["id"]),
                "daily_internet_hours" : float(entry["daily_internet_hours"]),
                "smartphone_usage_years" : float(entry["smartphone_usage_years"])
            }
        
            con.execute(technology_usage_query, parameters)
        con.commit()
        
        # print("Populating Social Behavior table...")
        logger.info("Populating Social Behavior table...")
        social_behavior = processed_dataframes["social_behavior"]
        social_behavior_query = text("""INSERT INTO social_behavior(customer_id, social_media_hours, online_payment_trust_score, tech_savvy_score)
        VALUES(:customer_id, :social_media_hours,:online_payment_trust_score,:tech_savvy_score);""")
        for _, entry in social_behavior.iterrows():
            parameters = {
                "customer_id" : int(entry["id"]),
                "social_media_hours" : float(entry["social_media_hours"]),
                "online_payment_trust_score" : float(entry["online_payment_trust_score"]),
                "tech_savvy_score" : float(entry["tech_savvy_score"])
            }
            con.execute(social_behavior_query, parameters)
        con.commit()
            
        
        # print("Populating Shopping Behavior...")
        logger.info("Populating Shopping Behavior")
        shopping_behavior = processed_dataframes["shopping_behavior"]
        shopping_behavior_query = text("""INSERT INTO shopping_behavior(customer_id, monthly_online_orders, monthly_store_visits, avg_online_spend, shopping_preference_id)
                       VALUES(:customer_id, :monthly_online_orders, :monthly_store_visits, :avg_online_spend, :shopping_id);""")
        for _, entry in shopping_behavior.iterrows():
            parameters = {
                "customer_id": int(entry["id"]),
                "monthly_online_orders": int(entry["monthly_online_orders"]),
                "monthly_store_visits": int(entry["monthly_store_visits"]),
                "avg_online_spend": float(entry["avg_online_spend"]),
                "shopping_id": int(entry["shopping_preference"])
            }
            con.execute(shopping_behavior_query, parameters)
        con.commit()


        # print("Populating Invalid Entries...")
        logger.info("Populating Invalid Entries...")
        invalid_entries_query = text("""
                                      INSERT INTO invalid_entries(
                                      age, monthly_income, daily_internet_hours, smartphone_usage_years, social_media_hours,
                                      online_payment_trust_score, tech_savvy_score, monthly_online_orders, monthly_store_visits,
                                      avg_online_spend, shopping_preference)
                                      VALUES(
                                      :age, :monthly_income, :daily_internet_hours, :smartphone_usage_years, :social_media_hours,
                                      :online_payment_trust_score, :tech_savvy_score, :monthly_online_orders, :monthly_store_visits,
                                      :avg_online_spend, :shopping_preference);""")
        
        # change the types here while preserving none (sql alchemy likes None for nullables)
        for _, entry in invalid_entries.iterrows():
            logger.debug(f"Invalid entry found: {entry}")
            parameters = {
                "age" : int(entry["age"]),
                "monthly_income" : float(entry["monthly_income"]),
                "daily_internet_hours" : float(entry["daily_internet_hours"]),
                "smartphone_usage_years" : float(entry["smartphone_usage_years"]),
                "social_media_hours" : float(entry["social_media_hours"]),
                "online_payment_trust_score" : float(entry["online_payment_trust_score"]),
                "tech_savvy_score" : float(entry["tech_savvy_score"]),
                "monthly_online_orders" : int(entry["monthly_online_orders"]),
                "monthly_store_visits" : int(entry["monthly_store_visits"]),
                "avg_online_spend" : float(entry["avg_online_spend"]),
                "shopping_preference" : entry["shopping_preference"]
            }
        
            con.execute(invalid_entries_query, parameters)
        con.commit()
    # print("SUCCESSFULLY LOADED DATA INTO TABLES")
    logger.info("SUCCESSFULLY LOADED DATA INTO TABLES")
    return 0

# if __name__ == "__main__":
#     upload_to_db()