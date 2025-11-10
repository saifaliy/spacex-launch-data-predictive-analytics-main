# Import required libraries
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from folium.plugins import MousePosition
from folium.features import DivIcon

# Let's mark all the launch sites on a map
# Import the dataset
URL = 'spacex_launch_geo.csv'
spacex_df=pd.read_csv(URL)

# Select relevant sub-columns from the dataframe
# Normalize column names: some CSVs use 'class' (lowercase). Ensure 'Class' exists.
if 'Class' not in spacex_df.columns and 'class' in spacex_df.columns:
	spacex_df = spacex_df.rename(columns={'class': 'Class'})

spacex_df = spacex_df[['Launch Site','Lat','Long','Class']]
launch_sites_df = spacex_df.groupby(['Launch Site'], as_index=False).first()
launch_sites_df = launch_sites_df[['Launch Site','Lat','Long']]
launch_sites_df

# Create a folium Map object
# with an initial center location to be NASA Johnson Space Center at Houston, Texas.
nasa_coordinate = [29.559684888503615, -95.0830971930759]
site_map = folium.Map(location=nasa_coordinate, zoom_start=10)

# Create a blue circle at NASA Johnson Space Center, with a popup label
circle = folium.Circle(nasa_coordinate, radius=1000, color='#d35400', fill=True).add_child(
	folium.Popup('NASA Johnson Space Center')
)
# Create a blue circle at NASA Johnson Space Center's coordinate with a icon showing its name
marker = folium.map.Marker(
    nasa_coordinate,
    # Create an icon as a text label
    icon=DivIcon(
        icon_size=(20,20),
        icon_anchor=(0,0),
        html='<div style="font-size: 12; color:#d35400;"><b>%s</b></div>' % 'NASA JSC',
        )
    )
site_map.add_child(circle)
site_map.add_child(marker)

# Initialize the map
site_map = folium.Map(location=nasa_coordinate, zoom_start=5)
# For each launch site, add a Circle object based on its coordinate (Lat, Long) values. In addition, add Launch site name as a popup label
# Loop through each launch site
for index, site in launch_sites_df.iterrows():
    # Get coordinates and site name
    coordinate = [site['Lat'], site['Long']]
    name = site['Launch Site']

    # Add a Circle around each launch site
    folium.Circle(
        location=coordinate,
        radius=1000,
        color='#000000',
        fill=True
    ).add_child(folium.Popup(name)).add_to(site_map)

    # Add a Marker with a label
    folium.Marker(
        location=coordinate,
        icon=DivIcon(
            icon_size=(20,20),
            icon_anchor=(0,0),
            html=f'<div style="font-size: 12px; color:#d35400;"><b>{name}</b></div>'
        )
    ).add_to(site_map)

# Display the map
site_map

# Mark the success/failed launches for each site on the map
marker_cluster = MarkerCluster().add_to(site_map)
for index, row in spacex_df.iterrows():
    # Get coordinates, site name, and launch outcome
    coordinate = [row['Lat'], row['Long']]
    name = row['Launch Site']
    outcome = 'Success' if row['Class'] == 1 else 'Failure'
    
    # Define marker color based on launch outcome
    marker_color = 'green' if row['Class'] == 1 else 'red'
    
    # Create a marker with a popup
    folium.Marker(
        location=coordinate,
        icon=folium.Icon(color=marker_color),
        popup=f"{name} - {outcome}"
    ).add_to(marker_cluster)
# Display the map
site_map

# Add Mouse Position to the map
formatter = "function(num) {return L.Util.formatNum(num, 5);};"
mouse_position = MousePosition(
    position='topright',
    separator=' Long: ',
    empty_string='NaN',
    lng_first=False,
    num_digits=20,
    prefix='Lat:',
    lat_formatter=formatter,
    lng_formatter=formatter,
)
mouse_position.add_to(site_map)
# Display the map
site_map

# Closest coastline, highway, railway, etc to a launch site
from math import sin, cos, sqrt, atan2, radians

def calculate_distance(lat1, lon1, lat2, lon2):
    # approximate radius of earth in km
    R = 6373.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

# Define nearest coastline points for each launch site
# ACTUAL COASTLINE COORDINATES
coastline_points = {
    'CCAFS LC-40': {'lat': 28.561639, 'lon': -80.567028},
    'CCAFS SLC-40': {'lat': 28.561639, 'lon': -80.567028},
    'KSC LC-39A': {'lat': 28.561639, 'lon': -80.567028},
    'VAFB SLC-4E': {'lat': 34.634528, 'lon': -120.626778}
}

# Get unique launch sites from dataframe
launch_sites = spacex_df[['Launch Site', 'Lat', 'Long']].drop_duplicates()

# For each launch site, calculate distance to coastline
for idx, row in launch_sites.iterrows():
    launch_site_name = row['Launch Site']
    launch_site_lat = row['Lat']
    launch_site_lon = row['Long']
    
    # Get corresponding coastline point
    if launch_site_name in coastline_points:
        coastline_coords = coastline_points[launch_site_name]
        
        # Set up coordinates
        launch_site_coord = [launch_site_lat, launch_site_lon]
        coastline_coord = [coastline_coords['lat'], coastline_coords['lon']]
        
        # Calculate distance
        distance = calculate_distance(
            launch_site_lat, launch_site_lon,
            coastline_coords['lat'], coastline_coords['lon']
        )
        
        print(f"{launch_site_name}: Distance to coastline = {distance:.2f} KM")
        
        # Draw line from launch site to coastline
        folium.PolyLine(
            locations=[launch_site_coord, coastline_coord], 
            color='blue',
            weight=2.5, 
            opacity=1
        ).add_to(site_map)
        
        # Create marker AT THE COASTLINE
        distance_marker = folium.Marker(
            coastline_coord,
            icon=DivIcon(
                icon_size=(20, 20),
                icon_anchor=(0, 0),
                html='<div style="font-size: 12px; color:#d35400;"><b>%s</b></div>' % "{:10.2f} KM".format(distance),
            )
        )
        distance_marker.add_to(site_map)

# Display the map
site_map

# Create a marker with distance to a closest city, railway, highway, etc.
# Draw a line between the marker to the launch site
# Nearest cities to each launch site
nearest_cities = {
    'CCAFS LC-40': {'name': 'Cocoa Beach', 'lat': 28.3200, 'lon': -80.6076},
    'CCAFS SLC-40': {'name': 'Cocoa Beach', 'lat': 28.3200, 'lon': -80.6076},
    'KSC LC-39A': {'name': 'Titusville', 'lat': 28.6122, 'lon': -80.8075},
    'VAFB SLC-4E': {'name': 'Lompoc', 'lat': 34.6391, 'lon': -120.4579}
}

# Nearest railways to each launch site
nearest_railways = {
    'CCAFS LC-40': {'name': 'Florida East Coast Railway', 'lat': 28.4700, 'lon': -80.7200},
    'CCAFS SLC-40': {'name': 'Florida East Coast Railway', 'lat': 28.4700, 'lon': -80.7200},
    'KSC LC-39A': {'name': 'Florida East Coast Railway', 'lat': 28.5800, 'lon': -80.8000},
    'VAFB SLC-4E': {'name': 'Union Pacific Railroad', 'lat': 34.6469, 'lon': -120.50375}
}

# Nearest highways to each launch site
nearest_highways = {
    'CCAFS LC-40': {'name': 'State Road 401', 'lat': 28.5500, 'lon': -80.6200},
    'CCAFS SLC-40': {'name': 'State Road 401', 'lat': 28.5500, 'lon': -80.6200},
    'KSC LC-39A': {'name': 'State Road 405', 'lat': 28.5900, 'lon': -80.6800},
    'VAFB SLC-4E': {'name': 'Highway 1', 'lat': 34.6800, 'lon': -120.5200}
}

# Get unique launch sites from dataframe
launch_sites = spacex_df[['Launch Site', 'Lat', 'Long']].drop_duplicates()

# For each launch site, draw lines to city, railway, and highway
for idx, row in launch_sites.iterrows():
    launch_site_name = row['Launch Site']
    launch_site_lat = row['Lat']
    launch_site_lon = row['Long']
    launch_site_coord = [launch_site_lat, launch_site_lon]
    
    # Draw line to nearest city
    if launch_site_name in nearest_cities:
        city = nearest_cities[launch_site_name]
        city_coord = [city['lat'], city['lon']]
        
        distance = calculate_distance(launch_site_lat, launch_site_lon, city['lat'], city['lon'])
        
        # Green line for cities
        folium.PolyLine(
            locations=[launch_site_coord, city_coord],
            color='green',
            weight=2,
            opacity=0.8
        ).add_to(site_map)
        
        # City marker
        folium.Marker(
            city_coord,
            icon=DivIcon(
                icon_size=(20, 20),
                icon_anchor=(0, 0),
                html='<div style="font-size: 11px; color:#27ae60;"><b>City: %s</b></div>' % "{:.2f} KM".format(distance),
            )
        ).add_to(site_map)
    
    # Draw line to nearest railway
    if launch_site_name in nearest_railways:
        railway = nearest_railways[launch_site_name]
        railway_coord = [railway['lat'], railway['lon']]
        
        distance = calculate_distance(launch_site_lat, launch_site_lon, railway['lat'], railway['lon'])
        
        # Purple line for railways
        folium.PolyLine(
            locations=[launch_site_coord, railway_coord],
            color='purple',
            weight=2,
            opacity=0.8
        ).add_to(site_map)
        
        # Railway marker
        folium.Marker(
            railway_coord,
            icon=DivIcon(
                icon_size=(20, 20),
                icon_anchor=(0, 0),
                html='<div style="font-size: 11px; color:#8e44ad;"><b>Railway: %s</b></div>' % "{:.2f} KM".format(distance),
            )
        ).add_to(site_map)
    
    # Draw line to nearest highway
    if launch_site_name in nearest_highways:
        highway = nearest_highways[launch_site_name]
        highway_coord = [highway['lat'], highway['lon']]
        
        distance = calculate_distance(launch_site_lat, launch_site_lon, highway['lat'], highway['lon'])
        
        # Orange line for highways
        folium.PolyLine(
            locations=[launch_site_coord, highway_coord],
            color='orange',
            weight=2,
            opacity=0.8
        ).add_to(site_map)
        
        # Highway marker
        folium.Marker(
            highway_coord,
            icon=DivIcon(
                icon_size=(20, 20),
                icon_anchor=(0, 0),
                html='<div style="font-size: 11px; color:#e67e22;"><b>Highway: %s</b></div>' % "{:.2f} KM".format(distance),
            )
        ).add_to(site_map)

print("Lines drawn to cities (green), railways (purple), and highways (orange)")
# Display the map
site_map

