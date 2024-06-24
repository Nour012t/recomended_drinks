# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 21:40:41 2020

@author: win10
"""

# 1. Library imports
import uvicorn
from fastapi import FastAPI
from BankNotes import BankNote
import numpy as np
import pickle
import pandas as pd
# 2. Create the app object
app = FastAPI()
pickle_in = open("classifier.pkl","rb")
classifier=pickle.load(pickle_in)

# 3. Index route, opens automatically on http://127.0.0.1:8000

@app.post('/predict')
def predict_drink(data:BankNote):
    data = data.dict()
    UserId=data['UserId']
    ProductId=data['ProductId']
    Rating=data['Rating']
    price=data['price']
   # print(classifier.predict([[UserId,ProductId,Rating,price]]))
    prediction = classifier.predict([[UserId,ProductId,Rating,price]])

    
   
    return {
        'prediction': prediction
    }
# 5. Run the API with uvicorn
#    Will run on http://127.0.0.1:8000
if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
    

def process_csv():
    # Read the CSV file
    df = pd.read_csv('DATA.csv')

    # Group the data by UserId
    grouped_data = df.groupby('UserId')

    processed_data = []

    # Iterate over each group
    for user_id, group in grouped_data:
        # Check if the user has ordered more than once
        if len(group) > 1:
            # Calculate the count of each product for the current user
            product_counts = group['ProductName'].value_counts()

            # Find the least ordered drink for the current user
            least_ordered_drink = product_counts.idxmin()

            # Get the indices of orders for the least ordered drink
            drink_indices = group[group['ProductName'] == least_ordered_drink].index

            # Sort the group by order time
            sorted_group = group.loc[drink_indices].sort_values(by='time')

            # Apply a 30% discount to the first occurrence of the least ordered drink
            sorted_group.loc[sorted_group.index[0], 'price'] *= 0.7

            # Update the data for the current user in the original DataFrame
            df.loc[sorted_group.index] = sorted_group

            # Append processed data for the current user
            processed_data.append({"User ID": user_id, "Processed Data": sorted_group.to_dict(orient="records")})

    return processed_data

@app.get("/least_orders offers/")
async def process_data_endpoint():
    processed_data = process_csv()
    return {"processed_data": processed_data}

def process_data():
    # Read the CSV file
    df = pd.read_csv('DATA.csv')

    # Convert 'time' to datetime format
    df['time'] = pd.to_datetime(df['time'])

    # Create a new column for the offer time
    df['offer_time'] = ''

    # Apply discount and calculate new price
    df['new_price'] = df.apply(lambda row: float(row['price']) * 0.7 if (pd.notna(row['price']) and not pd.isna(row['time']) and (('07:00' <= row['time'].strftime('%H:%M') <= '09:00') or ('17:00' <= row['time'].strftime('%H:%M') <= '19:00'))) else None, axis=1)

    # Update the offer time based on the order time
    df.loc[pd.notna(df['new_price']) & ('07:00' <= df['time'].dt.strftime('%H:%M')) & (df['time'].dt.strftime('%H:%M') <= '09:00'), 'offer_time'] = '17:00-19:00'
    df.loc[pd.notna(df['new_price']) & ('17:00' <= df['time'].dt.strftime('%H:%M')) & (df['time'].dt.strftime('%H:%M') <= '19:00'), 'offer_time'] = '07:00-09:00'

    # Create a new DataFrame with the desired columns
    output_df = df[pd.notna(df['new_price'])][['ProductName', 'UserId', 'time', 'offer_time', 'new_price']]

    return output_df.to_dict(orient="records")

@app.get("/offer according time/")
async def process_data_endpoint():
    processed_data = process_data()
    return {"processed_data": processed_data}

#uvicorn app:app --reload
