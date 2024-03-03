#!/usr/bin/env python3
from local_file_picker import local_file_picker

from nicegui import ui
import pandas as pd
from pandas.api.types import is_numeric_dtype,is_bool_dtype
import random

df = pd.DataFrame()

async def pick_file() -> None:
    result = await local_file_picker('~', multiple=True)
    #ui.notify(f'You chose {result}')
    #ui.label(result)
    file_choice_label.text = result

    return result

ui.button('Choose file', on_click=pick_file, icon='folder')


file_choice_label = ui.label('Chosen File')


def read_file() -> None:

    # returns a list, so need to get first element
    file_choice = file_choice_label.text
    file_choice = str(file_choice[0])

    
    if file_choice.endswith('.csv'):
        global df
        # read the result of the file picker as a pandas dataframe
        df = pd.read_csv(file_choice)
        update()
        #print(df.head())
        
    else:
        ui.notify("Please choose a csv file")
    
    #return(df)

#ui.button('Read file', icon='dataset', on_click=read_file)

def update():
    table_container.clear()
    with table_container:
        ui.aggrid.from_pandas(df)
        print(df.head())

ui.label('Dataframe')

with ui.element().classes("w-full") as table_container:
    ui.aggrid.from_pandas(df).style("width: 50%;")
ui.button('Read file', icon='dataset', on_click=read_file)
#ui.button('Update', on_click=update)



ui.run()