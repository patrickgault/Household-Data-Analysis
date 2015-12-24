# ------------------------------------------------------------------ #
# Name: Household Data Explorer | Part 1 of 4: Data Setup
# Purpose: The purpose of this script is to: 1) import a household survey table with latitude/longitude coordinates;
#          2) create a GIS dataset from the household survey table; 3) buffer the household point locations and clip
#          the buffer to the national boundary (Admin. 0) to create a mask for subsequent analyses.  
# Author: Patrick Gault - FirstLast @ gmail.com
# Created: 2015/11
# License: MIT License
# Requirements: ArcGIS Desktop 10.x, Geostatistical Analyst
# ------------------------------------------------------------------ #

print "Starting Part 1 of 4: Data Setup..."

# ---- STEP 1: IMPORT ARCPY, SET ENVIRONMENTS, WORKSPACE---- #
# Import ArcPy, os, and shutil site packages
import arcpy
import os
import shutil

# Checkout Geostatistical Extension
arcpy.CheckOutExtension("GeoStats")

# Set prefix for filenames
filePrefix = "BGD_"  # This should be the 3 letter ISO 3116 code. For reference, see: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3

# Set Spatial Reference using WKID (http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#/Projected_coordinate_systems/02r3000000vt000000/)
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(3106)  # Use the url to look up the WKID for the appropriate projection in the area of interest.

# Create a new Project Folder
projectPath = r'\\Projects\\YourProjectName'  # Add the path to the location where your project folder should be stored
folderName = filePrefix + "Household_Data_Analysis"  # This is the name of your new project folder
if os.path.exists(projectPath + "\\" + folderName):
    shutil.rmtree(projectPath + "\\" + folderName)
os.makedirs(projectPath + "\\" + folderName)

# Create a GDB in your new project folder
pathLocation = projectPath + "\\" + folderName  # This is the path for your project folder
gdbName = filePrefix + "Data"  # This is the name of the new GDB.  The name uses the three letter country code that you defined above in filePrefix.
arcpy.CreateFileGDB_management(pathLocation, gdbName)

# Set workspace and add overwrite permissions
fileGDB = pathLocation + "\\" + gdbName  # Add the filepath of the workspace File GDB
arcpy.env.workspace = fileGDB
arcpy.env.overwriteOutput = True  # This sets overwrite permissions

# ---- STEP 2: IMPORT DATASETS TO FILE GDB: HOUSEHOLD POINTS AND ADMIN 0 SHAPEFILE ---- #

# Import hh points table to GDB

# Set local variables for importing table and Admin 0 shapefile to GDB to GDB
table = r'\\Projects\\YourProjectName\\Household_Data_Analysis\\hhPoints_table.csv'  # Add the file path for the household points .csv file
inputAdm0 = r'\\Projects\\YourProjectName\\Household_Data_Analysis\\Adm0.shp'  # Add the file path for the Admin 0 shapefile.  This will be used as the clipping feature below.

# Execute Table To Geodatabase
print "\n\t 1 of 5: Importing table to GDB: " + fileGDB
arcpy.CopyRows_management(table, filePrefix + "hhPoints_table")
print "\t\t Complete: Table imported!"

# Execute Feature Class to Geodatabase
print "\n\t 2 of 5: importing Adm0 shapefile to GDB: %s..." % fileGDB
arcpy.CopyFeatures_management(inputAdm0, filePrefix + "Adm0")
print "\t\t Complete: Admin 0 shapefile imported!"

# Make XY Event Layer from hh points and export to GDB

# Set the local variables
print "\n\t 3 of 5: Making XY Event from lat/long in table and exporting to GDB..."
in_Table = filePrefix + "hhPoints_Table"  # Add the location of the input table containing the household points
x_coords = "longitude"  # This is the field heading for the field that contains longitude values
y_coords = "latitude"  # This is the field heading for the field that contains latitude values
out_Layer = filePrefix + "hhPoints_XYEvent"  # This is the name of the XY Event layer
saved_Layer = filePrefix + "hhPoints"  # This the output dataset
# Set the source spatial reference using WKID (http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#/Geographic_ \coordinate_systems/02r300000105000000/)
spRef = arcpy.SpatialReference(4326)  # This refers to the coordinate system that the latitude/longitude values in the table reference.  Use 4326 as the WKID for GCS WGS 1984.

# Make the XY event layer...
arcpy.MakeXYEventLayer_management(in_Table, x_coords, y_coords, out_Layer, spRef, "")
 
# Copy XY event layer to GDB
arcpy.CopyFeatures_management(out_Layer, saved_Layer)
print "\t\t Complete: XY Event Layer exported to GDB as: %s " % saved_Layer

# ---- STEP 3: CREATE HOUSEHOLD POINT BUFFER AND CLIP ADMIN 0 ---- #
# *** Requires User Input ***

# Buffer the Household Points
print "\n\t 4 of 5: Buffering the hh points..."
# Set local variables
bufferInput = filePrefix + "hhPoints"
bufferDistance = "25 Kilometers"  # This parameter should be selected based on testing different buffer distances anddetermining which distance creates the most contiguous surface without leaving isolated households.
bufferOutput = "in_memory\hhPoints_Buffer"
dissolveType = "All"  # This makes the output of the buffer one contiguous shape
arcpy.Buffer_analysis(bufferInput, bufferOutput, bufferDistance, "", "", "All", "")
print "\t\t Complete: The hh points have been buffered!"

# Clip the Household Points
print "\n\t 5 of 5: Clipping the hh points buffer..."

# Set local variables
clipInput = "in_memory\hhPoints_Buffer"
clipFeatures = filePrefix + "Adm0"
clipOutput = filePrefix + "hhPointsMask"  # This mask will be used to define the mask environment setting in subsequent analyses
arcpy.Clip_analysis(clipInput, clipFeatures, clipOutput, "")
print "\t\t Complete: The hh points have been clipped!"

print "Part 1 of 4: Data Setup is complete!"
