#Analysis for a house flip imports, sort by median household income by zip codes, return URL
from numpy import blackman, negative
import pandas as pd

zillow_props = pd.read_excel("./Scraped Data/Zillow/Properties_Zillow_Aug2.xlsx")
mass_data = pd.read_excel("Massachusetts_IncomeByZipDemographics.xlsx")

def fix_zip(series):
      return series.astype(str).str.extract('(\d+)', expand=False).str.zfill(5)

mass_data['zip_code'] = fix_zip(mass_data['zip_code'])
del mass_data['geoid']
del mass_data['state_name']

#Checking if the datasets are good

zillow_props['zip'] = zillow_props['address'].str.extract(r'(\d{5}\-?\d{0,4})')
del zillow_props['rank']
del zillow_props['property_id']
del zillow_props['latitude']
del zillow_props['longitude']
del zillow_props['currency']
del zillow_props['land_area']
del zillow_props['sold_date']
del zillow_props['is_zillow_owned']
del zillow_props['image']
del zillow_props['listing_type']
del zillow_props['broker_name']
del zillow_props['input']
del zillow_props['listing_url']
zillow_props['area'] = zillow_props['area'].str.replace("sqft", "")
print(zillow_props.head())

#Checking if the datasets are good
print(mass_data.head())

# #Gotta do traffic analysis
# from googlemaps import GoogleMaps
# gmaps = GoogleMaps(api_key)
# address = '424 Massachusetts Avenue, Boston, MA, 02118'
# directions = gmaps.directions(address, destination)

#Filter all the adresses with a certain income threshhold by zip codes
thresh = 90000
#Create good props dataframe

good_props10 = pd.DataFrame(columns=['address','price','bathrooms','bedrooms','area','zestimate','rent_zestimate','days_on_zillow','property_url','zip'])
good_props25 = pd.DataFrame(columns=['address','price','bathrooms','bedrooms','area','zestimate','rent_zestimate','days_on_zillow','property_url','zip'])
good_props40 = pd.DataFrame(columns=['address','price','bathrooms','bedrooms','area','zestimate','rent_zestimate','days_on_zillow','property_url','zip'])
unwanted_props = pd.DataFrame( columns=['address','price','bathrooms','bedrooms','area','zestimate','rent_zestimate','days_on_zillow','property_url','zip'])

# Function to sort hte list by second item of tuple
def Sort_Tuple(tup): 
  
    # reverse = None (Sorts in Ascending order) 
    # key is set to sort using second element of 
    # sublist lambda has been used 
    tup.sort(key = lambda x: x[1], reverse=True) 
    return tup 

#demographic analysis:
def demographic_analysis(rowzillow, rowmassdata):
    print("--------------Demographic analysis -----------")
    #Racial community analysis:
    white = ("White", rowmassdata['race_and_ethnicity_white'])
    black = ("Black", rowmassdata['race_and_ethnicity_black'])
    asian = ("Asian", rowmassdata['race_and_ethnicity_asian'])
    two = ("Two", rowmassdata['race_and_ethnicity_two'])
    hispanic = ("Hispanic", rowmassdata['race_and_ethnicity_hispanic'])
    islander = ("Islander", rowmassdata['race_and_ethnicity_islander'])
    native = ("Native", rowmassdata['race_and_ethnicity_native'])
    other = ("Other", rowmassdata['race_and_ethnicity_other'])
    racialdemo = [white, black,asian, two, hispanic, islander, native, other]
    sortedracial = Sort_Tuple(racialdemo)
    print("Most populated race in zip code: " + str(sortedracial[0][0]) + " at " + str("{:.2f}".format(sortedracial[0][1] / rowmassdata['race_and_ethnicity_total'] * 100)) + r"% of total population") 
    print("Second most populated race in zip code: " + str(sortedracial[1][0]) + " at " + str("{:.2f}".format(sortedracial[1][1] / rowmassdata['race_and_ethnicity_total'] * 100)) + r"% of total population") 
    print("Third most populated race in zip code: " + str(sortedracial[2][0]) + " at " + str("{:.2f}".format(sortedracial[2][1] / rowmassdata['race_and_ethnicity_total'] * 100)) + r"% of total population") 
    
    #Median age analysis:
    medianage = rowmassdata['median_age']
    print("Median age of zip code is:" + str(medianage) + "years old.")
    priceofhome = rowzillow['price']
    medianvalueofhomes = rowmassdata['median_value_of_owner_occupied_units']
    percentdiffprice = (priceofhome - medianvalueofhomes) / medianvalueofhomes * 100
    #property price is above or below the median value of owner occupied units
    if priceofhome <= medianvalueofhomes:
        print("Property is priced below the median value of owner occupied units in the zip code by " + str("{:.2f}".format(percentdiffprice)) + "%")
    elif priceofhome >= medianvalueofhomes:
        print("Property is priced above the median value of owner occupied units in the zip code by " + str("{:.2f}".format(percentdiffprice)) + "%")
        
    #property zip code has high percentage of poverty
    povertyrate = rowmassdata['family_poverty_pct']
    unemploymentrate = rowmassdata['unemployment_pct']
    if povertyrate < 10:
        print("Poverty rate is: " + str("{:.2f}".format(povertyrate * 100)) + "%")
    elif povertyrate > 10:
        print(r"Poverty rate is above 10% in zip code")
    elif povertyrate > 25:
        print(r"A quarter of the zip code is in poverty")
    elif povertyrate > 50:
        print(r"You probably do not want this property")
    print("Unemployment rate of zip code is: " + str("{:.2f}".format((unemploymentrate * 100)) + "%"))
    print("--------------Demographic analysis end -----------")
    return


#Filtering real estate for loops and insert to worksheets
for index, rowzillow in zillow_props.iterrows():
    #print(prop, row['zip'], row['address'])
    #failsafe zip doesn't exist in the other spreadsheet
    checkzip = rowzillow['zip']
    for index1, rowmassdata in mass_data.iterrows():
        checkzipmass = rowmassdata['zip_code']
        if checkzip != checkzipmass:
            #print("cannot match zip code for: " + rowzillow['address'] + " at price: " + str(rowzillow['price']))
            unwanted_props = unwanted_props.append(rowzillow, ignore_index=True)
            continue
        else: 
            incomecheck = rowmassdata['median_household_income']
            #if income of zip code is below the threshhold level
            if incomecheck <= thresh:
                print("property is undesired at " + rowzillow['address'] + ', ' + "since it is below the "  + str(thresh) + " income level")
                unwanted_props = unwanted_props.append(rowzillow, ignore_index=True)
            else:
                # income level is above or equal the threshold. 
                # if income level is close to 10 percent above the threshhold level
                percentThresh = ((incomecheck - thresh) / thresh)
                if percentThresh <= 0.1:
                    print("[!] Found desired property at " + rowzillow['address'] + " at price: " + str(rowzillow['price']) + ", average median income: " + str(incomecheck) + "$ above " + str("{:.2f}".format(percentThresh*100)) + r"% threshold")
                    print("area of property: " + str(rowzillow['area']))
                    print("days on market: " + str(rowzillow['days_on_zillow']))
                    #Demographic analysis:
                    demographic_analysis(rowzillow, rowmassdata)
                    #Append
                    good_props10 = good_props40.append(rowzillow, ignore_index=True)
                # if income level is close to 25 percent above the threshhold level
                elif percentThresh <= 0.25:
                    print("[!!] Found desired property at " + rowzillow['address'] + " at price: " + str(rowzillow['price']) + ", average median income: " + str(incomecheck) + "$ above " + str("{:.2f}".format(percentThresh*100)) + r"% threshold")
                    print("Area of property: " + str(rowzillow['area']) + "sq ft.")
                    print("Days on market: " + str(rowzillow['days_on_zillow']) + "days.")
                    #Demographic analysis:
                    demographic_analysis(rowzillow, rowmassdata)
                    good_props25 = good_props40.append(rowzillow, ignore_index=True)
                # if income level is close to 40 percent above the threshhold level
                elif percentThresh <= 0.40:
                    print("[!!!] Found desired property at " + rowzillow['address'] + " at price: " + str(rowzillow['price']) + ", average median income: " + str(incomecheck) + "$ above " + str("{:.2f}".format(percentThresh*100)) + r"% threshold")
                    print("area of property: " + str(rowzillow['area']))
                    print("days on market: " + str(rowzillow['days_on_zillow']))
                    #Demographic analysis:
                    demographic_analysis(rowzillow, rowmassdata)
                    good_props40 = good_props40.append(rowzillow, ignore_index=True)
                # if income level is close to 80 percent above the threshhold level
                elif percentThresh <= 0.80:
                    print("[!!!!] Found desired property at " + rowzillow['address'] + " at price: " + str(rowzillow['price']) + ", average median income: " + str(incomecheck) + "$ above " + str("{:.2f}".format(percentThresh*100)) + r"% threshold")
                    print("area of property: " + str(rowzillow['area']))
                    print("days on market: " + str(rowzillow['days_on_zillow']))
                    #Demographic analysis:
                    demographic_analysis(rowzillow, rowmassdata)
                    good_props40 = good_props40.append(rowzillow, ignore_index=True)


    

#Datetime thing
import datetime
import xlsxwriter 
current_date_and_time = datetime.datetime.now()
current_date_and_time_string = str(current_date_and_time)
date = list(current_date_and_time_string)

date[4] = "_"
date[7] = "_"
date[10] = "_"
date[13] = "_"
date[16] = "_"
date[19] = "_"
usedate = "".join(date)
extension = ".xlsx"


#Export good props for manual imagery analysis:

filename = r"C:\Users\henry\Desktop\Google Backup\House Flipping\zillowflipping\results\goodprops" + usedate + extension
#3 worksheets separately to income area disparities:
writer = pd.ExcelWriter(filename,engine='xlsxwriter')


#Saving as workbook
good_props10.to_excel(writer, sheet_name='10 Percent', index=False)
good_props25.to_excel(writer, sheet_name='25 Percent', index=False)
good_props40.to_excel(writer, sheet_name='40 Percent', index=False)
unwanted_props.to_excel(writer, sheet_name='Unwanted', index=False)
zillow_props.to_excel(writer, sheet_name="full_data", index=False)


# save
writer.save()

