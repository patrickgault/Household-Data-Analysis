# ------------------------------------------------------------------ #
# Name: Household Data Explorer | Part 2 of 4: Empirical Bayesian Kriging (EBK)
# Purpose: The purpose of this script is to: 1) Create an interpolated surface for variables of interest;
#          2) Create a standard error surface for variables of interest.
# Author: Patrick Gault - FirstLast @ gmail.com
# Created: 2015/11
# License: MIT License
# Requirements: ArcGIS Desktop 10.x, Geostatistical Analyst
# ------------------------------------------------------------------ #

print "Starting Part 2 of 4: Empirical Bayesian Kriging..."

# ---- STEP 1: IMPORT ARCPY, SET ENVIRONMENTS, WORKSPACE ---- #
# Import ArcPy site package
import arcpy

# Checkout Geostatistical Extension
arcpy.CheckOutExtension("GeoStats")

# Set workspace and add overwrite permissions
fileGDB = r'\\Projects\\YourProjectName\\Household_Data_Analysis\\YourGDB'  # Add the filepath of the workspace File GDB
arcpy.env.workspace = fileGDB
arcpy.env.overwriteOutput = True

# Set prefix for filenames
filePrefix = "BGD_"  # This should be the 3 letter ISO 3116 code.  For reference, see: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3
 
# *** Set Spatial Reference using WKID
# http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#/Projected_coordinate_systems/02r3000000vt000000/
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(3106)

# Set Raster Mask
arcpy.env.mask = filePrefix + "hhPointsMask" 


# ---- STEP 2: EMPIRICAL BAYESIAN KRIGING (EBK) ---- #
try:
	# Set local variables
	inPointFeatures = filePrefix + "hhPoints"
	zField = ["dietDiv", "agshkR"]  # These are the field names for the variables that will be iterated over
	outLayer = ""
	outRaster = filePrefix
	cellSize = ""
	transformation = "NONE"
	maxLocalPoints = ""
	overlapFactor = ""
	numberSemivariograms = "500"  # This is the number of semivariograms used to refine the model

	# Set variables for search neighborhood
	radius = ""
	angle = ""
	maxNeighbor = ""
	minNeighbor = ""
	sectorType = "8"  # This is important and you should figure out which value will work best for the purposes of your analysis
	searchNeighborhood = arcpy.SearchNeighborhoodStandardCircular(radius, angle, maxNeighbor,
																  minNeighbor, sectorType)

	# Set variables for output
	# outputType = Either PREDICTION or PREDICTION_STANDARD_ERROR as set in the EBK function
	quantileValue = ""
	thresholdType = ""
	probabilityThreshold = ""

	# Execute Empirical Bayesian Kriging for Prediction Surfaces
	print "\n\t 1 of 1: Starting EBK..."
	for s in zField:
		print "\t\t Creating the prediction surface for %s..." % s
		arcpy.EmpiricalBayesianKriging_ga(inPointFeatures, s, outLayer, outRaster + "EBK" + s, cellSize,
										  transformation, maxLocalPoints, overlapFactor,
										  numberSemivariograms, searchNeighborhood, "PREDICTION",
										  quantileValue, thresholdType, probabilityThreshold)
		print "\t\t\t Finished the prediction surface for %s!" % s
		
	# Execute Empirical Bayesian Kriging for Standard Error Surfaces
		print "\n\t\t Creating the standard error surface for %s..." % s
		arcpy.EmpiricalBayesianKriging_ga(inPointFeatures, s, outLayer, outRaster + "EBK" + s + "_SE", cellSize,
										  transformation, maxLocalPoints, overlapFactor,
										  numberSemivariograms, searchNeighborhood, "PREDICTION_STANDARD_ERROR",
										  quantileValue, thresholdType, probabilityThreshold)
		print "\t\t\t Finished the standard error surface for %s!" % s

	print "\n\t Complete: Finished EBK!"

except:
	# If an error occurred print the message to the screen
	print arcpy.GetMessages()

print "Part 2 of 4: Empirical Bayesian Kriging is complete!"
