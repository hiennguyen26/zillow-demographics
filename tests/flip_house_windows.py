# Analysis for a house flip imports, sort by median household income by zip codes, return URL
import datetime
from numpy import blackman, full, negative
import pandas as pd

zillow_props = pd.read_excel("Scraped Data\Zillow\Properties_Zillow_Jan23_Below800kMiami.xlsx")
mass_data = pd.read_excel("Miami_IncomeByZipDemographics.xlsx")
rent_data = pd.read_excel("Scraped Data\Zillow\Properties_Zillow_Jan23_Rentals800k_Miami.xlsx")
sold_data = pd.read_excel("Scraped Data\Zillow\Properties_Zillow_Jan23_Below800kMiamiSold.xlsx")

# # Filter all the adresses with a certain income threshhold by zip codes
# thresh = 25000


def fix_zip(series):
    return series.astype(str).str.extract('(\d+)', expand=False).str.zfill(5)


mass_data['zip_code'] = fix_zip(mass_data['zip_code'])
del mass_data['geoid']
del mass_data['state_name']

# Correct scraped zillow data set


def correct_zillow_dataset(dataset):
    dataset['zip'] = dataset['address'].str.extract(r'(\d{5}\-?\d{0,4})')
    del dataset['rank']
    del dataset['property_id']
    del dataset['latitude']
    del dataset['longitude']
    del dataset['currency']
    del dataset['sold_date']
    del dataset['is_zillow_owned']
    del dataset['image']
    del dataset['land_area']
    del dataset['listing_type']
    del dataset['broker_name']
    del dataset['input']
    del dataset['listing_url']
    dataset['area'] = dataset['area'].str.replace("sqft", "")
    dataset['$/sqft'] = ""
    dataset['compare_$sqft_sold_inZip'] = ""
    dataset['household_median_income_on_threshold'] = ""
    dataset['most_populated'] = ""
    dataset['second_most_populated'] = ""
    dataset['third_most_populated'] = ""
    dataset['median_age'] = ""
    dataset['median_house_value'] = ""
    dataset['poverty_rate'] = ""
    dataset['unemployment_rate'] = ""
    dataset['rent_zestimate_rentals'] = ""
    dataset['rent_zestimate_sold'] = ""

    return dataset

# Correct scraped zillow data set


def correct_supportingzillow_dataset(dataset):
    dataset['zip'] = dataset['address'].str.extract(r'(\d{5}\-?\d{0,4})')
    del dataset['rank']
    del dataset['property_id']
    del dataset['latitude']
    del dataset['longitude']
    del dataset['currency']
    del dataset['land_area']
    del dataset['sold_date']
    del dataset['is_zillow_owned']
    del dataset['image']
    del dataset['listing_type']
    del dataset['broker_name']
    del dataset['input']
    del dataset['listing_url']
    dataset['area'] = dataset['area'].str.replace("sqft", "")
    return dataset


# Checking if the datasets are good
correct_zillow_dataset(zillow_props)
correct_supportingzillow_dataset(rent_data)
correct_supportingzillow_dataset(sold_data)


# Create good props dataframe
good_props10 = pd.DataFrame()
good_props25 = pd.DataFrame()
good_props40 = pd.DataFrame()
good_props100 = pd.DataFrame()
unwanted_props = pd.DataFrame()
good_props = pd.DataFrame()

# Function to sort hte list by second item of tuple


def Sort_Tuple(tup):
    # reverse = None (Sorts in Ascending order)
    # key is set to sort using second element of
    # sublist lambda has been used
    tup.sort(key=lambda x: x[1], reverse=True)
    return tup

# demographic analysis:


def demographic_analysis(rowzillow, rowmassdata):
    print("--------------Demographic analysis -----------")
    # Racial community analysis:
    white = ("White", rowmassdata['race_and_ethnicity_white'])
    black = ("Black", rowmassdata['race_and_ethnicity_black'])
    asian = ("Asian", rowmassdata['race_and_ethnicity_asian'])
    two = ("Two", rowmassdata['race_and_ethnicity_two'])
    hispanic = ("Hispanic", rowmassdata['race_and_ethnicity_hispanic'])
    islander = ("Islander", rowmassdata['race_and_ethnicity_islander'])
    native = ("Native", rowmassdata['race_and_ethnicity_native'])
    other = ("Other", rowmassdata['race_and_ethnicity_other'])
    racialdemo = [white, black, asian, two, hispanic, islander, native, other]
    sortedracial = Sort_Tuple(racialdemo)
    rowzillow['most_populated'] = str(sortedracial[0][0]) + " at " + str("{:.2f}".format(
        sortedracial[0][1] / rowmassdata['race_and_ethnicity_total'] * 100)) + "%"
    rowzillow['second_most_populated'] = str(sortedracial[1][0]) + " at " + str(
        "{:.2f}".format(sortedracial[1][1] / rowmassdata['race_and_ethnicity_total'] * 100)) + "%"
    rowzillow['third_most_populated'] = str(sortedracial[2][0]) + " at " + str(
        "{:.2f}".format(sortedracial[2][1] / rowmassdata['race_and_ethnicity_total'] * 100)) + "%"
    print("Most populated race in zip code: " + str(sortedracial[0][0]) + " at " + str("{:.2f}".format(
        sortedracial[0][1] / rowmassdata['race_and_ethnicity_total'] * 100)) + r"% of total population")
    print("Second most populated race in zip code: " + str(sortedracial[1][0]) + " at " + str("{:.2f}".format(
        sortedracial[1][1] / rowmassdata['race_and_ethnicity_total'] * 100)) + r"% of total population")
    print("Third most populated race in zip code: " + str(sortedracial[2][0]) + " at " + str("{:.2f}".format(
        sortedracial[2][1] / rowmassdata['race_and_ethnicity_total'] * 100)) + r"% of total population")
    # Median age analysis:
    medianage = rowmassdata['median_age']
    rowzillow['median_age'] = str(medianage)
    print("Median age of zip code is: " + str(medianage) + " years old.")
    priceofhome = rowzillow['price']
    medianvalueofhomes = rowmassdata['median_value_of_owner_occupied_units']
    percentdiffprice = (priceofhome - medianvalueofhomes) / \
        medianvalueofhomes * 100
    # property price is above or below the median value of owner occupied units
    if priceofhome <= medianvalueofhomes:
        rowzillow['median_house_value'] = str(
            "{:.2f}".format(percentdiffprice)) + "%"
        print("Property is priced below the median value of owner occupied units in the zip code by " +
              str("{:.2f}".format(percentdiffprice)) + "%")
    elif priceofhome >= medianvalueofhomes:
        rowzillow['median_house_value'] = str(
            "{:.2f}".format(percentdiffprice)) + "%"
        print("Property is priced above the median value of owner occupied units in the zip code by " +
              str("{:.2f}".format(percentdiffprice)) + "%")
    # property zip code has high percentage of poverty
    povertyrate = rowmassdata['family_poverty_pct']
    unemploymentrate = rowmassdata['unemployment_pct']
    if povertyrate < 10:
        rowzillow['poverty_rate'] = str(
            "{:.2f}".format(povertyrate * 100)) + "%"
        print("Poverty rate is: " +
              str("{:.2f}".format(povertyrate * 100)) + "%")
    elif povertyrate > 10:
        rowzillow['poverty_rate'] = r"Poverty rate is above 10% in zip code"
        print(r"Poverty rate is above 10% in zip code")
    elif povertyrate > 25:
        rowzillow['poverty_rate'] = r"A quarter of the zip code is in poverty"
        print(r"A quarter of the zip code is in poverty")
    elif povertyrate > 50:
        rowzillow['poverty_rate'] = r"You probably do not want this property"
        print(r"You probably do not want this property")
    rowzillow['unemployment_rate'] = str(
        "{:.2f}".format((unemploymentrate * 100)) + "%")
    print("Unemployment rate of zip code is: " +
          str("{:.2f}".format((unemploymentrate * 100)) + "%"))
    return

# Basic Property Analysis:


def property_basic_analysis(row):
    print("Property has " + str(row['bathrooms']) +
          " bathrooms, and " + str(row['bedrooms']) + " bedrooms.")
    print("Area of property: " + str(row['area']) + "sq ft.")
    print("Days on market: " + str(row['days_on_zillow']) + " days.")
    return

# Price per sq feet analysis:


def pricesqfeet_analysis(rowzillow, rowmassdata):
    # TODO:
    # Print sq feet and calculate sqfeet
    housevalue = float(rowzillow['price'])
    livingarea = float(rowzillow['area'])
    if livingarea == 0:
        livingarea = 1
        pricesqfeet = housevalue / livingarea
    else:
        pricesqfeet = housevalue / livingarea
    zipcheck = rowzillow['zip']
    total_sold_persqfeet = 0
    rowzillow['$/sqft'] = "$" + str("{:.0f}".format(pricesqfeet))
    counter_sold = 0
    # Method 1: Compare price per sqfeet with average price per sq feet of sold listings in zip code
    for index, rowsold in sold_data.iterrows():
        sold_housevalue = float(rowsold['price'])
        sold_livingarea = float(rowsold['area'])
        if sold_livingarea == 0:
            continue
        else: 
            sold_pricesqfeet = (sold_housevalue / sold_livingarea)
        if zipcheck == rowsold['zip']:
            total_sold_persqfeet += sold_pricesqfeet
            counter_sold += 1
        else:
            continue
    average_sold_persqfeet = 0
    if counter_sold > 0:
        average_sold_persqfeet = total_sold_persqfeet / counter_sold
    else:
        rowzillow['compare_$sqft_sold_inZip'] = "Cannot find other homes to compare"
        print("Cannot find other homes within the zip code")
    percentage_diff_sold = (pricesqfeet - average_sold_persqfeet) / pricesqfeet
    # Analysis against listed rentals
    if pricesqfeet > average_sold_persqfeet:
        rowzillow['compare_$sqft_sold_inZip'] = \
            str("{:.2f}".format(percentage_diff_sold*100)) + "%"
        print("The property's price per sq feet is higher than average sold's in the area by " +
              str("{:.2f}".format(percentage_diff_sold*100)) + "%")
    else:
        rowzillow['compare_$sqft_sold_inZip'] =  \
            str("{:.2f}".format(percentage_diff_sold*100)) + "%"
        print("The property's price per sq feet is lower than average sold's in the area by " +
              str("{:.2f}".format(percentage_diff_sold*100)) + "%")
    # Method 2: Compare price per sqfeet with average price per sq feet of listings in zip code
    # Method 3: Compare price per sqfeet with average price per sq feet of listings in town
    # Method 3: Compare price per sqfeet with average price per sq feet of listings in Boston
    # Method 4: Compare RENTABLE price per sqfeet with average price per sq feet of listings in zip code
    # Method 5: Compare RENTABLE price per sqfeet with average price per sq feet of listings in town
    return


# take in a zip code and find the percentage change on the average rent of similar house with same configuration in that zip code across datasets
# TODO: Checks for both: Higher by 100% possible, lower by nan% possible
# TODO: Rent zestimates compared to listings dataset
def rent_analysis(row):
    print("--------------Rent Analysis -----------")
    numbedrooms = row['bedrooms']
    numbathrooms = row['bathrooms']
    zipcheck = row['zip']
    rent_zestimate = row['rent_zestimate']
    total_rentals = 0
    counter_rentals = 0
    # find average rent in the same zip code of the same config
    for index, rowrent in rent_data.iterrows():
        if zipcheck == rowrent['zip']:
            if numbathrooms >= rowrent['bathrooms']:
                if numbedrooms >= rowrent['bedrooms']:
                    total_rentals += float(rowrent['price'])
                    counter_rentals += 1
        else:
            continue
    ave_rent_rentals = 0
    # if it finds a rental within the zip code
    if counter_rentals > 0:
        ave_rent_rentals = total_rentals / counter_rentals
    else:
        print("Cannot find other similar rentals for this zip code")
    percentage_diff_rentals = (
        rent_zestimate - ave_rent_rentals) / rent_zestimate
    # Analysis against listed rentals
    if rent_zestimate > ave_rent_rentals:
        rowzillow['rent_zestimate_rentals'] = "Higher by " + \
            str("{:.2f}".format(percentage_diff_rentals*100)) + "%"
        print("The property's rent zestimate is higher than average rentals in the area by " +
              str("{:.2f}".format(percentage_diff_rentals*100)) + "%")
    else:
        rowzillow['rent_zestimate_rentals'] = "Lower by " + \
            str("{:.2f}".format(percentage_diff_rentals*100)) + "%"
        print("The property's rent zestimate is lower than average rentals in the area by " +
              str("{:.2f}".format(percentage_diff_rentals*100)) + "%")

    # find average rent zestimate in the same zip code of the same config for sold properties
    counter_sold = 0
    average_rent_sold = 0
    for index, rowsold in sold_data.iterrows():
        if zipcheck == rowsold['zip']:
            if numbathrooms >= rowsold['bathrooms']:
                if numbedrooms >= rowsold['bedrooms']:
                    average_rent_sold += float(rowsold['rent_zestimate'])
                    counter_sold += 1
        else:
            continue
    ave_rent_sold = 0
    if counter_sold > 0:
        ave_rent_sold = average_rent_sold / counter_sold
    else:
        print("Cannot find other similar sold houses for this zip code")
    percentage_diff_rentsold = (
        rent_zestimate - ave_rent_sold) / rent_zestimate
    # Analysis against sold houses rent zestimates
    if rent_zestimate > ave_rent_sold:
        rowzillow['rent_zestimate_sold'] = "Higher by " + \
            str("{:.2f}".format(percentage_diff_rentsold*100)) + "%"
        print("The property's rent zestimate is higher than average sold rent zestimate in the area by " +
              str("{:.2f}".format(percentage_diff_rentsold*100)) + "%")
        print("----------------------------------------------------------------------")
        print()
    else:
        rowzillow['rent_zestimate_sold'] = "Lower by " + \
            str("{:.2f}".format(percentage_diff_rentsold*100)) + "%"
        print("The property's rent zestimate is lower than average sold rent zestimate in the area by " +
              str("{:.2f}".format(percentage_diff_rentsold*100)) + "%")
        print("----------------------------------------------------------------------")
        print()
        


