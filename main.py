#!/usr/bin/env python3
from local_file_picker import local_file_picker

from nicegui import ui
import pandas as pd
from pandas.api.types import is_numeric_dtype,is_bool_dtype
import random


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
        # read the result of the file picker as a pandas dataframe
        df = pd.read_csv(file_choice)
        print(df.head())
    else:
        ui.notify("Please choose a csv file")
    
    return(df)

ui.button('Read file', icon='dataset', on_click=read_file)

ui.label('Dataframe')



#ui.aggrid(df)
#df = pd.DataFrame(data={'col1': [], 'col2': []})
grid = ui.aggrid(
    {
        "defaultColDef": {"flex": 1},
        "columnDefs": [
            {"headerName": "Name", "field": "name"},
            {"headerName": "Age", "field": "age"},
            {"headerName": "Parent", "field": "parent", "hide": True},
        ],
        "rowData": [],
        "rowSelection": "multiple",
    }
).classes("max-h-40")

class App:
    def __init__(self):
        self.rows = []

    def update(self, df):
        self.rows.clear()
        self.rows.extend(df.to_dict("records"))


app = App()
grid.options["rowData"] = app.rows


def update():
    df = pd.DataFrame(
        [
            {"name": "Alice", "age": random.random(), "parent": "David"},
            {"name": "Bob", "age": random.random(), "parent": "Eve"},
            {"name": "Carol", "age": random.random(), "parent": "Frank"},
        ]
    )
    app.update(df)
    grid.update()


ui.button("Update", on_click=update)

ui.run()