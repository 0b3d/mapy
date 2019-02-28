#!/usr/bin/env bash

#Postgis 
# To eliminate a postgis database run this psql command 
# DROP DATABASE <name-of-database>;

# Create a vitual environment and install some stuff 
conda create -n mapnik -c conda-forge -c cpaulik python-mapnik
conda activate mapnik
conda install -c conda-forge proj4
conda install psycopg2
conda install tensorflow
conda install -c conda-forge opencv

# Download map data and save it in shapes/ 
source download.sh
shapeindex --shape_files \
data/simplified-water-polygons-complete-3857/simplified_water_polygons.shp \xxz
data/water-polygons-split-3857/water_polygons.shp \
data/antarctica-icesheet-polygons-3857/icesheet_polygons.shp \
data/antarctica-icesheet-outlines-3857/icesheet_outlines.shp \
data/ne_110m_admin_0_boundary_lines_land/ne_110m_admin_0_boundary_lines_land.shp

# Put this a directory in map_data/styles/data
mkdir -p map_data/styles/data
cp -r shapes/* map_data/styles/data/

#Copy the symbols carpet to map_data/styles
cp -r ../carto/symbols map_data/styles/

# This will clone openstreet map carto in a parallele directory to this repo
git clone https://github.com/dooman87/openstreetmap-carto.git ../carto
cd ../carto 

#Para crear el archivo xml usar
xmllint --format osm.xml > osm2.xml --noent