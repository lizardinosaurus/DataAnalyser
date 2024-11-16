import matplotlib.pyplot as plt
import numpy as np
from sklearn import linear_model
from scipy.stats import norm
import DBFunctions as DB

def plotScatter(table, column1, column2):
    """
    Plot a 2d scatter graph

    :param table: the table the axis values will come from
    :param column1: the column to use for the x axis
    :param column2: the column to use for the y axis
    """ 
    x = DB.selectColumn(table, column1)
    y = DB.selectColumn(table, column2)
    plt.scatter(x, y)
    plt.show()

def hotEncode(columnData):
    """
    One-hot encode a 1D array of categorical data.

    :param columnData: the list of items to encode
    :return: returns a list of encoded data
    """
    unique_values = np.unique(columnData)
    encoding = np.zeros((len(columnData), len(unique_values)), dtype=int)

    for i, value in enumerate(columnData):
        encoding[i, np.where(unique_values == value)[0][0]] = 1

    return encoding

def predictValue(columnNames, tableName, predictColumn, userInput):
    """
    predict a value using linear regression based on user inputted data checked
    against existing data

    :param columnNames: the names of the columns that the model will
    be trained with
    :param tableName: the name of the table that contains columnNames
    :param predictColumn: the column name the model will need to predict
    :param userInput: the values the user inputs that will be used
    for their prediction
    :return: returns the predicted value for the userInput
    """ 
    X_data = []
    categoricalColumns = []
    allCategories = [] 

    # Fetch data for each specified column
    for i in range(0, len(columnNames), 2):
        column_name = columnNames[i]
        column_type = columnNames[i + 1]

        # Fetch column data
        column_data = np.array(DB.selectColumn(tableName, column_name))

        if column_type == "float":
            X_data.append(np.array(column_data, dtype=float).reshape(-1, 1))  # Reshape to 2D
        elif column_type == "string":
            categoricalColumns.append(column_data)
            allCategories.append(np.unique(column_data))  # Store unique categories

    # One-hot encode the categorical columns
    for cat_data in categoricalColumns:
        encoded_data = hotEncode(cat_data)
        X_data.append(encoded_data)

    # Create the feature matrix
    X = np.concatenate(X_data, axis=1)

    # Fetch the target variable
    y = np.array(DB.selectColumn(tableName, predictColumn[0]), dtype=float).flatten()

    # Create and train the linear regression model
    regr = linear_model.LinearRegression()
    regr.fit(X, y)

    # Prepare user input for prediction
    user_input_encoded = []

    for i in range(len(userInput)):
        if columnNames[i * 2 + 1] == "string":
            # Initialize one-hot for input with the same size as in training
            one_hot = np.zeros((1, sum(len(cat) for cat in allCategories)), dtype=int)
            unique_values = allCategories[i]  # Use stored unique categories for this column
            
            if userInput[i] in unique_values:
                one_hot[0, np.where(unique_values == userInput[i])[0][0]] = 1
            else:
                raise ValueError(f"Input value '{userInput[i]}' not found in training data.")
            user_input_encoded.append(one_hot)  # Keep as 2D
        elif columnNames[i * 2 + 1] == "float":
            user_input_encoded.append(np.array(float(userInput[i])).reshape(1, 1))  # Reshape to (1, 1)

    # Combine all user inputs into a single array
    input_data = np.concatenate(user_input_encoded, axis=1)


    # Check if the input_data shape matches the training model
    if input_data.shape[1] != X.shape[1]:
        raise ValueError(f"User input has {input_data.shape[1]} features, but model expects {X.shape[1]}.")

    return regr.predict(input_data)

def calcMean(data):
    """
    Calculate the mean for a set of data.

    :param data: the data set to get the mean
    :return: returns the mean value of data
    """
    total = 0
    for item in data:
        total += float(item[0])
    return total / len(data) 

def calcStandardDeviation(data):
    """
    Calculate the standard deviation of a set of data.

    :param data: the data set to calculate the standard deviation
    :return: return the standard deviation of data
    """
    mean = calcMean(data)
    variance = sum([((float(x[0]) - mean) ** 2) for x in data]) / len(data) 
    return variance ** 0.5 

def getStandardDeviationsOfValue(data, value):
    """
    calculate how many standard deviations a value is from
    the mean of a set of data.

    :param data: the set of data the value is from
    :param value: the value to convert to standard deviations
    :return: returns the amount of standard deviations
    """
    mean = calcMean(data)
    standardDeviation = calcStandardDeviation(data)
    difference = value - mean
    return difference/standardDeviation

def getValueOfStandardDeviation(data, value):
    """
    convert standard deviations to a numerical value 
    from the data set.

    :param data: the set of data the standard deviations are from
    :param value: the amount of standard deviations
    :return: returns the equivelent value from the data
    """
    mean = calcMean(data)
    standardDeviation = calcStandardDeviation(data)
    difference = standardDeviation * value
    return difference + mean

def plotNormalDistribution(data):
    """
    plot a normal distribution of a data set.

    :param data: the set of data to plot the normal distribution
    """
    mean = calcMean(data)
    standardDeviation = calcStandardDeviation(data)
    
    lower_bound = mean - 4 * standardDeviation
    upper_bound = mean + 4 * standardDeviation
    
    if lower_bound < 0 and np.min(data) >= 0:
        lower_bound = 0  
    
    x = np.arange(lower_bound, upper_bound, 0.01 * standardDeviation)
    
    plt.plot(x, norm.pdf(x, mean, standardDeviation))
    plt.show()