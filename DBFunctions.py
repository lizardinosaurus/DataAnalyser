import csv
import sqlite3
import os

conn = sqlite3.connect("rawdata.db")
cursor = conn.cursor()

def initialiseDBTable(name):
    """
    create a new DB table with a rowID column

    :param name: will be used as the name for the new table
    """ 
    cursor.execute("DROP TABLE IF EXISTS {}".format(name))
    cursor.execute("""
        CREATE TABLE {}
        (
        rowID INTEGER,
        primary key (rowID))
        """.format(name))

def isInt(value):
    """
    check if a string value is an Integer

    :param value: the string to be checked
    :return: returns True if integer False otherwise
    """ 
    return ((value.startswith("-") and value.replace('-','',1).isdigit() and value.count('-') < 2) or (value.isdigit()))

def isFloat(value):
    """
    check if a string value is a Float

    :param value: the string to be checked
    :return: returns True if float False otherwise
    """ 
    return (value.startswith("-") and value.replace('-','',1).replace('.','',1).isdigit() and value.count('-') < 2 and value.count('.') < 2) or (value.replace('.','',1).isdigit() and value.count('.') < 2)

def createTableList(path):
    """
    create a list from the csv file that will be used to create
    a tables columns. The header is used to get the column names
    and the most common data type from the column is used as the type

    :param path: the path of the csv file
    :return: returns the list is in the form [columnName1, type, columnName2, type...]
    """ 
    with open(os.path.join(path), newline='', encoding='UTF-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        valueCount = []
        for item in header:
            valueCount.append([0,0,0])
        for line in reader:
            for i, item in enumerate(line):
                if (isInt(item)):
                    valueCount[i][0] += 1
                elif (isFloat(item)):
                    valueCount[i][1] += 1
                else:
                    valueCount[i][2] += 1
          
    values = []
    for item in valueCount:
        if ((item[0] + item[1]) > item[2]):
            if (item[1] >= 1):
                values.append("FLOAT")
            else:
                values.append("INTEGER")
        else:
           values.append("TEXT")
           
    return [sub[item] for item in range(len(values))
                      for sub in [header, values]]

def createDBTable(name, path):
    """
    create all columns other than rowID for a DB table

    :param name: the name of the initialised table to add the columns
    :param path: the path of the csv file with the data
    """ 
    tableList = createTableList(path)
    for i in range(0,(len(tableList)),2):
        addColumnToTable(name, tableList[i], tableList[i + 1])


def populateDBTable(name, path):
    """
    insert all the rows from a csv file into a table

    :param name: name of the table to insert the data into
    :param path: the path of the csv file with the data
    """ 
    with open(os.path.join(path), newline='') as f:
        next(f)
        keyID = 0
        reader = csv.reader(f)
        insertRows(name, reader)
    
def loadFile(path, name):
    """
    call all the functions required to load
    the data from a selected csv file into a DB table

    :param path: the path of csv file with the data
    :param name: the name of the table to create
    """ 
    rawPath = r"{}".format(path)
    initialiseDBTable(name) 
    createDBTable(name, rawPath)
    populateDBTable(name, rawPath)

def deleteFile(tables):
    """
    delete 1 or more tables from the database

    :param tables: the list of tables to delete
    """ 
    for table in tables:
        cursor.execute("DROP TABLE IF EXISTS {}".format(table[0].strip(",()\'")))
        conn.commit()

def getColumnType(tableName, columnName):
    """
    get the data type of a requested column

    :param tableName: the name of the table where the column is from
    :param columnName: the name of the column to get the type of
    :return: returns the type of the column as an uppercase string
    """ 
    cursor.execute("SELECT typeof ({}) FROM {}".format(columnName, tableName))
    dataType = str(cursor.fetchall()[0]).strip(",()\'").upper()
    return dataType


def addColumnToTable(tableName, columnName, dataType):
    """
    add a new column to an exisiting table

    :param tableName: the name of the table to add the column to
    :param columnName: the name of the column to add
    :param dataType: the data type of the column to add
    """ 
    cursor.execute("alter table {} add column {} {}".format(tableName, columnName, dataType))

def insertRows(tableName, data):
    """
    insertRows inserts many rows of data into a table

    :param tableName: the name of the table to insert the data
    :param data: the rows of data to insert
    """ 
    keyID = 0
    for items in data:
        items = list(items)
        items.insert(0, keyID)
        itemsString = ",".join(map(lambda item: f'"{item}"', items))
        cursor.execute("INSERT INTO {} VALUES ({})".format(tableName, itemsString))
        conn.commit()
        keyID += 1

def selectColumn(tableName, columnName):
    """
    get all the data from a specific column in a table

    :param tableName: the name of the table where the column is from
    :param columnName: the name of the column to get the data of
    :return: returns all the data from the slected column
    """ 
    cursor.execute('SELECT {} FROM {}'.format(columnName, tableName))
    return cursor.fetchall()



def hasIncorrectData(rowID, columnName, tableName):
    """
    check if an entry in a table is either null
    or does not match the data type of the column

    :param rowID: the row of the entry to check
    :param columnName: the name of the column of the entry to check
    :param tableName: the name of the table the entry is in
    :return: returns True if the data is incorrect and false if not
    """ 
    cursor.execute('SELECT {} FROM {} WHERE rowID={}'.format(columnName, tableName, rowID))
    data = str(cursor.fetchall()[0]).strip(",()\'")
    if (data == ""):
        return True
    elif ((getColumnType(tableName, columnName) == "FLOAT" or "REAL") and (isInt(data) or isFloat(data))):
        return False
    elif ((getColumnType(tableName, columnName) == "INTEGER") and (isInt(data))):
        return False
    elif ((getColumnType(tableName, columnName) == "TEXT")):
        return False
    else:
        return True
    

def condenseColumns(duplicates, columns, oldName, newName):
    """
    Use an SQL group by statement to remove unnecessary 
    columns then condense the remaining rows into a new table

    :param duplicates: the rows which will have duplicate entries
    after removing the columns that will be grouped by
    :param columns: the columns that will be summed in the group by
    :param oldName: the name of the table the values are taken from
    :param newName: the name of the new table that will be created
    """ 
    initialiseDBTable(newName)
    for item in duplicates:
        addColumnToTable(newName, item, getColumnType(oldName, item))
    for item in columns:
        addColumnToTable(newName, item, getColumnType(oldName, item))
    duplicatesString = ",".join([("\"" + str(item) + "\"") for item in duplicates])
    sumColumns = ",".join([("SUM(" + column + ")") for column in columns])
    cursor.execute('SELECT {}, {} FROM {} GROUP BY {}'.format(duplicatesString, sumColumns, oldName, duplicatesString))
    data = cursor.fetchall()
    insertRows(newName, data)


def condenseRows(conditions, conditionColumns, columns, oldName, newName):
    """
    Create a new table using only rows that meet 
    selected conditions

    :param conditions: the values that will be checked in an
    SQL where clause
    :param conditionColumns: the columns that will be checked
    against the conditions in the SQL where clause
    :param columns: all the columns in the original table
    :param oldName: the name of the table the values are taken from
    :param newName: the name of the new table that will be created
    """ 
    initialiseDBTable(newName)
    for item in columns[1:]:
        addColumnToTable(newName, item, getColumnType(oldName, item))
    columnsString = ",".join([("\"" + str(item) + "\"") for item in columns[1:]])
    where = []
    for i in range(len(conditionColumns)):
        where.append(conditionColumns[i])
        where.append("=")
        if isFloat(conditions[i]) or isInt(conditions[i]):
            where.append(conditions[i])
        else:
            where.append("\"")
            where.append(conditions[i])
            where.append("\"")
        if (i+1 != len(conditionColumns)):
            where.append(" AND ")

    whereString = "".join([(str(item)) for item in where])
    cursor.execute('SELECT {} FROM {} WHERE {}'.format(columnsString, oldName, whereString))
    data = cursor.fetchall()
    insertRows(newName, data)

def getColumnNames(table):
    """
    get all the column names in a table

    :param table: the name of the table to get the columns of
    :return: returns a list of column names
    """ 
    columnNames = []
    columns = cursor.execute("SELECT * FROM {}".format(table))
    for column in columns.description: 
        columnNames.append(column[0])
    return columnNames


def cleanByRemovingNull(table, newName):
    """
    remove null values as well as data with incorrect
    type from a table and put the result in a new table

    :param table: the name of the original table with the data
    :param newName: the name of the new table to put the result
    """ 
    initialiseDBTable(newName)
    cursor.execute("SELECT COUNT(*) FROM {}".format(table))
    result = cursor.fetchone()
    row_count = result[0]
    columnNames = getColumnNames(table)
    for item in columnNames:
        if (item != "rowID"):
            addColumnToTable(newName, item, getColumnType(table, item))
    for i in range(0, row_count-1):
        goodRow = True
        for j in range(len(columnNames)):
            if(hasIncorrectData(i, columnNames[j], table)):
                goodRow = False
                row_count -= 1
                break
        if (goodRow):
            cursor.execute("SELECT * FROM {} WHERE rowID={}".format(table, i))
            items = (cursor.fetchall()[0])
            itemsString = ",".join(map(lambda item: f'"{item}"', items))
            cursor.execute("INSERT INTO {} VALUES ({})".format(newName, itemsString))
            conn.commit()