#####Function to run #####
full_list = []
#Function to scrape everything without threshold. 
# Filtering real estate for loops and insert to worksheets
for index, rowzillow in zillow_props.iterrows():
    #print(prop, row['zip'], row['address'])
    # failsafe zip doesn't exist in the other spreadsheet
    checkzip = rowzillow['zip']
    for index1, rowmassdata in mass_data.iterrows():
        checkzipmass = rowmassdata['zip_code']
        if checkzip == checkzipmass:
            incomecheck = rowmassdata['median_household_income']
            property_basic_analysis(rowzillow)
            # $/sqfeet analysis:
            pricesqfeet_analysis(rowzillow, rowmassdata)
            # Demographic analysis:
            demographic_analysis(rowzillow, rowmassdata)
            rent_analysis(rowzillow)
            full_list.append(rowzillow)


# ######################
# unwanted_list = []
# list_10 = []
# list_25 = []
# list_40 = []
# list_100 = []

# # Filtering real estate for loops and insert to worksheets
# for index, rowzillow in zillow_props.iterrows():
#     #print(prop, row['zip'], row['address'])
#     # failsafe zip doesn't exist in the other spreadsheet
#     checkzip = rowzillow['zip']
#     for index1, rowmassdata in mass_data.iterrows():
#         checkzipmass = rowmassdata['zip_code']
#         if checkzip == checkzipmass:
#             incomecheck = rowmassdata['median_household_income']
#             # if income of zip code is below the threshhold level
#             if incomecheck <= thresh:
#                 rowzillow['household_median_income_on_threshold'] = "[X] Property is undesired at " + \
#                     rowzillow['address'] + ', ' + \
#                     "since it is below the " + str(thresh) + " income level"
#                 print("[X] Property is undesired at " + rowzillow['address'] +
#                       ', ' + "since it is below the " + str(thresh) + " income level")
#                 print()
#                 unwanted_list.append(rowzillow)
#                 # income level is above or equal the threshold.
#                 # if income level is close to 10 percent above the threshhold level
#             else:
#                 percentThresh = ((incomecheck - thresh) / thresh)
#                 if percentThresh <= 0.1:
#                     rowzillow['household_median_income_on_threshold'] = str(
#                         "{:.2f}".format(percentThresh*100))
#                     print("[!] Found desired property at " + rowzillow['address'] + " at price: " + str(rowzillow['price']) +
#                           ", average median income: " + str(incomecheck) + "$ above " + str("{:.2f}".format(percentThresh*100)) + r"% threshold")
#                     property_basic_analysis(rowzillow)
#                     # $/sqfeet analysis:
#                     pricesqfeet_analysis(rowzillow, rowmassdata)
#                     # Demographic analysis:
#                     demographic_analysis(rowzillow, rowmassdata)
#                     rent_analysis(rowzillow)
#                     list_10.append(rowzillow)
#                 # if income level is close to 25 percent above the threshhold level
#                 elif percentThresh <= 0.25:
#                     rowzillow['household_median_income_on_threshold'] = str(
#                         "{:.2f}".format(percentThresh*100))
#                     print("[!!] Found desired property at " + rowzillow['address'] + " at price: " + str(rowzillow['price']) +
#                           ", average median income: " + str(incomecheck) + "$ above " + str("{:.2f}".format(percentThresh*100)) + r"% threshold")
#                     property_basic_analysis(rowzillow)
#                     # $/sqfeet analysis:
#                     pricesqfeet_analysis(rowzillow, rowmassdata)
#                     # Demographic analysis:
#                     demographic_analysis(rowzillow, rowmassdata)
#                     rent_analysis(rowzillow)
#                     list_25.append(rowzillow)
#                 # if income level is close to 40 percent above the threshhold level
#                 elif percentThresh <= 0.40:
#                     rowzillow['household_median_income_on_threshold'] = str(
#                         "{:.2f}".format(percentThresh*100))
#                     print("[!!!] Found desired property at " + rowzillow['address'] + " at price: " + str(rowzillow['price']) +
#                           ", average median income: " + str(incomecheck) + "$ above " + str("{:.2f}".format(percentThresh*100)) + r"% threshold")
#                     property_basic_analysis(rowzillow)
#                     # $/sqfeet analysis:
#                     pricesqfeet_analysis(rowzillow, rowmassdata)
#                     # Demographic analysis:
#                     demographic_analysis(rowzillow, rowmassdata)
#                     rent_analysis(rowzillow)
#                     list_40.append(rowzillow)
#                 # if income level is close to 100 percent above the threshhold level
#                 elif percentThresh <= 1:
#                     rowzillow['household_median_income_on_threshold'] = str(
#                         "{:.2f}".format(percentThresh*100))
#                     print("[!!!!] Found desired property at " + rowzillow['address'] + " at price: " + str(rowzillow['price']) +
#                           ", average median income: " + str(incomecheck) + "$ above " + str("{:.2f}".format(percentThresh*100)) + r"% threshold")
#                     property_basic_analysis(rowzillow)
#                     # $/sqfeet analysis:
#                     pricesqfeet_analysis(rowzillow, rowmassdata)
#                     # Demographic analysis:
#                     demographic_analysis(rowzillow, rowmassdata)
#                     rent_analysis(rowzillow)
#                     list_100.append(rowzillow)
#         else:
#             continue


