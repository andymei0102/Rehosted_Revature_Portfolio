"""File to test parser.py functionality"""
import pytest
from src.parser import clean_data, read_file_subset, add_id_feature, preprocessing, upload_to_db
import pandas as pd
import numpy as np

class TestParserFunctionality:
    """Test all of the parser's edgecases"""

# test cases for testing read_file_subset in parser.py
    def test_file_not_found(self):
        # test file not found when parsing
        with pytest.raises(FileNotFoundError):
            read_file_subset("NotAValidFile", [])

    def test_empty_file(self, tmp_path):
        # test file is empty — function catches EmptyDataError and returns None
        empty_file = tmp_path / "empty_file.csv"
        empty_file.write_text("")
        result = read_file_subset(str(empty_file), [])
        assert result is None

    def test_parsing_error(self, tmp_path):
        # test that a malformed/corrupt file raises a RuntimeError (wrapped by the function)
        bad_file = tmp_path / "malformed.csv"
        bad_file.write_text("col1,col2\n1,2,3\n4,5,6,7")
        with pytest.raises(RuntimeError):
            read_file_subset(str(bad_file), [])

    def test_reading_file(self):
        # test reading in a file with a given subset
        # ARRANGE
        # expected output when reading the data:
        # 11 columns with 7 rows
        # 2 rows have only 6 non NULL values
        expected_output = pd.DataFrame({
            'age': [56, 69, 46, 32, 60, 60, 60],
            'monthly_income': [221111.0, 96029.0, 19055.0, 53170.0, 244016.0, 244016.0, 244016.0],
            'daily_internet_hours': [6.5, 8.2, 6.4, 6.4, 6.0, 6.0, 6.0],
            'smartphone_usage_years': [12.0, 13.0, 4.0, 11.0, 5.0, 5.0, 5.0],
            'social_media_hours': [0.7, 2.7, 2.1, 0.7, 0.7, 0.7, 0.7],
            'online_payment_trust_score': [1.0, 6.0, 10.0, 2.0, 2.0, 2.0, 2.0],
            'tech_savvy_score': [6.0, 9.0, 8.0, 10.0, 5.0, 5.0, None],
            'monthly_online_orders': [16, 14, 2, 20, 18, 18, 18],
            'monthly_store_visits': [16, 1, 0, 3, 16, 16, 16],
            'avg_online_spend': [28551.0, 124056.0, 81939.0, 35901.0, 131971.0, 131971.0, None],
            'shopping_preference': ['Store', 'Hybrid', 'Store', 'Store', 'Store', 'Store', 'Store']
        })

        # ACT
        # get data frame from reading in the file
        subset = [
            'age', 'monthly_income', 'daily_internet_hours', 'smartphone_usage_years', 'social_media_hours', 'online_payment_trust_score',
            'tech_savvy_score', 'monthly_online_orders', 'monthly_store_visits', 'avg_online_spend', 'shopping_preference'
        ]
        df = read_file_subset('tests/test_subset.csv', subset)
        test = df.compare(expected_output)

        # ASSERT
        assert test.empty, f"Cleaned data does not match expected output diff:{df.compare(test)}"
        


    def test_read_file_no_subset_returns_all_columns(self, tmp_path):
        # when subset is empty (default), all columns from the CSV are returned
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("col1,col2,col3\n1,2,3\n4,5,6")
        df = read_file_subset(str(csv_file))
        assert list(df.columns) == ["col1", "col2", "col3"]
        assert len(df) == 2

    def test_read_file_with_subset_returns_only_requested_columns(self, tmp_path):
        # when a subset list is provided, only those columns are returned
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("col1,col2,col3\n1,2,3\n4,5,6")
        df = read_file_subset(str(csv_file), ["col1", "col3"])
        assert list(df.columns) == ["col1", "col3"]
        assert "col2" not in df.columns

    def test_read_file_subset_preserves_row_count(self, tmp_path):
        # row count is preserved when selecting a subset of columns
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("a,b,c\n1,2,3\n4,5,6\n7,8,9")
        df = read_file_subset(str(csv_file), ["a", "b"])
        assert len(df) == 3

    def test_read_file_invalid_column_raises_key_error(self, tmp_path):
        # requesting a column that does not exist raises a KeyError
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("col1,col2\n1,2")
        with pytest.raises(KeyError):
            read_file_subset(str(csv_file), ["col1", "nonexistent_col"])

    def test_read_file_returns_dataframe(self, tmp_path):
        # return type is always a pandas DataFrame
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("x,y\n10,20")
        result = read_file_subset(str(csv_file))
        assert isinstance(result, pd.DataFrame)

    def test_subset_csv_returns_dataframe(self):
        # read_file_subset on test_subset.csv returns a DataFrame
        df = read_file_subset('tests/test_subset.csv')
        assert isinstance(df, pd.DataFrame)

    def test_subset_csv_row_count(self):
        # test_subset.csv has 7 data rows (excluding header)
        df = read_file_subset('tests/test_subset.csv')
        assert len(df) == 7

    def test_subset_csv_column_count(self):
        # test_subset.csv has 11 columns
        df = read_file_subset('tests/test_subset.csv')
        assert len(df.columns) == 11

    def test_subset_csv_expected_columns(self):
        # test_subset.csv contains all expected column names
        expected_cols = [
            'age', 'monthly_income', 'daily_internet_hours', 'smartphone_usage_years',
            'social_media_hours', 'online_payment_trust_score', 'tech_savvy_score',
            'monthly_online_orders', 'monthly_store_visits', 'avg_online_spend',
            'shopping_preference'
        ]
        df = read_file_subset('tests/test_subset.csv')
        assert list(df.columns) == expected_cols

    def test_subset_csv_single_column_subset(self):
        # requesting only 'age' column returns a DataFrame with just that column
        df = read_file_subset('tests/test_subset.csv', ['age'])
        assert list(df.columns) == ['age']
        assert len(df) == 7

    def test_subset_csv_two_column_subset(self):
        # requesting two columns returns only those columns with correct row count
        df = read_file_subset('tests/test_subset.csv', ['age', 'monthly_income'])
        assert list(df.columns) == ['age', 'monthly_income']
        assert len(df) == 7

    def test_subset_csv_age_values(self):
        # age column values match expected data from test_subset.csv
        df = read_file_subset('tests/test_subset.csv', ['age'])
        assert list(df['age']) == [56, 69, 46, 32, 60, 60, 60]

    def test_subset_csv_contains_nulls(self):
        # test_subset.csv has rows with NaN values (row 7 has missing tech_savvy_score and avg_online_spend)
        df = read_file_subset('tests/test_subset.csv')
        assert df.isnull().any().any()

    def test_subset_csv_null_column_locations(self):
        # NaN values appear specifically in tech_savvy_score and avg_online_spend columns
        df = read_file_subset('tests/test_subset.csv')
        assert df['tech_savvy_score'].isnull().any()
        assert df['avg_online_spend'].isnull().any()

    def test_subset_csv_shopping_preference_values(self):
        # shopping_preference column contains expected raw values (un-cleaned)
        df = read_file_subset('tests/test_subset.csv', ['shopping_preference'])
        assert set(df['shopping_preference'].unique()).issubset({'Store', 'Hybrid'})

    def test_subset_csv_invalid_column_raises_key_error(self):
        # requesting a non-existent column from test_subset.csv raises KeyError
        with pytest.raises(KeyError):
            read_file_subset('tests/test_subset.csv', ['age', 'nonexistent_col'])


