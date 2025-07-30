"""
KMZ Cleaner and Mobile Compatibility Optimizer
Author: Bill Fleming
License: MIT

Description:
-------------
This script processes KMZ and ZIP files containing KML overlays (typically topo map images),
with the goal of making them compatible with the **Google Earth mobile app** on iOS and Android.

Problem Addressed:
-------------------
KMZ overlays that load fine in Google Earth Pro often fail on mobile devices due to:
- Region-based NetworkLink errors
- Strict overlay rendering rules on mobile
- Unsupported LOD or bounding logic

What This Script Does:
-----------------------
✓ Extracts KMZ or ZIP files containing KML with GroundOverlay
✓ Verifies presence of required overlay image
✓ Creates a cleaned, mobile-friendly KML with:
    - Simple LatLonBox bounding
    - Minimized LOD settings
    - No NetworkLink regions
    - Flattened image overlays

✓ Outputs are repackaged into new KMZ files in `processed_kmz/`
✓ Temp files are cleaned automatically

Usage:
-------
Place your KMZ or ZIP files in the same folder as this script and run:
    python custom-kmz-new.py

Tested on:
-----------
- Google Earth mobile (iOS / Android)
- Google Earth Pro (Desktop)
"""

import os
import zipfile
import xml.etree.ElementTree as ET
import shutil

# Set script folder and output paths
SCRIPT_FOLDER = os.path.dirname(os.path.abspath(__file__))  # Set to script's folder
OUTPUT_FOLDER = os.path.join(SCRIPT_FOLDER, "processed_kmz")  # Folder for cleaned KMZs
TEMP_FOLDER = os.path.join(SCRIPT_FOLDER, "temp_extract")  # Temporary extraction folder

# Ensure output folders exist and clean up old files
if os.path.exists(OUTPUT_FOLDER):
    shutil.rmtree(OUTPUT_FOLDER)  # Remove old processed files
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

if os.path.exists(TEMP_FOLDER):
    shutil.rmtree(TEMP_FOLDER)  # Remove old temp folder
os.makedirs(TEMP_FOLDER, exist_ok=True)

def extract_zip(zip_path):
    """Extract a ZIP file containing a KMZ"""
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(TEMP_FOLDER)

def extract_kmz(kmz_path, extract_to):
    """Extract a KMZ file to a folder"""
    with zipfile.ZipFile(kmz_path, "r") as kmz:
        kmz.extractall(extract_to)

def parse_kml(kml_path):
    """Parse the KML file and extract necessary information"""
    tree = ET.parse(kml_path)
    root = tree.getroot()

    # Get map name
    doc_name = root.find(".//{http://www.opengis.net/kml/2.2}name").text

    # Find GroundOverlay section
    ground_overlay = root.find(".//{http://www.opengis.net/kml/2.2}GroundOverlay")
    if ground_overlay is None:
        print(f"❌ No GroundOverlay found in {kml_path}, skipping...")
        return None, None, None

    # Extract map image filename
    image_href = ground_overlay.find(".//{http://www.opengis.net/kml/2.2}Icon/{http://www.opengis.net/kml/2.2}href").text

    # Ensure the image file exists before proceeding
    image_path = os.path.join(os.path.dirname(kml_path), image_href)
    if not os.path.exists(image_path):
        print(f"⚠️ Warning: Missing image file {image_href} for {doc_name}. Skipping...")
        return None, None, None

    # Extract bounding coordinates
    latlonbox = ground_overlay.find(".//{http://www.opengis.net/kml/2.2}LatLonBox")
    north = latlonbox.find("{http://www.opengis.net/kml/2.2}north").text
    south = latlonbox.find("{http://www.opengis.net/kml/2.2}south").text
    east = latlonbox.find("{http://www.opengis.net/kml/2.2}east").text
    west = latlonbox.find("{http://www.opengis.net/kml/2.2}west").text

    return doc_name, image_href, (north, south, east, west)

def create_clean_kml(output_kml, doc_name, image_href, coordinates):
    """Generate a new cleaned KML file with optimized rendering for Google Earth"""
    north, south, east, west = coordinates

    kml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
    <name>{doc_name}</name>
    <open>1</open>

    <GroundOverlay>
        <name>Map</name>
        <drawOrder>100</drawOrder>  <!-- Forces overlay to stay visible on Android -->
        <Icon>
            <href>{image_href}</href>
        </Icon>
        <LatLonBox>
            <north>{north}</north>
            <south>{south}</south>
            <east>{east}</east>
            <west>{west}</west>
        </LatLonBox>
        <Lod>
            <minLodPixels>64</minLodPixels>
            <maxLodPixels>-1</maxLodPixels>
        </Lod>
    </GroundOverlay>

