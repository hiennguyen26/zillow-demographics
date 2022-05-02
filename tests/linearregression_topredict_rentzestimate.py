import statsmodels.api as sm
from statsmodels.discrete.discrete_model import Probit
import pandas as pd
import numpy as np
from statsmodels.regression.linear_model import OLS

#Needs a separate numerical file to analyse

def run_model(df):
    df.columns = list(map(lambda name: name.lower(), df.columns))
    variables = ["address","price","bathrooms","bedrooms","area", "zestimate",  "days_on_zillow",	"$/sqft",	"household_median_income_on_threshold",	"most_populated","second_most_populated","third_most_populated",
                 "median_age", "median_house_value"	,"poverty_rate"	, "unemployment_rate",	"rent_zestimate_rentals","rent_zestimate_sold"]
    y = df["rent_zestimate"]
    X = sm.tools.add_constant(df[variables])
    model = OLS(y, X)
    print(model.fit(cov_type='HC0').summary())

df = pd.read_excel(
    './results/ZillowAnalysis_Threshold95K_Aug18.xlsx')   

run_model(df)