# unwanted_props = pd.concat(unwanted_list, axis=1).reset_index()
# good_props10 = pd.concat(list_10, axis=1, join='outer').reset_index()
# good_props25 = pd.concat(list_25, axis=1, join='outer').reset_index()
# good_props40 = pd.concat(list_40, axis=1, join='outer').reset_index()
# good_props100 = pd.concat(list_100, axis=1, join='outer').reset_index()

good_props = pd.concat(full_list, axis=1, join='outer').reset_index()


# Datetime
current_date_and_time = datetime.datetime.now()
current_date_and_time_string = str(current_date_and_time)
date = list(current_date_and_time_string)

# TODO: Substring this plz jesus
date[4] = "_"
date[7] = "_"
date[10] = "_"
date[13] = "_"
date[16] = "_"
date[19] = "_"
usedate = "".join(date)
extension = ".xlsx"


# Export good props for manual imagery analysis:
filename = r"C:/Users/henry/Desktop/Google Backup/House Flipping/zillowflipping/results" + usedate + extension
# 3 worksheets separately to income area disparities:
writer = pd.ExcelWriter(filename, engine='xlsxwriter')


# # Saving as workbook
# good_props10.transpose().to_excel(
#     writer, sheet_name='0-10% above Threshold', index=False)
# good_props25.transpose().to_excel(
#     writer, sheet_name='10-25% above Threshold', index=False)
# good_props40.transpose().to_excel(
#     writer, sheet_name='25-40% above Threshold', index=False)
# good_props100.transpose().to_excel(
#     writer, sheet_name='40-100% above Threshold', index=False)
# unwanted_props.transpose().to_excel(writer, sheet_name='Unwanted', index=False)\
    
good_props.transpose().to_excel(
    writer, sheet_name='Analysis', index=False)


zillow_props.to_excel(writer, sheet_name="full_data", index=False)


# save
writer.save()
