#!/usr/bin/env python3
from local_file_picker import local_file_picker

from nicegui import ui, Tailwind
import pandas as pd
from pandas.api.types import is_numeric_dtype,is_bool_dtype
import random

# Setup heading
ui.label('Correlation Analysis').tailwind.font_weight('extrabold').font_size('xl')

# setup an empty dataframe for the file read
df = pd.DataFrame()

# setup an empty dataframe for the correlation
corr = pd.DataFrame()

# create async func to wait while we pick a file
async def pick_file() -> None:
    result = await local_file_picker('~', multiple=True)
    file_choice_label.text = result
    return result

# create a button to choose the file
ui.button('Choose file', on_click=pick_file, icon='folder')

# show the chosen file
file_choice_label = ui.label('Chosen File')

# create a function to read the file and update the table
def read_file() -> None:
    # returns a list, so need to get first element
    # this is probably due to the Multiple=True in the file picker
    # get the file choice
    file_choice = file_choice_label.text
    file_choice = str(file_choice[0])
    if file_choice.endswith('.csv'):
        #make the df available outside the function
        global df
        # read the csv file into a dataframe
        df = pd.read_csv(file_choice)
        # update the table
        update()
    # if its not a csv file, let the user know
    else:
        ui.notify("Please choose a csv file")

# create a function to update the table
def update():
    # clear the table
    table_container.clear()
    # add the table
    with table_container:
        ui.aggrid.from_pandas(df)
        # test we are getting the data
        #print(df.head())

# Add a label
ui.label('Selected Dataframe').tailwind.font_weight('extrabold')

# create a container for the table
with ui.element().classes("w-full") as table_container:
    # add the table
    ui.aggrid.from_pandas(df).style("width: 50%;")

# create a button to read the file
ui.button('Read file', icon='dataset', on_click=read_file)

# Add a separator
ui.separator()

# create a label for the correlation method
ui.label('Correlation Method').tailwind.font_weight('extrabold')

# create a dropdown to select the correlation method
correlation_method = ui.select(options=['pearson', 'kendall', 'spearman'], value='pearson')

# calculate the correlation on df
def calculate_correlation() -> None:
    # get the correlation method
    method = correlation_method.value
    # calculate the correlation
    corr = df.corr(method=method)
    # clear the container
    correlation_results.clear()
    with correlation_results:
        ui.aggrid.from_pandas(corr)
    # show the correlation
    #ui.aggrid.from_pandas(corr)

# create a container for the correlation results
with ui.element().classes("w-full") as correlation_results:
    # add the correlation results
    ui.aggrid.from_pandas(corr).style("width: 50%;")

# create a button to calculate the correlation
ui.button('Calculate Correlation', on_click=calculate_correlation, icon='calculate')

# add a separator
ui.separator()

# create a label for the visualiser
ui.label('Visualiser').tailwind.font_weight('extrabold')


ui.run()