import os
from odf.opendocument import load
from odf.table import Table, TableRow, TableCell
import pandas as pd
import numpy as np
def isCellNa(series):
    return pd.isna(series[0])

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

    spot_comp = pd.DataFrame(columns=cluster_composition_columns)
    for row_index, row in enumerate(spot_word_table.getElementsByType(TableRow)[1:]):
        element_weight = float(str(row.getElementsByType(TableCell)[4]))
        if element_weight > 0.4:
            element_num = int(str(row.getElementsByType(TableCell)[1]))
            if element_num == 20:
                spot_comp['Ca2+'] = [element_weight]## need to check how to input NO
            if element_num == 15:
                spot_comp['P3-'] = [element_weight]
            if element_num == 30:
                spot_comp['Zn2+'] = [element_weight]
            if element_num == 11:
                spot_comp['Mg2+'] = [element_weight]

    if not isCellNa(spot_comp['Zn2+']):
        spot_comp['Zn'] = ['Yes']
    else:
        spot_comp['Zn'] = ['No']

    if not isCellNa(spot_comp['P3-']):

        if not isCellNa(spot_comp['Ca2+']):
            spot_comp['Ca&P'] = ['Yes']
            spot_comp['Non-Cap(only Calcium)'] = ['No']
        else:
            spot_comp['Ca&P'] = ['No']
            spot_comp['Non-Cap(only Calcium)'] = ['No']
    else:
        spot_comp['Ca&P'] = ['No']
        if not isCellNa(spot_comp['Ca2+']):
          spot_comp['Non-Cap(only Calcium)'] = ['Yes']


    cal_to_mg_ratio = spot_comp['Ca2+'].iloc[0] / spot_comp['Mg2+'].iloc[0]

    if 1.1 >= cal_to_mg_ratio >= 0.9:
        spot_comp['Ca:Mg =1'] = ['Yes'] # idea - add a threshold for the app
    else:
        spot_comp['Ca:Mg =1'] = ['No']

    return spot_comp

def getSpotIdentification():
    return

def getAnalysedClusterData(file_path):

    spot_tables = getTablesFromWord(file_path)
    analysed_cluster_data = []
    for spot_table_index, spot_table in enumerate(spot_tables):# gets last three tables
        print("Table:", spot_table_index + 1)
        # analysed_cluster_data.append(table)
        print(getSpotCompositionData(spot_table))
    return analysed_cluster_data


def getClusterData(file_path = 'Word Uneditted/sample 11.odt'):
    cluster_data = []
    if isFileValid(file_path):
        cluster_data = getAnalysedClusterData(file_path)
        return cluster_data
    else:
        return cluster_data

#spot and new image identification
getClusterData()

