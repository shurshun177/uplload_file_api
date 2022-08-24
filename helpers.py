import openpyxl


def read_exel(file_name):
    excel_file = openpyxl.load_workbook(file_name)
    values_sheet = excel_file['Sheet1']
    val = values_sheet.cell(row=3, column=2).value
    val = val.replace(',', '')
    return float(val[1:])


if __name__ == '__main__':
    read_exel('test.xlsx')