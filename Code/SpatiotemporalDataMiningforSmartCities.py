#!/usr/bin/env python
# coding: utf-8

# In[2]:


import os
import pandas as pd
import geopandas as gpd
import osmnx as ox
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from shapely.geometry import Point

os.chdir("C:\\Users\\kusha\\OneDrive\\Desktop\\Kushang's Files\\Research Paper DM\\Data\\Research_paper_csv_uid_67196de5-0cf8-43a1-bd74-f5c490a253b9")
os.getcwd()
# Output directory setup
output_dir = "san_jose_osm_outputs"
os.makedirs(output_dir, exist_ok=True)

# Area of interest
place = "San Jose, California, USA"


# In[4]:


import os
import pandas as pd
import geopandas as gpd
import osmnx as ox

# Create output directory
output_dir = "san_jose_osm_cleaned"
os.makedirs(output_dir, exist_ok=True)

# -----------------------------#
# ✅ SOLUTION A: BOUNDING BOX #
# -----------------------------#
print("🔲 Starting BOUNDING BOX download...")

# Bounding Box around central San Jose (adjust if needed)
north, south, east, west = 37.36, 37.30, -121.85, -121.91

# Feature tags to extract
tags_list = [
    ("building", {"building": True}),
    ("healthcare", {"healthcare": True}),
    ("highway", {"highway": True}),
    ("amenity", {"amenity": True})
]

for feature_name, tag in tags_list:
    print(f"📦 Fetching '{feature_name}' via bounding box...")
    try:
        gdf = ox.features_from_bbox(north, south, east, west, tags=tag)
        gdf = gdf[gdf.geometry.notnull()]
        gdf["longitude"] = gdf.geometry.centroid.x
        gdf["latitude"] = gdf.geometry.centroid.y
        filename = os.path.join(output_dir, f"{feature_name}_bbox.csv")
        gdf.to_csv(filename, index=False)
        print(f"✅ Saved {filename} | Records: {len(gdf)}")
    except Exception as e:
        print(f"❌ Failed to fetch {feature_name} via bounding box: {e}")

# --------------------------------------#
# ✅ SOLUTION B: SMALL AREAS BY NAMES  #
# --------------------------------------#
print("\n🏙️ Starting SMALL AREA (neighborhood) downloads...")

# Smaller neighborhoods in San Jose
places = [
    "Willow Glen, San Jose, California, USA",
    "Japantown, San Jose, California, USA",
    "Alum Rock, San Jose, California, USA"
]

for place in places:
    place_key = place.split(',')[0].replace(" ", "_").lower()
    for feature_name, tag in tags_list:
        print(f"📦 Fetching '{feature_name}' for {place}...")
        try:
            gdf = ox.features_from_place(place, tags=tag)
            gdf = gdf[gdf.geometry.notnull()]
            gdf["longitude"] = gdf.geometry.centroid.x
            gdf["latitude"] = gdf.geometry.centroid.y
            filename = os.path.join(output_dir, f"{place_key}_{feature_name}.csv")
            gdf.to_csv(filename, index=False)
            print(f"✅ Saved {filename} | Records: {len(gdf)}")
        except Exception as e:
            print(f"❌ Failed to fetch {feature_name} for {place}: {e}")

print("\n🎉 DONE! All OSM data saved to folder:", output_dir)


# In[5]:


import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium

# Input & output folders
input_dir = "san_jose_osm_cleaned"
output_dir = "visualizations"
os.makedirs(output_dir, exist_ok=True)

# Helper: Load CSV safely
def load_csv_safe(file):
    path = os.path.join(input_dir, file)
    return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()

# ------------------------- #
# 📊 BUILDING TYPE BAR CHART
# ------------------------- #
buildings_df = load_csv_safe("building_bbox.csv")
if not buildings_df.empty and "building" in buildings_df.columns:
    plt.figure(figsize=(10, 6))
    sns.countplot(y="building", data=buildings_df, order=buildings_df["building"].value_counts().iloc[:10].index)
    plt.title("Top 10 Building Types in San Jose (Bounding Box)")
    plt.xlabel("Count")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/building_type_bar.png")
    plt.close()
    print("✅ Saved: building_type_bar.png")