def test_clean_data():

    """Test clean_data function in parser.py"""
    
    # get sample data from test_subset.csv
    sample_data = pd.read_csv('tests/test_subset.csv')
    # expected output after cleaning the data
    # expected behavior changes:
    #   - rows 6 and 7 are duplicates, so drop them
    #   - Row 8 has nan values so it should be dropped
    #   - text for "Store" and " Hybrid" should be standardized to "store" and "hybrid" (strip whitespace and lowecase it all)
    # these are expected rows and typings     
    # age (int) ,monthly_income (float ),daily_internet_hours(float),smartphone_usage_years(float),social_media_hours(float),
    # online_payment_trust_score(float),tech_savvy_score(float),monthly_online_orders(int),monthly_store_visits(int),
    # avg_online_spend(float),shopping_preference(string)
    expected_output = pd.DataFrame({
        'age': [56, 69, 46, 32, 60],
        'monthly_income': [221111.0, 96029.0, 19055.0, 53170.0, 244016.0],
        'daily_internet_hours': [6.5, 8.2, 6.4, 6.4, 6.0],
        'smartphone_usage_years': [12.0, 13.0, 4.0, 11.0, 5.0],
        'social_media_hours': [0.7, 2.7, 2.1, 0.7, 0.7],
        'online_payment_trust_score': [1.0, 6.0, 10.0, 2.0, 2.0],
        'tech_savvy_score': [6.0, 9.0, 8.0, 10.0, 5.0],
        'monthly_online_orders': [16, 14, 2, 20, 18],
        'monthly_store_visits': [16, 1, 0, 3, 16],
        'avg_online_spend': [28551.0, 124056.0, 81939.0, 35901.0, 131971.0],
        'shopping_preference': ['store', 'hybrid', 'store', 'store', 'store']
    })

    expected_output2 = pd.DataFrame({
        'age': [60,60],
        'monthly_income': [244016.0,244016.0],
        'daily_internet_hours': [6.0,6.0],
        'smartphone_usage_years': [5.0,5.0],
        'social_media_hours': [0.7,0.7],
        'online_payment_trust_score': [2.0,2.0],
        'tech_savvy_score': [5.0, np.nan],
        'monthly_online_orders': [18,18],
        'monthly_store_visits': [16, 16],
        'avg_online_spend': [131971.0, np.nan],
        'shopping_preference': ['store', 'store']
    })
    # clean the data using the function
    cleaned_data, rejected_rows = clean_data(sample_data)

    #test rejected rows
    pd.set_option('display.max_columns', None)
    test2 = expected_output2.reset_index(drop=True).compare(rejected_rows.reset_index(drop=True))
    assert test2.empty, f"Rejected data does not match expected output diff:{test2}"

    # assert that the cleaned data matches the expected output
    test = cleaned_data.compare(expected_output)
    assert test.empty, f"Cleaned data does not match expected output diff:{cleaned_data.compare(test)}"


def test_add_id():
    """tests adding id feature"""

    sample_data = pd.read_csv('tests/test_subset.csv')

    expected_output1 = pd.DataFrame({
        'age': [56, 69, 46, 32, 60],
        'monthly_income': [221111.0, 96029.0, 19055.0, 53170.0, 244016.0],
        'daily_internet_hours': [6.5, 8.2, 6.4, 6.4, 6.0],
        'smartphone_usage_years': [12.0, 13.0, 4.0, 11.0, 5.0],
        'social_media_hours': [0.7, 2.7, 2.1, 0.7, 0.7],
        'online_payment_trust_score': [1.0, 6.0, 10.0, 2.0, 2.0],
        'tech_savvy_score': [6.0, 9.0, 8.0, 10.0, 5.0],
        'monthly_online_orders': [16, 14, 2, 20, 18],
        'monthly_store_visits': [16, 1, 0, 3, 16],
        'avg_online_spend': [28551.0, 124056.0, 81939.0, 35901.0, 131971.0],
        'shopping_preference': ['store', 'hybrid', 'store', 'store', 'store']
    })

    cleaned_data,rejected_rows = clean_data(sample_data)

    # test cleaned_data works
    test = cleaned_data.compare(expected_output1)
    assert test.empty, f"Cleaned data does not match expected output diff:{cleaned_data.compare(test)}"



    # test adding id works
    expected_output2 = pd.DataFrame({
        'age': [56, 69, 46, 32, 60],
        'monthly_income': [221111.0, 96029.0, 19055.0, 53170.0, 244016.0],
        'daily_internet_hours': [6.5, 8.2, 6.4, 6.4, 6.0],
        'smartphone_usage_years': [12.0, 13.0, 4.0, 11.0, 5.0],
        'social_media_hours': [0.7, 2.7, 2.1, 0.7, 0.7],
        'online_payment_trust_score': [1.0, 6.0, 10.0, 2.0, 2.0],
        'tech_savvy_score': [6.0, 9.0, 8.0, 10.0, 5.0],
        'monthly_online_orders': [16, 14, 2, 20, 18],
        'monthly_store_visits': [16, 1, 0, 3, 16],
        'avg_online_spend': [28551.0, 124056.0, 81939.0, 35901.0, 131971.0],
        'shopping_preference': ['store', 'hybrid', 'store', 'store', 'store'],
        'id' : [0,1,2,3,4]
    })

    result = add_id_feature(cleaned_data)
    test2 = expected_output2.compare(result)
    assert test2.empty, f"new data does not match expected output diff:{cleaned_data.compare(test)}"

def test_preprocessing():
    sample_data = pd.read_csv('tests/test_subset.csv')
    cleaned_data,_ = clean_data(sample_data)
    tables = preprocessing(cleaned_data)

    assert {"id","age","monthly_income"}.issubset(tables["customers"].columns), "Customers fail"

    assert {"id","daily_internet_hours","smartphone_usage_years"}.issubset(tables["technology_usage"].columns), "technology_usage fail"
    
    assert {"id","social_media_hours", "online_payment_trust_score", "tech_savvy_score"}.issubset(tables["social_behavior"].columns), "social_behavior fail"
    assert {"id","monthly_online_orders", "monthly_store_visits", "avg_online_spend","shopping_preference"}.issubset(tables["shopping_behavior"].columns), f"shopping_behavior fail got: {tables["shopping_behavior"].columns}"

    assert {"shopping_preference"}.issubset(tables["shopping_preference"].columns), "shopping_preference fail"


def test_upload_to_db():
    assert upload_to_db() == 0