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
    cell_list = worksheet.range(f'A2:D{ids}')
    return worksheet.get_all_values(f'A2:E{ids}')

def add_item(length,item):
    worksheet.update_cell(length+1,1,item[0])
    worksheet.update_cell(length+1,2,item[1])
    worksheet.update_cell(length+1,3,item[2])
    worksheet.update_cell(length+1,4,length)
    worksheet.update_cell(length+1, 5, item[3])
    # return item
    
def update_ids():
    ids = len(worksheet.col_values(4))
    cell_list = worksheet.range(f'D2:D{ids}')
    for index, cell in enumerate(cell_list):
        cell.value = index+1
    worksheet.update_cells(cell_list)

def id_find(message):
    cell = worksheet.find(message, in_column=4)
    row = cell.row
    name = worksheet.get(f"A{row}")
    return name[0][0]

