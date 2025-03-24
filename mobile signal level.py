#!/usr/bin/env python
# coding: utf-8

# In[1]:


import osmnx as ox
import osmium
import networkx as nx
import random
import folium
import branca  # For color scales

# Read the OSM file with osmium and extract data
class OSMHandler(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.graph = nx.Graph()

    def node(self, n):
        # Process nodes (You can extract node data here if needed)
        if n.location.valid():
            self.graph.add_node(n.id, lat=n.location.lat, lon=n.location.lon)

    def way(self, w):
        # Process ways (for example, streets, roads)
        if w.tags.get("highway"):
            nodes = list(w.nodes)
            for i in range(len(nodes) - 1):
                self.graph.add_edge(nodes[i].ref, nodes[i + 1].ref)

# Initialize osmium handler
handler = OSMHandler()

# Apply the handler to an OSM file
osm_file_path = 'E:\\INTERNSHIP(BEL)\\map.osm'  # Adjust the file path
handler.apply_file(osm_file_path)

# Manually set the CRS for the graph (WGS84)
handler.graph.graph['crs'] = 'EPSG:4326'

# Initialize the map at the center of the region
map_center = [13.06232, 77.57481]  # Example: Adjust based on your region
osm_map = folium.Map(location=map_center, zoom_start=13)

# Extract edge data and add signal strength
signal_values = []
edge_data = []

for u, v, data in handler.graph.edges(data=True):
    if 'lat' in handler.graph.nodes[u] and 'lat' in handler.graph.nodes[v]:
        u_lat = handler.graph.nodes[u]['lat']
        u_lon = handler.graph.nodes[u]['lon']
        v_lat = handler.graph.nodes[v]['lat']
        v_lon = handler.graph.nodes[v]['lon']
        
        # Simulate random signal strength between -40dBm and -110dBm for each edge
        signal_strength = random.randint(-110, -40)

        # Store the signal strength for later use in the color scale
        signal_values.append(signal_strength)

        # Calculate the midpoint of the line (for choropleth location)
        midpoint_lat = (u_lat + v_lat) / 2
        midpoint_lon = (u_lon + v_lon) / 2

        # Store edge data (for color-based mapping)
        edge_data.append({
            'lat': midpoint_lat,
            'lon': midpoint_lon,
            'signal_strength': signal_strength,
            'u': u,
            'v': v
        })

# Extract min and max signal strength values for scaling
min_signal = min(signal_values)
max_signal = max(signal_values)

# Create a color scale for the plotted range of signal strengths (for choropleth coloring)
colormap = branca.colormap.LinearColormap(
    colors=['blue', 'green', 'red'],  # Corresponding to values in the map (3 colors)
    vmin=min_signal,  # Minimum signal strength from the data
    vmax=max_signal   # Maximum signal strength from the data
).add_to(osm_map)

# Add a legend for the color scale
colormap.caption = 'Signal Strength (dBm)'
osm_map.add_child(colormap)

# Add edges with signal strength to the map as choropleth-style lines
for edge in edge_data:
    # Map the signal strength to a color (only 3 colors)
    if edge['signal_strength'] > -60:
        color = 'green'  # High signal strength
    elif edge['signal_strength'] > -85:
        color = 'blue'   # Medium signal strength
    else:
        color = 'red'    # Low signal strength

    folium.PolyLine(
        locations=[(handler.graph.nodes[edge['u']]['lat'], handler.graph.nodes[edge['u']]['lon']),
                   (handler.graph.nodes[edge['v']]['lat'], handler.graph.nodes[edge['v']]['lon'])],
        color=color, weight=5, opacity=0.7
    ).add_to(osm_map)

# Save the map as an HTML file
osm_map.save("osm_signal_choropleth_map_3_colors.html")

# Display the map
osm_map


# In[ ]:




