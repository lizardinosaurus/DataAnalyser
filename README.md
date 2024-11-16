# DataAnalyser

## Description

### overview

This project aims to be flexibale and allow users to work on any dataset with a variable amount of rows and columns. The program is able to manipulate tables, plot graphs and make predictions using a linear regression model that is compatable with numbers as well as strings.


### how to use
Run the circuit DataMain.py file to start the program. The databse is already loaded with some example datasets that will be used as examples below.
#### Import CSV
Copy and paste the path of the csv you want to import along with the name for the table the data will be imported into.
#### Delete dataset
Select a table and it will be deleted from the database.
#### Clean null values (Should be done before using any other functions)
Select a table and enter a name for a new table. the new table will not contain any rows from the previous table which were null or had incorrect data types. This should be done before using any of the functions below.
#### Condense/remove columns
choose a table which you want to keep only a few columns. Selct the columns that you want to keep in the first box that will run through the SQL Group by, and select columns with data that will be summed together in the second box. Enter a name in the name section and a new table with only the selected columns will be created. 

For example the death rates table contains 'births or deaths', 'year', 'location' and 'amount'. You can use this to remove the location by selecting 'births or deaths' and 'year' as the group by and 'amount' as the values to be summed. 
#### Select specific rows
Choose a table and select the columns that you want to meet certain conditions and enter a name for the new table. Continue and then enter the conditions for each of the columns selected, a new table will be created with only the rows that meet the selected conditions.

For example you can get only the male totals from the powerlifting dataset by selecting column 'sex' and setting the value to 'M'
#### Plot scatter graph
Select a table and select the x and y axis columns to plot a scatter graph. Leave the graph open and plot more axis values to plot different data sets on the same graph.
#### plot normal
Select a column from any table to plot a normal distribution of.
#### predict value
Select a table and select the column that contains the value you want to predict. Then select the columns that contain the values you know. Enter the values you know into the popup and the program will use them to predict a new value.

For example using the 'CrashDataNoNull' table we can start off by slecting 'totalinjuries' as the value we want to predict. Then we can select 'Age_drv1' and 'Weather' to see how weather conditions may effect drivers of a certain age. If we want to see how if effects young drivers we can enter '18' and 'cloudy' into the popup and see the total injuries is slightly higher than if we were to enter '18' and 'clear'.
#### Find equivilent value in different dataset
Assuming both datasets are normally distributed, select the column of the data you know, input the data and select the column of the equivilent value you want to know. The program uses a normal distribution to return an equivielnt value.

For example if A man and a women were both powelifters and wanted to compare their totals to eachother, the man colud select 'totalKG' from the 'MaleTotals' table (created from the powerlifting table using the condense and select rows functions above) and enter his total. Then he could select 'totalKG' from the 'FemaleTotals' table and they would be able to find out the equivilent total for her.



## Getting Started

### Dependencies

* make sure to install all the libraries in the requirements.txt file
* this program was made on windows 11

### Installing and executing

* The program runs from the DataMain.py file and requires all of the python files in the repository as well as the rawdata.db file.
