import requests
from bs4 import BeautifulSoup
import re
import folium
import json

def extract_data_table(soup_html, identifier):
    try:
        regex = re.compile(f'.*{identifier}.*')
        if identifier == "vo":
            overview = soup_html.find("div", {"class": "col-lg col-md-6 px-5 px-lg-3 col-vo"})
        else:
            overview = soup_html.find("div", {"class": regex})
        lst = []
        for country in overview.find_all("a"):
            destination = country.find("span", {"class": "country-name"}).text.replace("\n\t\t\t\t\t\t\t\t","").replace("\t\t\t\t\t\t\t","")
            lst.append(destination)
        count_lst = len(lst)
        return count_lst, lst
    except:
        count_lst = 0
        lst = []
        return count_lst, lst

def add_country_to_map(world_map,input_lst, color):
    # Opening JSON file
    f = open('data/countries.geojson')
    # returns JSON object as dictionary
    data = json.load(f)
    if "Timor-Leste" in input_lst:
        input_lst.append("East Timor")
    if "Cote d'Ivoire (Ivory Coast)" in input_lst:
        input_lst.append("Ivory Coast")
    if "Somalia" in input_lst:
        input_lst.append("Somaliland")
    if "Eswatini" in input_lst:
        input_lst.append("Swaziland")
    if "Turkey" in input_lst:
        input_lst.append("Northern Cyprus")
    if "North Macedonia" in input_lst:
        input_lst.append("Macedonia")
    if "Morocco" in input_lst:
        input_lst.append("Western Sahara")
    if "Bahamas" in input_lst:
        input_lst.append("The Bahamas")
    if "Serbia" in input_lst:
        input_lst.append("Republic of Serbia")
    if "Guinea-Bissau" in input_lst:
        input_lst.append("Guinea Bissau")
    if "Congo" in input_lst:
        input_lst.append("Republic of Congo")
    if "Congo (Dem. Rep.)" in input_lst:
        input_lst.append("Democratic Republic of the Congo")
    if "Tanzania" in input_lst:
        input_lst.append("United Republic of Tanzania")
    for country in data["features"]:
        if country["properties"]["ADMIN"] in input_lst:
            add_to_map(world_map, country, color)


def add_to_map(world_map, country, color):
    # Load a GeoJSON file containing the country boundaries
    folium.GeoJson(
        country,
        name='countries',
        style_function=lambda x: {'fillColor': color, 'fillOpacity': 1.0, 'color': 'black', "weight": 0.5}
    ).add_to(world_map)


FIRST_INPUT_URL = "https://visaindex.com/compare/?between=south-korea-passport-ranking"
response = requests.get(FIRST_INPUT_URL)
soup = BeautifulSoup(response.text, "html.parser")
countries = soup.find("div", {"class": "detailedResults container"}).find_all("div", {"class": "detailedResultsCountry"})
country_identifier_lst = []
for country in countries:
    identifier = country.find("span").text
    country_identifier_lst.append(identifier)

for country in country_identifier_lst:
    country_identifier = country
    if country_identifier == "Congo (Dem. Rep.)":
        country_identifier = "congo-dem-rep"
    if country_identifier == "Cote d’Ivoire (Ivory Coast)":
        country_identifier = "cote-divoire-ivory-coast"
    if country_identifier == "Myanmar":
        country_identifier = "myanmar-burma"
    if " " in country_identifier:
        country_identifier = country_identifier.replace(" ", "-")
    SECOND_INPUT_URL = f"https://visaindex.com/country/{country_identifier}-passport-ranking/"
    # Load the world map
    world_map = folium.Map(location=[0, 0], zoom_start=2)
    print(f"*** Extracting information for {country} ***")
    add_country_to_map(world_map, [country], "#000000")
    response = requests.get(SECOND_INPUT_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    country_rank = soup.find("div", {"class": "no display-5 rank"}).text.replace("\n\t\t\t\t\t\t\t","").replace("st ","").replace("nd ","").replace("rd ","").replace("th ","")
    visa_free_destination = soup.find("div", {"class": "no score"}).text.replace("\n\t\t\t\t\t\t\t", "").replace(" Destinations ","")
    print(f"*** Country Rank: {country_rank}, Visa Free Travel: {visa_free_destination} ***")
    country_overview_table = soup.find("div", {"class": "row justify-content-lg-center requirementsLists"})
    # visa free
    visa_free_count, visa_free_lst = extract_data_table(country_overview_table, "vfa")
    add_country_to_map(world_map, visa_free_lst, "#00EA29")
    # visa on arrival
    visa_on_arrival_count, visa_on_arrival_lst = extract_data_table(country_overview_table, "voa")
    add_country_to_map(world_map, visa_on_arrival_lst, "#2900EA")
    # eTA
    eta_count, eta_lst = extract_data_table(country_overview_table, "eta")
    add_country_to_map(world_map, eta_lst, "#9E00EA")
    # visa online
    visa_online_count, visa_online_lst = extract_data_table(country_overview_table, "vo")
    add_country_to_map(world_map, visa_online_lst, "#EA9E00")
    # visa required
    visa_required_count, visa_required_lst = extract_data_table(country_overview_table, "vr")
    add_country_to_map(world_map, visa_required_lst, "#EA2900")
    print(f"*** VF: {visa_free_count}, VOA {visa_on_arrival_count}, ETA {eta_count}, VO {visa_online_count}, VR {visa_required_count} ***")
    # Save the map to an HTML file
    world_map.save(f'world_map_{country}.html')
