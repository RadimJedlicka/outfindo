from geopy.geocoders import Nominatim
import pandas as pd

df = pd.read_csv('dealers.csv')

df['lat'] = df['lat'].astype('str')  
df['lng'] = df['lng'].astype('str')  

lats = df['lat'].to_list()
lngs = df['lng'].to_list()

coordinates = zip(lats, lngs)

# Inicializace geokodéru
geolocator = Nominatim(user_agent="my_app")

# Procházení seznamu souřadnic
for lat, lon in coordinates:
    location = geolocator.reverse(f"{lat}, {lon}")
    print(location.address)
