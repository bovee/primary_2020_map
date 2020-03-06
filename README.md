## Introduction
This is a little playground to see if I can successfully map the entirety of the 2020 state senate primary which is split between San Mateo and Santa Clara counties.

All of the data processing and mapping work occurs in `plot_elec_results.py`.

_Requires shapefile precinct map of Santa Clara county._

## Todo
 - The precinct consolidations for Santa Clara county don't appear to be the same from 2018 to 2020, but I can't find the current mapping.
 - Maybe this should just be a Jupyter notebook?

## Data Provenance

SMC map data from:
https://isd.smcgov.org/gis-data-download

SMC election results data and precinct consolidations from:
https://www.smcacre.org/march-3-2020-election-results-0

SCC election results data from API used by:
https://results.enr.clarityelections.com/CA/Santa_Clara/101316/web.241347/#/summary

SCC consolidations (from last election 2018; do not appear to be correct):
https://www.sccgov.org/sites/rov/Resources/Pages/PastEResults.aspx
