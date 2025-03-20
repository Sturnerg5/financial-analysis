import pandas as pd
import numpy as np
import os
from datetime import datetime

class FinancialReportGenerator:
    def __init__(self):
        self.data = None
        self.category_mapping = self._create_category_mapping()
    
    def _create_category_mapping(self):
        """
        Create a comprehensive category mapping for transactions
        """
        return {
            # Business Expenses - Plane Connection LLC
            'PLANE CONNECTION': 'Business',
            'PLANE CONNECTION LLC': 'Business',
            'PLANE CONNECT': 'Business',
            'TITAN AVIATION': 'Business',
            'ADP FEES': 'Business',
            'PAYROLL': 'Business',
            
            # Business Expenses - Lumis
            'LUMIS': 'Business',
            'LUMIS INC': 'Business',
            
            # Law School Expenses (New Hampshire specific)
            'LAW SCHOOL': 'Law School',
            'BARBRI': 'Law School',
            'BAR EXAM': 'Law School',
            'LEGAL EDUCATION': 'Law School',
            'WESTLAW': 'Law School',
            'LEXIS': 'Law School',
            
            # Homeschool Expenses
            'HOMESCHOOL': 'Homeschool',
            'CURRICULUM': 'Homeschool',
            'EDUCATIONAL': 'Homeschool',
            'BOOKS & SUPPLIES': 'Homeschool',
            
            # Subscription Services
            'ADOBE': 'Subscription',
            'AMAZON PRIME': 'Subscription',
            'NETFLIX': 'Subscription',
            'HULU': 'Subscription',
            'SPOTIFY': 'Subscription',
            
            # Personal Expenses
            'GROCERIES': 'Personal',
            'RESTAURANTS': 'Personal',
            'ENTERTAINMENT': 'Personal',
            'SHOPPING': 'Personal',
            'UTILITIES': 'Personal',
            
            # Financial Transactions
            'CREDIT CARD PAYMENT': 'Financial',
            'TRANSFER': 'Financial',
            'PAYCHECK': 'Income',
            'INTEREST INCOME': 'Income'
        }
    
    def load_financial_data(self, file_paths):
        """
        Load financial data from multiple CSV files
        
        Parameters:
        file_paths (list): List of paths to CSV files
        """
        all_data = []
        
        for file_path in file_paths:
            try:
                # Read CSV file
                df = pd.read_csv(file_path)
                
                # Standardize column names
                df = self._standardize_columns(df)
                
                # Add source file information
                df['Source_File'] = os.path.basename(file_path)
                
                all_data.append(df)
                print(f"Loaded {file_path} with {len(df)} transactions")
            
            except Exception as e:
                print(f"Error loading {file_path}: {str(e)}")
        
        # Combine all data
        if all_data:
            self.data = pd.concat(all_data, ignore_index=True)
            
            # Convert Date column to datetime
            self.data['Date'] = pd.to_datetime(self.data['Date'], errors='coerce')
            
            # Sort by date
            self.data.sort_values('Date', inplace=True)
            
            # Categorize transactions
            self._categorize_transactions()
            
            print(f"Total transactions loaded: {len(self.data)}")
        else:
            print("No data was loaded.")
    
    def _standardize_columns(self, df):
        """
        Standardize column names across different file types
        """
        # Mapping of potential column variations
        column_mapping = {
            'Date': ['Date', 'Transaction Date', 'Posted Date'],
            'Description': ['Description', 'Original Description'],
            'Amount': ['Amount', 'Transaction Amount']
        }
        
        # Rename columns to standard format
        for std_col, possible_cols in column_mapping.items():
            for col in possible_cols:
                if col in df.columns:
                    df.rename(columns={col: std_col}, inplace=True)
                    break
        
        # Ensure standard columns exist
        for std_col in ['Date', 'Description', 'Amount']:
            if std_col not in df.columns:
                df[std_col] = None
        
        return df
    
    def _categorize_transactions(self):
        """
        Categorize transactions based on predefined mapping
        """
        # Initialize category column
        self.data['Category'] = 'Uncategorized'
        
        # Categorize based on description
        for keyword, category in self.category_mapping.items():
            mask = self.data['Description'].str.upper().str.contains(keyword, na=False)
            self.data.loc[mask, 'Category'] = category
        
        # Special rule for New Hampshire transactions
        self.data.loc[self.data['Description'].str.contains('NH|NEW HAMPSHIRE', case=False, na=False), 'Category'] = 'Law School'
    
    def generate_tax_reports(self, output_folder=None):
        """
        Generate comprehensive tax reports
        
        Parameters:
        output_folder (str, optional): Folder to save reports
        """
        # Create output folder if not specified
        if output_folder is None:
            output_folder = f"tax_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(output_folder, exist_ok=True)
        
        # 1. Detailed Transaction Log
        detailed_log = self.data.copy()
        detailed_log.to_csv(os.path.join(output_folder, 'detailed_transaction_log.csv'), index=False)
        
        # 2. Category Summary
        category_summary = self.data.groupby('Category').agg({
            'Amount': ['count', 'sum']
        }).reset_index()
        category_summary.columns = ['Category', 'Transaction_Count', 'Total_Amount']
        category_summary.to_csv(os.path.join(output_folder, 'category_summary.csv'), index=False)
        
        # 3. Monthly Breakdown
        self.data['Month'] = self.data['Date'].dt.to_period('M')
        monthly_breakdown = self.data.groupby(['Month', 'Category'])['Amount'].agg([
            ('Total_Amount', 'sum'),
            ('Transaction_Count', 'count')
        ]).reset_index()
        monthly_breakdown.to_csv(os.path.join(output_folder, 'monthly_breakdown.csv'), index=False)
        
        # 4. Business Expense Detail
        business_expenses = self.data[self.data['Category'] == 'Business']
        business_expenses.to_csv(os.path.join(output_folder, 'business_expenses.csv'), index=False)
        
        # 5. Tax Preparation Summary
        with open(os.path.join(output_folder, 'tax_summary.txt'), 'w') as f:
            f.write("TAX PREPARATION SUMMARY\n")
            f.write("=======================\n\n")
            f.write(f"Date Range: {self.data['Date'].min()} to {self.data['Date'].max()}\n")
            f.write(f"Total Transactions: {len(self.data)}\n\n")
            
            f.write("CATEGORY BREAKDOWN\n")
            f.write("------------------\n")
            for _, row in category_summary.iterrows():
                f.write(f"{row['Category']}: {row['Transaction_Count']} transactions, ${row['Total_Amount']:,.2f}\n")
        
        print(f"Tax reports generated in {output_folder}")
        return output_folder

# Main execution function
def generate_financial_reports(bank_files, credit_card_files):
    """
    Generate financial reports from bank and credit card files
    
    Parameters:
    bank_files (list): List of bank statement CSV file paths
    credit_card_files (list): List of credit card statement CSV file paths
    
    Returns:
    str: Path to generated reports folder
    """
    # Initialize report generator
    report_generator = FinancialReportGenerator()
    
    # Combine all files
    all_files = bank_files + credit_card_files
    
    # Load financial data
    report_generator.load_financial_data(all_files)
    
    # Generate tax reports
    reports_folder = report_generator.generate_tax_reports()
    
    return reports_folder

# Example usage (modify file paths when running)
if __name__ == "__main__":
    # Replace these with your actual file paths
    bank_files = [
        'bank_statements/bk_download 1.csv',
        'bank_statements/bk_download 3.csv',
        # Add other bank statement files
    ]
    
    credit_card_files = [
        'credit_card_statements/activity.csv',
        'credit_card_statements/activity 1.csv',
        # Add other credit card statement files
    ]
    
    # Generate reports
    reports_folder = generate_financial_reports(bank_files, credit_card_files)
    print(f"Reports generated in: {reports_folder}")
