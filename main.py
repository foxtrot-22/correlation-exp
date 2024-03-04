#!/usr/bin/env python3
from local_file_picker import local_file_picker

from nicegui import ui, Tailwind
import pandas as pd
from pandas.api.types import is_numeric_dtype,is_bool_dtype
from random import random

import json
# import preprocessing from sci-kit learn
from sklearn import preprocessing

# Setup heading
ui.label('Correlation Analysis').tailwind.font_weight('extrabold').font_size('xl')

# setup an empty dataframe for the file read
df = pd.DataFrame()

# setup an empty dataframe for the correlation
corr = pd.DataFrame()

# Setup empty lists for chart_container
chartdata = [{}]
chartlinks=[{}]

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
    global corr

    # get the correlation method
    method = correlation_method.value
    # calculate the correlation
    corr = df.corr(method=method)

    #print(num_vis_columns)    
    show_columns()
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

# create a dropdown from the list of columns in the correlation dataframe
#column_list = list(corr.columns)

# count hte number of columns
#with ui.row():
vis_columns = ui.select([''], value='',label='Select Source Column').style("width: 15%;")
    #vis_inc_columns = ui.select(options=[''], value='', label='Select Target Columns', multiple=True)

vis_tgt_columns = ui.select([''], value='',label='Select Target Columns', multiple=True).style("width: 15%;")

# show the columns from the corr dataframe
def show_columns() -> None:
    # get the columns from the correlation dataframe
    #
    column_list = list(corr.columns)
    ex_column_list = list(corr.columns)
    # update the dropdown
    vis_columns.set_options(column_list, value=column_list[0])
    vis_tgt_columns.set_options(column_list, value=column_list[0])



with ui.element().classes("w-full") as chart_container:
    echart = ui.echart({
    "title": {"text": 'Correlation Visualisation', "subtext": 'Correlation Visualisation of the selected columns'},
    "tooltip": {},
    "animationDurationUpdate": 1500,
    "animationEasingUpdate": 'quinticInOut',
    "series": [
        {
        "type": 'graph',
        #"layout": 'force',
        "layout": 'circular',
        "animation": False,
        "symbolSize": 50,
        "roam": True,
        "draggable": True,
        "force": {
            "initLayout": 'circular',
            "repulsion": 20,
            #"gravity": 0.2,
            "edgeLength": 300
            },
        "label": {
            "show": True
        },
        "edgeSymbol": ['circle', 'arrow'],
        "edgeSymbolSize": [4, 10],
        "edgeLabel": {
            "fontSize": 20
        },
        "data": chartdata,

        "links": chartlinks,
        "lineStyle": {
        "opacity": 0.9,
        "width": 2,
        "curveness": 0
        }
    }
    ]
    }
    ).style("width: 100%; height: 600px;")
    


def visualise() -> None:
    
    # get the source column
    source_column = vis_columns.value
    # get the target columns
    target_columns = vis_tgt_columns.value
    
    # check that target columns is not an empty list or that its not the same as source_column
    if len(target_columns) == 0 or source_column in target_columns:
        ui.notify("Please select more target columns")
        return
    else:
        chartdata = []
        # add the source column to the chart data
        chartdata.append({"name": source_column})
        # add the target columns to the chart data
        for column in target_columns:
            chartdata.append({"name": column})

        # now lets generate the links
        chartlinks = []

        #Lets normalise the dataframe to make the differences bigger
        # This was just a test - doesn't account for -ve due to the abs calc
        corr_norm = corr.abs().apply(lambda x: x/x.max(), axis=0)
        x = corr.values
        min_max_scaler = preprocessing.MinMaxScaler()
        x_scaled = min_max_scaler.fit_transform(x)
        corr_norm = pd.DataFrame(x_scaled, columns=corr.columns, index=corr.index)
        print(chartdata)
        for column in target_columns:
            # get the intersection value of the source and target columns from the corr dataframe
            value = corr.loc[source_column, column]
            #value = corr_norm.loc[source_column, column]
            # added + 5 to get them above 0
            value = int(value*10)+2

            # display negative correlations in red            
            if value == 1:
                color = "#ff0000"
            else:
                color = "#000"
            
            chartlinks.append({
                "source": source_column,
                "target": column,
                "label":{
                    "show":True,
                    "formatter": str(value)
                },
                "symbolSize":[5,20],
                "lineStyle":{
                    "width":value,
                    "curveness": 0.3,
                    "color": f"{color}"
                    }
                
                })
        
        # now we have some json/dict issues so replace all the quotes with double quotes
        # ok so the list elements are all dicts so we need to use json
        
        def replace_quotes(obj):
            if isinstance(obj, dict):
                return {k: replace_quotes(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_quotes(elem) for elem in obj]
            elif isinstance(obj, str):
                return obj.replace("'", "\"")
            else:
                return obj
            
        chartlinks=replace_quotes(chartlinks)
        
        chart_container.clear()
        with chart_container:
            echart = ui.echart({
                "title": {"text": 'Correlation Visualisation', "subtext": 'Correlation Visualisation of the selected columns'},
                "tooltip": {},
                "animationDurationUpdate": 1500,
                "animationEasingUpdate": 'quinticInOut',
                "series": [{
                        "type": 'graph',
                        #"layout": 'none',
                        "draggable": True,
                        "layout": 'circular',
                        "symbolSize": 50,
                        "roam": True,
                        "label": {
                            "show": True
                        },
                        "edgeSymbol": ['circle', 'arrow'],
                        "edgeSymbolSize": [4, 10],
                        "edgeLabel": {
                            "fontSize": 20
                        },
                        "data": chartdata,
                        "links": chartlinks,
                        "lineStyle": {
                            "opacity": 0.9,
                            "width": 2,
                            "curveness": 0
                        }
                    }
                ]
            }).style("width: 100%; height: 250px;")


ui.button('Visualise', on_click=visualise, icon='analytics')

ui.run()