import os
from odf.opendocument import load
from odf.table import Table, TableRow, TableCell
from odf.text import P, Span
from odf.style import Style, TextProperties
import pandas as pd
import re


import numpy as np
def isInThreshold(series,num=0.4):
    return float(series[0]) > num

# def assignDefualtSpotCompositionValues():


def isFileValid(file_path):
    if os.path.exists(file_path):
        print(f"The file {file_path} exists.")
        return True
    else:
        print(f"The file {file_path} does not exist.")
        return False

def getWordTables(file_path):

    doc = load(file_path)
    tables = doc.getElementsByType(Table)
    if tables:
        for table_index, table in enumerate(tables):
            print("Table:", table_index + 1)
            for row_index, row in enumerate(table.getElementsByType(TableRow)):
                row_data = []
                for cell_index, cell in enumerate(row.getElementsByType(TableCell)):
                    print(cell)
                    cell_content = ""
                    for child in cell.childNodes:
                        cell_content += str(child)

                    row_data.append(cell_content)
                # table.append(row_data)
                print(row_data)

def getTablesFromWord(file_path):
    doc = load(file_path)
    return doc.getElementsByType(Table)

def getSpotCompositionData(spot_word_table):
    cluster_composition_columns = [ 'Ca2+', 'P3-', 'Zn2+', 'Mg2+', 'Ca&P',
                       'Non-Cap(only Calcium)', 'Zn', 'Ca:Mg =1']
 # initialize compound values
    # Split columns
    numeric_cols = cluster_composition_columns[:4]
    text_cols = cluster_composition_columns[4:]

    # Create row values
    row_values = [0] * len(numeric_cols) + ['No'] * len(text_cols)

    # Create DataFrame
    spot_comp = pd.DataFrame([row_values], columns=cluster_composition_columns)

    for row_index, row in enumerate(spot_word_table.getElementsByType(TableRow)[1:]):
        element_weight = float(str(row.getElementsByType(TableCell)[4]))

        element_num = int(str(row.getElementsByType(TableCell)[1]))
        if element_num == 20:
            spot_comp['Ca2+'] = [element_weight]## need to check how to input NO
        if element_num == 15:
            spot_comp['P3-'] = [element_weight]
        if element_num == 30:
            spot_comp['Zn2+'] = [element_weight]
        if element_num == 12:
            spot_comp['Mg2+'] = [element_weight]

    if isInThreshold(spot_comp['Zn2+']):
        spot_comp['Zn'] = ['Yes']

    if  isInThreshold(spot_comp['P3-']):

        if isInThreshold(spot_comp['Ca2+']):
            spot_comp['Ca&P'] = ['Yes']
    else:
        if isInThreshold(spot_comp['Ca2+']):
          spot_comp['Non-Cap(only Calcium)'] = ['Yes']

          if isInThreshold(spot_comp['Mg2+']):
            cal_to_mg_ratio = spot_comp['Ca2+'].iloc[0] / spot_comp['Mg2+'].iloc[0]

            if 1.1 >= cal_to_mg_ratio >= 0.9:
                spot_comp['Ca:Mg =1'] = ['Yes'] # idea - add a threshold for the app


    return spot_comp

def getText(file_path):
    doc = load(file_path)
    all_text = []

    # Loop through all paragraphs and spans to extract the text
    for paragraph in doc.getElementsByType(P):
        for span in paragraph.getElementsByType(Span):
            if span.firstChild:  # Ensure the span has text content
                all_text.append(span.firstChild.data)

    return "\n".join(all_text)

def getSpotNumbers():
    numbers = re.findall(r'(\d+)\.\s*Spot', getText('Word Uneditted/sample 11.odt'))  # \d+ matches one or more digits
    print(numbers)
    return numbers


def getAnalysedClusterData(file_path):

    spot_tables = getTablesFromWord(file_path)
    analysed_cluster_data = []
    for spot_table_index, spot_table in enumerate(spot_tables[:]):# gets last three tables
        print("Table:", spot_table_index + 1)
        analysed_cluster_table = getSpotCompositionData(spot_table)
        result_series = analysed_cluster_table.iloc[0]
        analysed_cluster_data.append(result_series)
        print(result_series)
    return pd.DataFrame(analysed_cluster_data)


def getClusterData(file_path = 'Word Uneditted/sample 11.odt'):
    cluster_data = []
    if isFileValid(file_path):
        cluster_data = getAnalysedClusterData(file_path)
        return cluster_data
    else:
        return cluster_data

def isExcelFileOpen(file_path):
    try:
        with open(file_path, 'r+b'):
            print("File is not open in Excel.")
    except PermissionError:
        raise Exception("The Excel file is currently open. Please close it and try again.")
    except FileNotFoundError:
        raise Exception("The file does not exist.")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {e}")

def createClusterExcel():
    file_path = 'output.xlsx'
    try:
        isExcelFileOpen(file_path)
        getClusterData().to_excel(file_path, index=False)
        print("Success :)")
    except Exception as e:
        print(f"Caught an error: {e}")

createClusterExcel()