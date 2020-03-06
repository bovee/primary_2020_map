from geopandas.io.file import read_file
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import requests
import pandas as pd


# load all the maps
scc_precincts = read_file('./SCC_BOUNDARIES/Precinct_Boundaries.shp')
# scc_precincts = scc_precincts[scc_precincts['VALID'] == 'Valid']
scc_precincts.set_index('PRECINCT', inplace=True)
scc_precincts.index = 'SC_' + scc_precincts.index.map(str)
scc_precincts = scc_precincts[['geometry']]

smc_precincts = read_file('./SMC_BOUNDARIES/ELECTION_PRECINCTS.shp')
smc_precincts.set_index('ELECTION_P', inplace=True)
smc_precincts.rename_axis('PRECINCT', inplace=True)
smc_precincts.index = 'SM_' + smc_precincts.index.map(str)
smc_precincts = smc_precincts[['geometry']]

precincts = pd.concat([smc_precincts, scc_precincts])

## SCC data
scc_consolidations = {}
for line in open('./scc_consolidations_2018.txt'):
    sline = line.split('\t')
    from_p = sline[0].split()[-1]
    to_p = sline[2].split()[-1].split('/')[0]
    if from_p != to_p:
        scc_consolidations[f'SC_{from_p}'] = f'SC_{to_p}'

CACHE_PATH = './cached_smc.json'
if not os.path.exists(CACHE_PATH):
    scc_all_res = requests.get('https://results.enr.clarityelections.com//CA/Santa_Clara/101316/244146/json/ALL.json').json()['Contests']
    scc_summary = requests.get('https://results.enr.clarityelections.com//CA/Santa_Clara/101316/244146/json/en/summary.json').json()
    json.dump([scc_all_res, scc_summary], open(CACHE_PATH, 'w'))
else:
    scc_all_res, scc_summary = json.load(open(CACHE_PATH))

scc_contest_names = {}
scc_contest_options = {}
for s in scc_summary:
    if s['K'] in scc_contest_names:
        continue
    scc_contest_names[s['K']] = s['C']
    scc_contest_options[s['K']] = s['CH']

def get_scc_results(race_name, cand_name):
    results = {}
    for r in scc_all_res:
        precinct = r['A']
        for contest, values in zip(r['C'], r['V']):
            assert len(values) == len(scc_contest_options[contest])
            votes = dict(zip(scc_contest_options[contest], values))
            if scc_contest_names[contest] == race_name:
                results[f'SC_{precinct}'] = votes[cand_name] / sum(values)

    # TODO: technically better to merge the polygons in precincts, but this works for display
    # for k, v in scc_consolidations.items():
    #     if v in results:
    #         results[k] = results[v]
    return results

## SMC data
smc_votes = pd.read_csv('./smc_2020_primary/36_electionresults_03_05_2020.csv')
smc_votes.set_index('Precinct_name', inplace=True)
smc_consolidations = {}
for line in open('./smc_consolidations.txt'):
    for d in line.split()[1:]:
        smc_consolidations[f'SM_{d}'] = f'SM_{line.split()[0]}'

def get_smc_results(race_name, cand_name):
    results = smc_votes[
        (smc_votes['Contest_title'] == race_name) &
        (smc_votes['candidate_name'] == cand_name) &
        (smc_votes['total_ballots'] > 0)
    ].groupby(by=lambda x: x).aggregate(sum)
    results_p = results['total_votes'] / results['total_ballots']
    results_p.index = 'SM_' + results_p.index.map(str)
    results_p = results_p.to_dict()

    # TODO: technically better to merge the polygons in precincts, but this works for display
    # for k, v in smc_consolidations.items():
    #     if v in results_p:
    #         results_p[k] = results_p[v]

    return results_p

# now make some maps
# masur_p_scc = get_scc_results('State Senator, District 13', 'SHELLY MASUR')
# masur_p = get_smc_results('State Senator, 13th District', 'SHELLY MASUR')
masur_p_scc = get_scc_results('State Senator, District 13', 'SALLY J. LIEBER')
masur_p = get_smc_results('State Senator, 13th District', 'SALLY J. LIEBER')
masur_p.update(masur_p_scc)
masur_p = pd.Series(masur_p)

p13_p = get_smc_results('Proposition 13 (Majority Approval Required)', 'YES')
# p13_p = get_smc_results('San Mateo Union High School District, Measure L (55 Percent Approval Required)', 'BONDS YES')
dem_p = get_smc_results('President of the United States, Democratic', 'MICHAEL R. BLOOMBERG')
# 'BERNIE SANDERS', 'ELIZABETH WARREN', 'JOSEPH R. BIDEN'

precincts = precincts.assign(masur=masur_p)

fig, ax = plt.subplots(1, 1)
ax.set_axis_off()
# base = precincts.plot(column='dem', ax=ax, vmin=0.1, vmax=0.4, edgecolor=(0,0,0,0), legend=True)
base = precincts.plot(column='masur', ax=ax, vmin=0.1, vmax=0.4, edgecolor=(0,0,0,0), legend=True)
# base = precincts.plot(column='p13', ax=ax, vmin=0.35, vmax=0.75, cmap='PiYG', edgecolor=(0,0,0,0), legend=True)
smc_cities = read_file('./SMC_BOUNDARIES/CITY.shp')
smc_cities.plot(ax=ax, facecolor=(0,0,0,0), edgecolor="black")

# precincts['coords'] = precincts['geometry'].apply(lambda x: x.representative_point().coords[:])
# precincts['coords'] = [coords[0] for coords in precincts['coords']]
# for idx, row in precincts.iterrows():
#     plt.annotate(s=row.name, xy=row['coords'],
#                  horizontalalignment='center')

plt.show()
