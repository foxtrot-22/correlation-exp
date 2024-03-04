import pandas as pd
from sklearn.datasets import load_diabetes
import seaborn as sns
import matplotlib.pyplot as plt

 
# Load the dataset with frame
df = load_diabetes(as_frame=True)
# conver into pandas dataframe
df = df.frame

# export to csv
df.to_csv('diabetes.csv', index=False)
# Print first 5 rows
corr = df.corr(method='pearson')
print(corr)

