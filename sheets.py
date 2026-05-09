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

# def push_update():
#     worksheet.update_cell(1,2,'Ringo!')
#     worksheet.update_cell(2,1,'Bingo!')

# def get_dic():
#     dictionary = worksheet.get_all_records()
#     print(dictionary)

# def add_shop():
#     f = open('shop.txt','r')
#     global mainshop
#     mainshop = []
#     for line in f:
#         line = line.strip()
#         line = line.split(' , ')
#         line[2] = line[2].replace('\\n','\n')
#         item = {'name':line[0],'price':line[1],'desc':line[2]}
#         mainshop.append(item)
#     f.close()

#     for i in range(len(mainshop)):
#         worksheet.update_cell(i+2,1,mainshop[i]['name'])
#         worksheet.update_cell(i+2,2,mainshop[i]['price'])
#         worksheet.update_cell(i+2,3,mainshop[i]['desc'])
#         worksheet.update_cell(i+2,4,i)

def get_all_values():
    return worksheet.get_all_values()

def add_item(length,item):
    worksheet.update_cell(length+1,1,item[0])
    worksheet.update_cell(length+1,2,item[1])
    worksheet.update_cell(length+1,3,item[2])
    worksheet.update_cell(length+1,4,length-1)
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

# values_list = worksheet.row_values(1)
# print(values_list)