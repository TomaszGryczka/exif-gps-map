#!/usr/bin/env python3

import os
from PIL import Image
import folium
import base64

# Step 1: Get the current working directory
current_directory = os.getcwd()

# Step 2: Create a folium map
m = folium.Map(location=[0, 0], zoom_start=2)  # Initial map with a default location

# Step 3: Recursively traverse through all subdirectories and process images
for root, dirs, files in os.walk(current_directory):
    for filename in files:
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
            image_path = os.path.join(root, filename)

            # Step 4: Load and process each image
            image = Image.open(image_path)
            exif_data = image._getexif()

            print('8888888888888888888888888888888888888888888888888888')
            print(exif_data)

            # Check if EXIF data exists and contains GPS information
            if exif_data is not None and 34853 in exif_data:
                gps_info = exif_data[34853]  # 34853 is the EXIF tag for GPS information
                latitude = None
                longitude = None

                # Some GPS data structures store latitude and longitude differently
                if 2 in gps_info:  # Latitude and longitude as tuples
                    latitude = gps_info[2][0] + gps_info[2][1] / 60 + gps_info[2][2] / 3600
                    longitude = gps_info[4][0] + gps_info[4][1] / 60 + gps_info[4][2] / 3600
                elif 1 in gps_info:  # Latitude and longitude as decimal values
                    latitude = gps_info[2]
                    longitude = gps_info[4]

                if latitude is not None and longitude is not None:
                    # Step 5: Add markers for each image's location on the map with photo info and image popup
                    photo_info = f'Photo: {filename}<br>Latitude: {latitude}<br>Longitude: {longitude}'

                    # Read and encode the image as base64
                    with open(image_path, "rb") as image_file:
                        image_data = base64.b64encode(image_file.read()).decode()

                    img_popup = f'<img src="data:image/jpeg;base64,{image_data}" alt="{filename}" width="300">'
                    popup_content = f'{photo_info}<br><br>{img_popup}'

                    folium.Marker([latitude, longitude], popup=folium.Popup(popup_content, max_width=350)).add_to(m)
                    print(f'Processed: {filename}, Latitude: {latitude}, Longitude: {longitude}')
                else:
                    print(f'Skipped: {filename} (Invalid GPS data format)')
            else:
                print(f'Skipped: {filename} (No GPS data found)')

# Step 6: Save the map to an HTML file
m.save('map.html')

# Open the map in your default web browser
import webbrowser
webbrowser.open('map.html')
