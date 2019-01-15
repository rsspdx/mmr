setwd("~/data/geo/mmr")

library(ggplot2)
library(rgdal)
library(plyr)

# get shapefile for world map and data file for maternal mortality
download.file("https://opendata.arcgis.com/datasets/252471276c9941729543be8789e06e12_0.zip", destfile = "countries.zip")
download.file("http://api.worldbank.org/v2/en/indicator/SH.STA.MMRT?downloadformat=csv", destfile = "mmr.zip")
download.file("https://drive.google.com/file/d/1vv1qy2hGSgSmO-p_D0wZYAJkVc4JKeu6/view?usp=sharing", destfile = "iso_2_iso_3.csv")
mmr.files <- unzip("mmr.zip")
unzip("countries.zip")
mmr.data <- read.csv(mmr.files[2], skip = 3, stringsAsFactors = FALSE)
mmr.data.name <- mmr.data$Country.Name
mmr.data.code <- mmr.data$Country.Code
mmr.data.mmr <- mmr.data$X2015
mmr.data.df <- as.data.frame(cbind(mmr.data.name, mmr.data.code, mmr.data.mmr))
names(mmr.data.df) <- c("Country.Name", "Country.Code", "mmr")

world.map <- readOGR(dsn=".", layer = "UIA_World_Countries_Boundaries")
world.map@data$id <- rownames(world.map@data)
world.map.df <- fortify(world.map)

# need to get ISO2 country codes
iso_2_iso_3 <- read.csv("iso_2_iso_3.csv")
iso_2_iso_3$ISO <- iso_2_iso_3$ISO2
mmr.data.df <- merge(iso_2_iso_3, mmr.data.df, by.x="ISO3", by.y="Country.Code")

# merge maternal mortality data
mmr <- merge(world.map, mmr.data.df, by = "ISO")
mmr <- fortify(mmr)

# create a map
map <- ggplot(data = mmr, aes(x = long, y = lat, group = group) + geom_polygon(fill = mmr))

# look at the map
map

