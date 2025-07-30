# KMZ Cleaner and Mobile Compatibility Optimizer

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.6%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Google%20Earth%20Mobile%20%26%20Pro-green.svg)](#)

## Description

`kmz-cleaner.py` is a standalone Python script that processes `.KMZ` and `.ZIP` files containing KML overlays (such as topographic map images), and repackages them into simplified KMZ files optimized for mobile use. These cleaned KMZ files are designed to load correctly in the Google Earth mobile app on iOS and Android.

KMZ files generated with tools like GDAL may display fine in Google Earth Pro on desktop, but often fail to load or display properly on mobile devices due to stricter limitations in KML support. This script resolves that issue.

## Problem This Solves

Google Earth on mobile does not support:
- Region-based `<NetworkLink>` or complex `<Region>` elements
- Unsupported LOD configurations
- Certain GroundOverlay structures that are desktop-friendly

This tool rewrites the KML and rebuilds the KMZ to ensure mobile compatibility.

## Features

- Scans `.KMZ` and `.ZIP` files in the current folder
- Extracts embedded `doc.kml` and image overlay
- Cleans and rewrites the KML:
  - Removes unsupported or unnecessary features
  - Uses a simplified `GroundOverlay` with `LatLonBox`
  - Adds mobile-optimized LOD settings
- Repackages the cleaned files into a new `.KMZ`
- Cleans up temporary folders automatically
- Logs processed files to `processed_kmz/processed_kmz_log.txt`

## Usage

1. Place your `.KMZ` or `.ZIP` files in the same folder as `kmz-cleaner.py`.
2. Run the script using Python 3.6 or later:

Cleaned and mobile-friendly KMZ files will be saved to the processed_kmz/ folder.

Output Example
Each processed KMZ contains:

A cleaned doc.kml

The required map image (e.g. .jpg or .png)

No extra folders, metadata, or unsupported elements

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support This Project

If you find this project helpful, consider supporting my work:

- [Donate via PayPal](https://paypal.me/techbill?country.x=US&locale.x=en_US)
- [Buy Me a Coffee](https://www.buymeacoffee.com/techbill)

Your support helps me maintain and improve this project. Thank you!
