#!/usr/bin/env python3

import os
import sys
from PIL import Image
import folium
import base64
from datetime import datetime

try:
    arg = sys.argv[1]

    if os.path.isdir(arg):
        parent_directory = os.path.abspath(arg)
    else:
        print("Wrong directory!")
        parent_directory = os.getcwd()
        print("Working in: " + str(parent_directory))
except:
    parent_directory = os.getcwd()
    print("No directory provided, working in: " + str(parent_directory))
    
m = folium.Map(location=[52, 14], zoom_start=6)
counter = 0

for root, dirs, files in os.walk(parent_directory):
    for filename in files:
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
            image_path = os.path.join(root, filename)

            image = Image.open(image_path)
            exif_data = image._getexif()

            if exif_data is not None and 34853 in exif_data:
                gps_info = exif_data[34853]  # 34853 is EXIF tag for GPS information
                latitude = None
                longitude = None

                if 2 in gps_info:  # Latitude and longitude as tuples
                    latitude = gps_info[2][0] + gps_info[2][1] / 60 + gps_info[2][2] / 3600
                    longitude = gps_info[4][0] + gps_info[4][1] / 60 + gps_info[4][2] / 3600
                elif 1 in gps_info:  # Latitude and longitude as decimal values
                    latitude = gps_info[2]
                    longitude = gps_info[4]

                if latitude is not None and longitude is not None:
                    creation_datetime = None
                    if 36867 in exif_data:  # 36867 is the EXIF tag for Date/Time Original
                        creation_datetime = exif_data[36867]
                    
                    # Format the creation date and time
                    formatted_creation_datetime = ""
                    if creation_datetime:
                        try:
                            creation_datetime = datetime.strptime(creation_datetime, "%Y:%m:%d %H:%M:%S")
                            formatted_creation_datetime = creation_datetime.strftime("%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            pass

                    # Add markers for each image's location on the map with photo info and image popup
                    photo_info = f'Photo: {filename}<br>Latitude: {latitude}<br>Longitude: {longitude}'
                    exif_info = f'Creation Date/Time: {formatted_creation_datetime}'
                    
                    # Read and encode the image as base64
                    with open(image_path, "rb") as image_file:
                        image_data = base64.b64encode(image_file.read()).decode()
                    
                    img_popup = f'<img src="file://{image_path}" alt="{filename}" width="700">'
                    popup_content = f'{photo_info}<br>{exif_info}<br><br>{img_popup}'
                    
                    folium.Marker([latitude, longitude], popup=folium.Popup(popup_content, max_width=730)).add_to(m)
                    print(f'Processed: {filename}, Latitude: {latitude}, Longitude: {longitude}')
                    counter += 1
                else:
                    print(f'Skipped: {filename} (Invalid GPS data format)')
            else:
                print(f'Skipped: {filename} (No GPS data found)')

map_path = os.path.join(parent_directory, 'map.html')
if not counter == 0:
    m.save(map_path)
    print('Saved to: ' + str(map_path))
else:
    print("Images without GPS info, no need to create map.")

import webbrowser
webbrowser.open(map_path)
