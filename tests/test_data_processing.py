import unittest
import pandas as pd
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.data_processing import get_processed_data


class TestDataProcessing(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures."""
        # Get the project root directory (one level up from tests/)
        project_root = os.path.dirname(os.path.dirname(__file__))
        self.data_file = os.path.join(project_root, 'data', 'nat2021.csv')

    def test_real_data_processing(self):
        """Test data processing with actual INSEE dataset."""
        # Only run if the actual data file exists
        if not os.path.exists(self.data_file):
            self.skipTest(f"Data file {self.data_file} not found")

        df = get_processed_data(self.data_file)

        # Test basic structure
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty)

        # Test required columns exist
        expected_columns = {'Gender', 'Name', 'Year', 'Count', 'Percentage', 'Total_Count'}
        self.assertTrue(expected_columns.issubset(set(df.columns)))

        # Test data types
        self.assertTrue(pd.api.types.is_numeric_dtype(df['Year']))
        self.assertTrue(pd.api.types.is_numeric_dtype(df['Count']))
        self.assertTrue(pd.api.types.is_numeric_dtype(df['Percentage']))

        # Test INSEE-specific expectations
        self.assertGreaterEqual(df['Year'].min(), 1900)
        self.assertLessEqual(df['Year'].max(), 2025)

        # Test gender standardization
        valid_genders = {'Male', 'Female'}
        self.assertTrue(set(df['Gender'].unique()).issubset(valid_genders))

    def test_data_integrity_with_real_data(self):
        """Test data integrity calculations with actual INSEE data."""
        if not os.path.exists(self.data_file):
            self.skipTest(f"Data file {self.data_file} not found")

        df = get_processed_data(self.data_file)

        # Test percentage calculations on a sample
        sample_df = df.head(100)  # Test first 100 rows for performance

        for _, row in sample_df.iterrows():
            expected_percentage = (row['Count'] / row['Total_Count']) * 100
            self.assertAlmostEqual(expected_percentage, row['Percentage'], places=3)

    def test_known_insee_names_exist(self):
        """Test that known popular French names exist in the dataset."""
        if not os.path.exists(self.data_file):
            self.skipTest(f"Data file {self.data_file} not found")

        df = get_processed_data(self.data_file)

        # Test some names that should definitely exist in French INSEE data
        expected_names = ['MARIE', 'PIERRE', 'JEAN', 'PHILIPPE']
        existing_names = set(df['Name'].unique())

        for name in expected_names:
            self.assertIn(name, existing_names,
                          f"Expected French name '{name}' not found in dataset")


if __name__ == '__main__':
    unittest.main(verbosity=2)