</Document>
</kml>"""

    with open(output_kml, "w", encoding="UTF-8") as f:
        f.write(kml_content)

def repackage_kmz(temp_folder, output_kmz, image_file):
    """Create a new KMZ file with only the cleaned KML and image"""
    with zipfile.ZipFile(output_kmz, "w", zipfile.ZIP_DEFLATED) as kmz:
        kmz.write(os.path.join(temp_folder, "cleaned.kml"), "doc.kml")
        kmz.write(os.path.join(temp_folder, image_file), image_file)

def process_files():
    """Process all ZIP and KMZ files in the folder"""
    log_file = os.path.join(OUTPUT_FOLDER, "processed_kmz_log.txt")

    with open(log_file, "w") as log:
        log.write("Processed KMZ Files:\n")

        print(f"📂 Looking for ZIP and KMZ files in: {SCRIPT_FOLDER}")

        # Step 1: Extract ZIP files first
        for zip_file in os.listdir(SCRIPT_FOLDER):
            if zip_file.lower().endswith(".zip"):
                zip_path = os.path.join(SCRIPT_FOLDER, zip_file)
                print(f"📦 Extracting ZIP: {zip_file}...")
                extract_zip(zip_path)

        print(f"📁 Checking extracted KMZ files in: {TEMP_FOLDER}")

        # Step 2: Process extracted KMZ files
        for kmz_file in os.listdir(TEMP_FOLDER):
            print(f"📌 Found in temp_extract: {kmz_file}")
            if kmz_file.lower().endswith(".kmz"):
                kmz_path = os.path.join(TEMP_FOLDER, kmz_file)
                kmz_extract_folder = os.path.join(TEMP_FOLDER, kmz_file.replace(".kmz", ""))
                os.makedirs(kmz_extract_folder, exist_ok=True)

                print(f"🔍 Processing: {kmz_file}...")

                # Extract KMZ
                extract_kmz(kmz_path, kmz_extract_folder)

                # Locate KML file
                kml_path = os.path.join(kmz_extract_folder, "doc.kml")
                if not os.path.exists(kml_path):
                    print(f"❌ No KML file found in {kmz_file}, skipping...")
                    shutil.rmtree(kmz_extract_folder)
                    continue

                # Parse KML file
                doc_name, image_href, coordinates = parse_kml(kml_path)
                if not doc_name or not image_href:
                    print(f"⚠️ Skipping {kmz_file}: Missing required KML data")
                    shutil.rmtree(kmz_extract_folder)
                    continue  # Skip files with missing data

                print(f"✅ Successfully parsed: {doc_name}")

                # Create a cleaned KML file
                cleaned_kml_path = os.path.join(kmz_extract_folder, "cleaned.kml")
                create_clean_kml(cleaned_kml_path, doc_name, image_href, coordinates)

                # Repackage into a new KMZ file
                output_kmz_path = os.path.join(OUTPUT_FOLDER, kmz_file)
                repackage_kmz(kmz_extract_folder, output_kmz_path, image_href)

                print(f"✅ Processed: {kmz_file} -> {output_kmz_path}")
                log.write(f"{kmz_file} -> {output_kmz_path}\n")  # Log the file processed

                # Cleanup temp extraction folder
                shutil.rmtree(kmz_extract_folder)

    # Cleanup temp_extract folder after all processing is complete
    if os.path.exists(TEMP_FOLDER):
        for root, dirs, files in os.walk(TEMP_FOLDER, topdown=False):
            for file in files:
                try:
                    os.remove(os.path.join(root, file))
                except Exception as e:
                    print(f"⚠️ Warning: Could not delete file {file}: {e}")

            for dir in dirs:
                try:
                    os.rmdir(os.path.join(root, dir))
                except Exception as e:
                    print(f"⚠️ Warning: Could not delete folder {dir}: {e}")

        try:
            shutil.rmtree(TEMP_FOLDER)
            print("🧹 Cleaned up temp_extract/ folder.")
        except Exception as e:
            print(f"⚠️ Warning: Could not remove temp_extract/: {e}")

if __name__ == "__main__":
    process_files()
