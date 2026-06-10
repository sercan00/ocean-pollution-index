# Plastic pollution entering the ocean through rivers - Data package

This data package contains the data that powers the chart ["Plastic pollution entering the ocean through rivers"](https://ourworldindata.org/grapher/plastic-entering-ocean?v=1&csvType=full&useColumnShortNames=false&measure=total) on the Our World in Data website. It was downloaded on June 8, 2026.

### Active Filters

A filtered subset of the full data was downloaded. The following filters were applied:

## CSV Structure

The high level structure of the CSV file is that each row is an observation for an entity (usually a country or region) and a timepoint (usually a year).

The first two columns in the CSV file are "Entity" and "Code". "Entity" is the name of the entity (e.g. "United States"). "Code" is the OWID internal entity code that we use if the entity is a country or region. For most countries, this is the same as the [iso alpha-3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) code of the entity (e.g. "USA") - for non-standard countries like historical countries these are custom codes.

The third column is either "Year" or "Day". If the data is annual, this is "Year" and contains only the year as an integer. If the column is "Day", the column contains a date string in the form "YYYY-MM-DD".

The final column is the data column, which is the time series that powers the chart. If the CSV data is downloaded using the "full data" option, then the column corresponds to the time series below. If the CSV data is downloaded using the "only selected data visible in the chart" option then the data column is transformed depending on the chart type and thus the association with the time series might not be as straightforward.


## Metadata.json structure

The .metadata.json file contains metadata about the data package. The "charts" key contains information to recreate the chart, like the title, subtitle etc.. The "columns" key contains information about each of the columns in the csv, like the unit, timespan covered, citation for the data etc..

## About the data

Our World in Data is almost never the original producer of the data - almost all of the data we use has been compiled by others. If you want to re-use data, it is your responsibility to ensure that you adhere to the sources' license and to credit them correctly. Please note that a single time series may have more than one source - e.g. when we stich together data from different time periods by different producers or when we calculate per capita metrics using population data from a second source.

## Detailed information about the data


## Plastic pollution entering the ocean through rivers
Estimated quantity of plastic pollution entering the ocean via rivers, in tonnes per year.
Last updated: January 27, 2026  
Date range: 2019–2019  
Unit: tonnes  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
Meijer et al. (2021) – with minor processing by Our World in Data

#### Full citation
Meijer et al. (2021) – with minor processing by Our World in Data. “Plastic pollution entering the ocean through rivers” [dataset]. Meijer et al., “More than 1000 rivers account for 80% of global riverine plastic emissions into the ocean” [original data].
Source: Meijer et al. (2021) – with minor processing by Our World In Data

### What you should know about this data
* These estimates come from a statistical model that combines location-specific data with environmental factors. They are not direct measurements for every country and river.
* Annual emissions for a river basin are calculated by multiplying the mismanaged plastic waste in each location by its probability of reaching the ocean, then adding up all locations across the entire basin.
* These estimates focus on larger plastic items (typically bigger than 0.5 cm) that float on or near the water surface. They do not include tiny microplastics, plastic on riverbeds, or plastic stopped by dams.
* These estimates have significant uncertainty and can differ substantially from actual measurements. For example, if a river is estimated to carry 100 tonnes of plastic, the true value could reasonably be anywhere from 25 to 400 tonnes, and in some cases could be as low as 10 or as high as 1,000 tonnes.
* These figures do not include plastic waste that is shipped overseas for processing. That exported waste may be at higher risk of entering the ocean if it is not properly managed in the destination country.

### Source

#### Meijer et al. – More than 1000 rivers account for 80% of global riverine plastic emissions into the ocean
Retrieved on: 2026-01-27  
Retrieved from: https://www.science.org/doi/10.1126/sciadv.aaz5803  


    