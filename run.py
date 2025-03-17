import gspread
from google.oauth2.service_account import Credentials
from pprint import pprint

SCOPE = [
"https://www.googleapis.com/auth/spreadsheets",
"https://www.googleapis.com/auth/drive.file",
"https://www.googleapis.com/auth/drive"
]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('love_sandwiches')

def get_sales_data():
	"""
	Get sales data from user
	"""
	while True:
		print('Please enter sales data from last market.')
		print('Data should be six numbers separated by commas.')
		print('Example: 10,20,30,40,50,60\n')

		data_str = input('Enter your data here: ')

		sales_data = data_str.split(',')

		if validate_data(sales_data):
			print('\nData is valid\n')
			break

	return sales_data

def validate_data(values):
	"""
	Validate input values are correct
	"""
	try:
		[int(value) for value in values]
		if len(values) != 6:
			raise ValueError(
			(f'Exactly 6 values must be entered. You entered {len(values)}')
			)
	except ValueError as e:
		print(f'Invalid data: {e}. Please try again.')
		return False

	return True

def update_worksheet(worksheet, data):
	"""
	Update any worksheet with entered/cacluated data
	"""
	print(f'Updating {worksheet} worksheet...\n')
	worksheet_update = SHEET.worksheet(worksheet)
	worksheet_update.append_row(data)
	print(f'{worksheet} worksheet updated successfully.\n')

def calculate_surplus(sales_row):
	"""
	Use sales data and stock data to determine surplus stock for each market day

	Stock - Sales = Surplus
	 - Positive indicates waste
	 - Negative indicates extra made to meet demand
	"""
	print("Calculating surplus data...\n")
	stock = SHEET.worksheet('stock').get_all_values()
	stock_row = stock[-1]
	surplus_data = []

	for stock, sales in zip(stock_row, sales_row):
		surplus = int(stock) - sales
		surplus_data.append(surplus)

	return surplus_data

def get_last_five_sales():
	"""
	Pull the last fives sales values for each sandwich
	"""
	sales = SHEET.worksheet('sales')
	columns = []
	for i in range(1,7):
		column = sales.col_values(i)
		columns.append(column[-5:])

	return columns

def calculate_stock_data(data):
	"""
	Genereates recommendations of stock  levels based on sales
	"""
	print('Calculating stock data...\n')
	new_stock_data = []
	for column in data:
		int_column = [int(num) for num in column]
		average = sum(int_column) / len(int_column)
		stock_num = round(average * 1.1)
		new_stock_data.append(stock_num)

	return new_stock_data

def main():
	"""
	Run all functions of program
	"""
	data = get_sales_data()
	sales_data = [int(num) for num in data]
	update_worksheet('sales', sales_data)
	surplus_data = calculate_surplus(sales_data)
	update_worksheet('surplus', surplus_data)
	sales_columns = get_last_five_sales()
	stock_data = calculate_stock_data(sales_columns)
	update_worksheet('stock', stock_data)

print("Welcome to Love Sandwiches Data Control program.\n")
main()