else:
    print("⚠️ Building data not found or missing 'building' column.")

# ------------------------- #
# 📊 HOSPITAL BEDS BOXPLOT
# ------------------------- #
health_df = load_csv_safe("healthcare_bbox.csv")
if not health_df.empty and "beds" in health_df.columns:
    health_df["beds"] = pd.to_numeric(health_df["beds"], errors="coerce")
    beds_df = health_df[health_df["beds"].notnull()]
    if not beds_df.empty:
        plt.figure(figsize=(8, 5))
        sns.boxplot(x=beds_df["beds"])
        plt.title("Distribution of Hospital Bed Counts")
        plt.xlabel("Number of Beds")
        plt.tight_layout()
        plt.savefig(f"{output_dir}/hospital_beds_boxplot.png")
        plt.close()
        print("✅ Saved: hospital_beds_boxplot.png")
    else:
        print("⚠️ No valid 'beds' values to plot.")
else:
    print("⚠️ Healthcare data not found or 'beds' column missing.")

# ------------------------- #
# 📊 AMENITY PIE CHART
# ------------------------- #
amenity_df = load_csv_safe("amenity_bbox.csv")
if not amenity_df.empty and "amenity" in amenity_df.columns:
    top_amenities = amenity_df["amenity"].value_counts().iloc[:6]
    plt.figure(figsize=(7, 7))
    top_amenities.plot.pie(autopct="%1.1f%%")
    plt.title("Top 6 Amenities in San Jose (BBox)")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/amenities_pie_chart.png")
    plt.close()
    print("✅ Saved: amenities_pie_chart.png")
else:
    print("⚠️ Amenity data not found or 'amenity' column missing.")

# ------------------------- #
# 🗺️ BUILDING DENSITY MAP
# ------------------------- #
if not buildings_df.empty:
    m1 = folium.Map(location=[37.33, -121.88], zoom_start=13)
    for _, row in buildings_df.iterrows():
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=2,
            color="blue",
            fill=True,
            fill_opacity=0.4
        ).add_to(m1)
    m1.save(f"{output_dir}/map_building_density.html")
    print("✅ Saved: map_building_density.html")
else:
    print("⚠️ Building data not found for mapping.")

# ------------------------- #
# 🗺️ HEALTHCARE FACILITIES MAP
# ------------------------- #
if not health_df.empty:
    m2 = folium.Map(location=[37.33, -121.88], zoom_start=13)
    for _, row in health_df.iterrows():
        try:
            beds = float(row["beds"]) if not pd.isnull(row["beds"]) else 0
            size = min(max(beds / 20, 3), 15)
        except:
            size = 3
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=size,
            color="red",
            fill=True,
            fill_opacity=0.7,
            popup=f"{row.get('name', 'Unknown')} | Beds: {row.get('beds', 'NA')}"
        ).add_to(m2)
    m2.save(f"{output_dir}/map_healthcare_facilities.html")
    print("✅ Saved: map_healthcare_facilities.html")
else:
    print("⚠️ Healthcare data not found for mapping.")

# ------------------------- #
# 🗺️ AMENITY MARKERS MAP
# ------------------------- #
if not amenity_df.empty:
    m3 = folium.Map(location=[37.33, -121.88], zoom_start=13)
    for _, row in amenity_df.iterrows():
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            popup=row.get("amenity", "Unknown"),
            icon=folium.Icon(color="green", icon="info-sign")
        ).add_to(m3)
    m3.save(f"{output_dir}/map_amenities.html")
    print("✅ Saved: map_amenities.html")
else:
    print("⚠️ Amenity data not found for mapping.")


# In[6]:


