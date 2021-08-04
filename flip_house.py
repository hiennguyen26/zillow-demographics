#Analysis for a house flip imports, sort by median household income by zip codes, return URL
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
zillow_props.head()

#Checking if the datasets are good
mass_data.head()

#Filter all the adresses with a certain income threshhold by zip codes
def filter_good_props(thresh):
    #Create good props dataframe
    
    rowslist = []
    dict1 = {}
    for index, rowzillow in zillow_props.iterrows():
        #print(prop, row['zip'], row['address'])
        #failsafe zip doesn't exist in the other spreadsheet
        checkzip = rowzillow['zip']
        for index1, rowmassdata in mass_data.iterrows():
            checkzipmass = rowmassdata['zip_code']
            if checkzip != checkzipmass:
                #print("cannot match zip code for: " + rowzillow['address'] + " at price: " + str(rowzillow['price']))
                continue
            else: 
                incomecheck = rowmassdata['median_household_income']
                #if does match, check median household income is below threshhold to evade
                if incomecheck < thresh:
                    print("property is undesired at " + rowzillow['address'] + ', ' + "since it is below the "  + str(thresh) + " income level")
                else:
                    print("found desired property at " + rowzillow['address'] + " at price: " + str(rowzillow['price']) + ", average median income at: " + str(incomecheck))
                    dict1.update(rowzillow)
                    rowslist.append(dict1)
    good_props = pd.DataFrame(rowslist, columns=['address','price','bathrooms','bedrooms','area','zestimate','rent_zestimate','days_on_zillow','property_url','zip'])
    return good_props

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


#Export good props to manual analysis:
filename = r"C:\Users\henry\Desktop\Google Backup\House Flipping\zillowflipping\results\goodprops" + usedate + extension
filter_good_props(75000).to_excel(filename, index=False)








