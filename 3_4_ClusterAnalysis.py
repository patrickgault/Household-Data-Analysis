# ------------------------------------------------------------------ #
# Name: Household Data Explorer | Part 3 of 4: Cluster and Outlier Analysis
# Purpose: This script runs three tests for clustering of marked point patterns: LISA 
#          (Anselin Local Moran's I), Optimized Hot Spot Analysis (Getis-Ord Gi*), and Incremental
#          Spatial Autocorrelation. 
# Author: Patrick Gault - FirstLast @ gmail.com
# Created: 2015/11
# License: MIT License
# Requirements: ArcGIS Desktop 10.x, Geostatistical Analyst, Spatial Analyst
# ------------------------------------------------------------------ #

print "Starting Part 3 of 4: Cluster and Outlier Analysis..."

# ---- STEP 1: IMPORT ARCPY, SET ENVIRONMENTS, WORKSPACE ---- #
# Import ArcPy, os, and shutil site packages
import arcpy
import os
import shutil

# Checkout Geostatistical and Spatial Analyst Extensions
arcpy.CheckOutExtension("GeoStats")
arcpy.CheckOutExtension("Spatial") #  The Spatial Analyst Extension is needed to produce one of the optional outputs selected below.

# Set prefix for filenames 
filePrefix = "BGD_" # This should be the 3 letter ISO 3116 code.  For reference, see: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3

# Create new folder as the workspace to store output report documents and overwrite it if it already exists
projectPath = r'\\psf\\Home\\Documents\\Test\\Household_Data_Analysis' #  Add the path to your project folder
folderName = filePrefix + "Cluster_Outlier_Analysis"

if os.path.exists(projectPath + "\\" + folderName):
    shutil.rmtree(projectPath + "\\" + folderName)
os.makedirs(projectPath + "\\" + folderName)

# Set workspace to new folder and add overwrite permissions
arcpy.env.workspace = projectPath + "\\" + folderName
arcpy.env.overwriteOutput = True

# Set the GDB path in order to call data from the GDB
fileGDB = r'\\psf\\Home\\Documents\\Test\\Household_Data_Analysis\\BGD_Data.gdb'  # Add the filepath of the workspace File GDB

# *** Set Spatial Reference using WKID (http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#/Projected_coordinate_systems/02r3000000vt000000/)
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(3106)

# Set Raster Mask
arcpy.env.mask = fileGDB + "\\" + filePrefix + "hhPointsMask" 

# ---- STEP 2: CLUSTER AND OUTLIER ANALYSIS - LISA, OPTIMIZED HOT SPOT, INCREMENTAL SPATIAL AUTOCORRELATION ---- #
try:
    # Local variables for all Cluster and Outlier Analyses
    inputLayer = fileGDB + "\\" + filePrefix + "hhPoints" # This is the household points dataset
    inputField = ["dietDiv", "agshkR"]  # This is the list of field names for the variables used in the Part 2 EBK script
    output = fileGDB + "\\" + filePrefix
   
    # Local variables for Cluster and Outlier Analysis (Anselin Local Moran's I)
    spatialRelationship = "INVERSE_DISTANCE"
    distanceMethod = "EUCLIDEAN_DISTANCE"
    Standardization = "ROW"
    distanceBand = ""
    weightsMatrix = ""
    FDR = "NO_FDR"

    # Local variables for Optimized Hot Spot Analysis:
    dataAggregation = "COUNT_INCIDENTS_WITHIN_FISHNET_POLYGONS"
    boundingBox = arcpy.env.mask
    aggregationPoly = ""
    hotSpotDensitySurface = filePrefix

    # Local variables for Incremental Spatial Autocorrelation:
    numDistanceBands = "20"
    beginningDistance = "5000"
    distanceIncrement = "5000"
    distanceMethod2 = "EUCLIDEAN"
    rowStandardization = "ROW_STANDARDIZATION"
    outputTable = filePrefix
    outputReport = filePrefix

    # Cluster and Outlier Analysis (Anselin Local Morans I)
    print "\t Starting the Cluster and Outlier Analysis..."
    for s in inputField: 
        print "\n\t\t 1 of 5: Doing the LISA for %s..." % s
        arcpy.ClustersOutliers_stats(inputLayer, s, "in_memory\LISA",
                                     spatialRelationship, distanceMethod, Standardization,
                                     distanceBand, weightsMatrix, "NO_FDR")
        print "\n\t\t\t Complete: Finished the LISA for %s!" % s

        # Make a feature layer from the feature class, then select the clusters at the 95% confidence level and copy them to the GDB
        print "\n\t\t\t\t Selecting only clusters that are significant at the 95% level and exporting to the GDB..."
        arcpy.MakeFeatureLayer_management("in_memory\LISA", "LISA")
        arcpy.SelectLayerByAttribute_management("LISA", "NEW_SELECTION", """ 'COType' = 'HH' AND 'COType' = 'LL' """)
        arcpy.CopyFeatures_management("LISA", output + s + "_LISA_95")
        print "\t\t\t\t\t Complete: Finished selecting and exporting the significant clusters"

    # Optimized Hot Spot Analysis
        print "\t\t 2 of 5: Doing the Optimized Hot Spot Analysis for %s..." % s
        arcpy.OptimizedHotSpotAnalysis_stats(inputLayer, output + s + "_hotspot",
                                             s, dataAggregation, boundingBox, aggregationPoly,
                                             hotSpotDensitySurface + s + "_hotSpot")
        print "\t\t\t Complete: Finished the Optimized Hot Spot Analysis for %s!" % s

    # Incremental Spatial Autocorrelation
        print "\t\t 3 of 5: Starting the Incremental Spatial Autocorrelation Analysis..."
        print "\t\t\t Doing Incremental Spatial Autocorrelation Analysis for %s..." % s
        arcpy.IncrementalSpatialAutocorrelation_stats(inputLayer, s, numDistanceBands,
                                                      beginningDistance, distanceIncrement, distanceMethod2,
                                                      rowStandardization, outputTable + s + "_SATable.dbf",
                                                      outputReport + s + "_SAReport.pdf")
        print "\n\t\t\t Complete: Finished the Optimized Hot Spot Analysis for %s!" % s

except:
    # If an error occurred print the message to the screen
    print arcpy.GetMessages()

print "Part 3 of 4: Cluster and Outlier Analysis is complete!"
