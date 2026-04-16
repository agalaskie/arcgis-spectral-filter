Spectral Filter ArcGIS Tool

A Python-based ArcGIS tool for filtering raster data using user-defined spectral intensity thresholds. The tool allows users to isolate pixels within specified band value ranges.

Requirements:

- ArcGIS Pro (with arcpy installed)
- Python environment managed by ArcGIS Pro
- Input multispectral raster images

Steps:

1. Copy the `.pyt` file into a known folder.
2. Open ArcGIS Pro.
3. Go to the Analysis tab
4. Click Tools 
5. Click the Toolboxes tab
6. Click Add Toolbox
7. Navigate to your `.pyt` file and select it
8. The toolbox will appear in the list
9. load your raster dataset
10. Select the Spectral Filter Tool
11. Configure parameters:
- Input Raster: The raster you want to analyze
- Band: Select the target band (e.g., Band 1, Band 2, etc.)
- Minimum Threshold: Minimum spectral intesity for selected band
- Maximum Threshold: Maximum spectral intesity for selected band
- Output Raster: Path for the filtered result
12. Run the tool