import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap

# Folder setup
input_dir = "san_jose_osm_cleaned"
output_dir = "visualizations"
os.makedirs(output_dir, exist_ok=True)

def load_csv_safe(file):
    path = os.path.join(input_dir, file)
    return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()

# ------------------------- #
# 🖼️ Figure 7: Road Density Heatmap
# ------------------------- #
roads_df = load_csv_safe("highway_bbox.csv")
if not roads_df.empty:
    m = folium.Map(location=[37.33, -121.88], zoom_start=13)
    heat_data = roads_df[['latitude', 'longitude']].dropna().values.tolist()
    HeatMap(heat_data, radius=8, blur=12).add_to(m)
    m.save(f"{output_dir}/road_density_heatmap.html")
    print("✅ Saved: road_density_heatmap.html")
else:
    print("⚠️ Road data not available for heatmap.")

# ------------------------- #
# 🖼️ Figure 8: Donut Chart — Public vs Private Operators
# ------------------------- #
df_all = pd.concat([
    load_csv_safe("building_bbox.csv"),
    load_csv_safe("healthcare_bbox.csv"),
    load_csv_safe("amenity_bbox.csv")
], ignore_index=True)

if not df_all.empty and "operator" in df_all.columns:
    df_all["operator"] = df_all["operator"].fillna("Unknown")
    top_operators = df_all["operator"].value_counts().iloc[:5]
    plt.figure(figsize=(6, 6))
    plt.pie(top_operators, labels=top_operators.index, autopct="%1.1f%%", startangle=140)
    centre_circle = plt.Circle((0, 0), 0.70, fc="white")
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    plt.title("Top Facility Operators (Donut Chart)")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/operator_donut_chart.png")
    plt.close()
    print("✅ Saved: operator_donut_chart.png")
else:
    print("⚠️ 'operator' column missing or empty.")

# ------------------------- #
# 🖼️ Figure 5.4: Road Hierarchy Map
# ------------------------- #
if not roads_df.empty:
    m = folium.Map(location=[37.33, -121.88], zoom_start=13)
    color_map = {
        "primary": "red",
        "secondary": "orange",
        "tertiary": "blue",
        "residential": "green",
        "footway": "purple",
        "service": "gray"
    }
    for _, row in roads_df.iterrows():
        color = color_map.get(str(row.get("highway", "")).lower(), "black")
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=1.5,
            color=color,
            fill=True,
            fill_opacity=0.6,
        ).add_to(m)
    m.save(f"{output_dir}/road_type_map.html")
    print("✅ Saved: road_type_map.html")
else:
    print("⚠️ Road data not available for hierarchy map.")

# ------------------------- #
# 🖼️ Figure 5.5: Land Use Map
# ------------------------- #
land_df = load_csv_safe("landuse_bbox.csv")
if not land_df.empty:
    m = folium.Map(location=[37.33, -121.88], zoom_start=13)
    for _, row in land_df.iterrows():
        popup = row.get("landuse", "Unknown")
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=2,
            color="brown",
            fill=True,
            fill_opacity=0.5,
            popup=popup
        ).add_to(m)
    m.save(f"{output_dir}/land_use_map.html")
    print("✅ Saved: land_use_map.html")
else:
    print("⚠️ Land use data not available.")

# ------------------------- #
# 🖼️ Figure 5.6: Spatial Governance Map (by Operator)
# ------------------------- #
if not df_all.empty and "operator" in df_all.columns:
    m = folium.Map(location=[37.33, -121.88], zoom_start=13)
    for _, row in df_all[df_all["operator"].notnull()].iterrows():
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=3,
            color="darkblue",
            fill=True,
            fill_opacity=0.6,
            popup=row["operator"]
        ).add_to(m)
    m.save(f"{output_dir}/operator_markers_map.html")
    print("✅ Saved: operator_markers_map.html")
else:
    print("⚠️ No operator data found for spatial governance map.")

