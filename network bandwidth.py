#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import osmnx as ox
import osmium
import networkx as nx
import random
import folium
import branca  # For color scales
from folium.plugins import HeatMap  # Import HeatMap plugin

# Read the OSM file with osmium and extract data
class OSMHandler(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.graph = nx.Graph()

    def node(self, n):
        if n.location.valid():
            self.graph.add_node(n.id, lat=n.location.lat, lon=n.location.lon)

    def way(self, w):
        if w.tags.get("highway"):
            nodes = list(w.nodes)
            for i in range(len(nodes) - 1):
                self.graph.add_edge(nodes[i].ref, nodes[i + 1].ref)

# Initialize osmium handler
handler = OSMHandler()

# Apply the handler to an OSM file
osm_file_path = 'E:\\INTERNSHIP(BEL)\\map.osm'  # Adjust path
handler.apply_file(osm_file_path)

# Manually set the CRS for the graph (WGS84)
handler.graph.graph['crs'] = 'EPSG:4326'

# Initialize the map at the center of the region
map_center = [13.06232, 77.57481]  # Adjust based on your region
osm_map = folium.Map(location=map_center, zoom_start=13)

# Extract edge data and add network bandwidth
heatmap_data = []  # List to store heatmap points
bandwidth_values = []  # Store values for scaling

for u, v, data in handler.graph.edges(data=True):
    if 'lat' in handler.graph.nodes[u] and 'lat' in handler.graph.nodes[v]:
        u_lat = handler.graph.nodes[u]['lat']
        u_lon = handler.graph.nodes[u]['lon']
        v_lat = handler.graph.nodes[v]['lat']
        v_lon = handler.graph.nodes[v]['lon']
        
        # Simulate random network bandwidth between 50 Mbps and 100 Mbps
        bandwidth = random.uniform(50, 100)
        bandwidth_values.append(bandwidth)  # Store for scale

        # Calculate the midpoint for heatmap points
        midpoint_lat = (u_lat + v_lat) / 2
        midpoint_lon = (u_lon + v_lon) / 2

        # Store heatmap data (lat, lon, intensity)
        heatmap_data.append([midpoint_lat, midpoint_lon, bandwidth])

# Get min and max bandwidth values
min_bandwidth = min(bandwidth_values)
max_bandwidth = max(bandwidth_values)

# Create and add the heatmap layer
HeatMap(
    heatmap_data,
    min_opacity=0.4,
    max_opacity=0.8,
    radius=20,  # Adjust radius for smooth effect
    blur=15,    # Blur effect for interpolation
).add_to(osm_map)

# Add an RGB color scale for network bandwidth
colormap = branca.colormap.LinearColormap(
    colors=['#0000ff', '#00ffff', '#00ff00', '#ffff00', '#ff0000'],  # Blue → Cyan → Green → Yellow → Red
    vmin=min_bandwidth,
    vmax=max_bandwidth,
    caption="Network Bandwidth (Mbps)"  # Legend title
)
osm_map.add_child(colormap)

# Save the map as an HTML file
osm_map.save("osm_network_bandwidth_heatmap_rgb.html")

# Display the map
osm_map



# In[ ]:




