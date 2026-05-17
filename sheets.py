import gspread
from google.oauth2.service_account import Credentials


scopes = [
    "https://www.googleapis.com/auth/spreadsheets"
]

creds = Credentials.from_service_account_file("credential.json", scopes=scopes)
client = gspread.authorize(creds)
sheet_id = "1Adk7-3qF98jTOL43Iq5-Hz9z02ytTWII2vHl8-5_8HY"
sheet = client.open_by_key(sheet_id)

worksheet = sheet.sheet1

def get_all_values():
    ids = len(worksheet.col_values(4))
    return worksheet.get_all_values(f'A2:F{ids}')
    #this is simple, just returns all the relevant data as a list of rows. note gives colums A to F which is what we care about



def add_item(length,item):
    worksheet.update_cell(length+1,1,item[0])       #name column
    worksheet.update_cell(length+1,2,item[1])       #price column
    worksheet.update_cell(length+1,3,item[2])       #description column
    worksheet.update_cell(length+1,4,length)        #id column - note this does not take in a value from item
    worksheet.update_cell(length+1,5, item[3])      #stock column
    worksheet.update_cell(length+1,6, 0)            #tier column - automatically makes it 0 so it does not appear on sheet
    #this takes the lsit "item" and adds its values to the correct part of the sheet
    


def update_ids():
    ids = len(worksheet.col_values(4))
    cell_list = worksheet.range(f'D2:D{ids}')
    for index, cell in enumerate(cell_list):
        cell.value = index+1
    worksheet.update_cells(cell_list)
    #this just goes through and updates the id column in the event of row deletion



def string_find(message):
    cell = worksheet.find(message,case_sensitive=False)
    price = worksheet.cell(cell.row, 2)
    return cell, price
    #returns the cell matching the name and the price


def stock_reduce(cell,amount):
    row = cell.row
    tier = int(worksheet.cell(row,6).value)
    if tier == 0:
        return 'tier error'
    stock = worksheet.cell(row,5).value
    if stock == 'Unlimited':
        return 'swag'
    else:
        stock = int(stock)
        if stock < amount:
            return 'stock error'
        elif stock-amount >= 1:
            worksheet.update_cell(row,5,stock-amount)
            return 'all good'
        else:
            worksheet.delete_rows(row)
            return 'all good'
    #first this checks to see if the tier of the item isnt 0 and therefore unavailable for purchase, then it checks if the stock is Unlimited,, if it isnt then it reduces the stock. if there isnt enough stock then it returns an error