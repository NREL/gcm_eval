"""
Collect data from CMIP6 .nc files and make projection summaries per variable per region
"""

from concurrent.futures import ProcessPoolExecutor, as_completed
import os
from glob import glob
import json
import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import logging

from rex import Resource, init_logger
from region_classifier import RegionClassifier

from sup3r.preprocessing.data_handling.base import DataHandler
from sup3r.preprocessing.data_handling import DataHandlerNCforCC
from sup3r.preprocessing.data_handling import DataHandlerNCforCCwithPowerLaw
from sup3r.bias.bias_calc import SkillAssessment

logger = logging.getLogger(__name__)


DataHandlerNCforCC.CHUNKS = {'time': None, 'lat': None, 'lon': None}


MODELS = ["CESM2",
    "CESM2-WACCM",
    "EC-Earth3-CC",
    "EC-Earth3",
    "EC-Earth3-Veg",
    "GFDL-CM4",
    "GFDL-ESM4",
    "INM-CM4-8",
    "INM-CM5-0",
    "MPI-ESM1-2-HR",
    "MRI-ESM2-0",
    "NorESM2-MM",
    "TaiESM1",
    ]
TAGS = [gcm.lower().replace('-','') for gcm in MODELS]


FEATURES = ['temperature_2m', 'temperature_max_2m', 'temperature_min_2m',
            'relativehumidity_2m', 'relativehumidity_max_2m', 'relativehumidity_min_2m',
            'rsds', 'pr']
#FEATURES = ['windspeed_100m']

FEATURE_MAP = {'temperature_2m': 'tas',
               'temperature_max_2m': 'tasmax',
               'temperature_min_2m': 'tasmin',
               'relativehumidity_2m': 'hurs',
               'relativehumidity_max_2m': 'hursmax',
               'relativehumidity_min_2m': 'hursmin',
               'rsds': 'rsds',
               'pr': 'pr',
               'windspeed_100m': 'windspeed_100m'}

REGIONS = {
    'Northeast': ['Connecticut', 'Delaware', 'Maine', 'Maryland', 'Massachusetts',
                  'New Hampshire', 'New Jersey', 'New York', 'Pennsylvania',
                  'Rhode Island', 'Vermont', 'District of Columbia'],

    'Upper Midwest': ['Iowa', 'Michigan', 'Minnesota', 'Wisconsin'],

    'Ohio Valley': ['Illinois', 'Indiana', 'Kentucky', 'Missouri', 'Ohio',
                    'Tennessee', 'West Virginia'],

    'Southeast': ['Alabama', 'Florida', 'Georgia', 'North Carolina',
                  'South Carolina', 'Virginia'],

    'Northern Rockies and Plains': ['Montana', 'Nebraska', 'North Dakota',
                                    'South Dakota', 'Wyoming'],

    'South': ['Arkansas', 'Kansas', 'Louisiana', 'Mississippi', 'Oklahoma',
              'Texas'],

    'Southwest': ['Arizona', 'Colorado', 'New Mexico', 'Utah'],

    'Northwest': ['Idaho', 'Oregon', 'Washington'],

    'West': ['California', 'Nevada'],

    
    'WECC': ['California', 'Nevada', 'Idaho', 'Oregon', 'Washington', 'Arizona', 
             'Colorado', 'New Mexico', 'Utah', 'Montana', 'Wyoming'],
    'MRO': ['Nebraska', 'North Dakota', 'South Dakota', 'Iowa', 'Minnesota', 'Kansas', 'Oklahoma', 'Wisconsin'],
    'Texas RE': ['Texas'],
    'SERC': ['Alabama', 'Florida', 'Georgia', 'North Carolina',
             'South Carolina', 'Virginia', 'Kentucky', 
             'Tennessee', 'Illinois', 'Missouri',
             'Arkansas', 'Louisiana', 'Mississippi'],
    'RF': ['Indiana', 'Ohio', 'West Virginia', 'Pennsylvania', 'Michigan', 
           'New Jersey', 'Delaware', 'Maryland', 'District of Columbia'],
    'NPCC': ['Connecticut', 'Maine', 'Massachusetts',
                  'New Hampshire', 'New York',
                  'Rhode Island', 'Vermont'],
}
REGIONS['conus'] = sorted(set([x for sub in REGIONS.values() for x in sub]))


def get_countries_shape():
    fp_shape = '/projects/alcaps/gcm_eval/analysis/gis_data/WorldCountries50mShapefile/ne_50m_admin_0_countries.shp'
    countries = gpd.GeoDataFrame.from_file(fp_shape)
    countries_col = 'admin'
    countries[countries_col] = countries[countries_col].astype(str)
    countries = countries[countries[countries_col] == 'United States of America']
    countries = countries.to_crs('EPSG:4326')
    return countries, countries_col


def get_states_shape():
    fp_shape = '/projects/alcaps/gcm_eval/analysis/gis_data/us_states_shapefiles/s_11au16.shp'
    states = gpd.GeoDataFrame.from_file(fp_shape)
    states_col = 'NAME'
    states[states_col] = states[states_col].astype(str)
    states = states.to_crs('EPSG:4326')
    return states, states_col


def get_eez_shape():
    fp_shape = '/projects/alcaps/gcm_eval/analysis/gis_data/EEZ_land_union_v3_202003/EEZ_Land_v3_202030.shp'
    eez = gpd.GeoDataFrame.from_file(fp_shape)
    eez_col = 'TERRITORY1'
    eez = eez[eez['TERRITORY1'] == 'United States']
    eez = eez.to_crs('EPSG:4326')
    return eez, eez_col


def get_targets_shapes():
    dh_targets = {}
    dh_shapes = {}

    for tag in TAGS:
        fp_base = '/projects/alcaps/gcm_eval/{}_historical/config_bias.json'
        fp_config = fp_base.format(tag)
        assert os.path.exists(fp_config)
        with open(fp_config, 'r') as f:
            config = json.load(f)

        dh_targets[tag] = config['jobs'][0]['target']
        dh_shapes[tag] = config['jobs'][0]['shape']
    return dh_targets, dh_shapes



def get_fps(model, scenario, feature, fp_base='/projects/alcaps/cmip6/{}/*.nc'):

    fps = sorted(glob(fp_base.format(model)))
    fps = [fp for fp in fps if scenario in fp or 'historical' in fp or 'orog_' in fp]

    if 'windspeed' in feature:
        dsets = ('ua', 'va', 'zg', 'orog')
        fps = [fp for fp in fps if os.path.basename(fp).startswith(dsets)]

        if model in ('EC-Earth3-CC', 'EC-Earth3-Veg'):
            # remove ua/va
            # EC-Earth3-CC/Veg does not have historical zg so need to use uas/vas
            dsets = ('ua_', 'va_', 'zg_')
            fps = [fp for fp in fps if not os.path.basename(fp).startswith(dsets)]

        elif any('ua_' in fp for fp in fps) and any('uas_' in fp for fp in fps):
            # remove uas/vas
            dsets = ('uas_', 'vas_')
            fps = [fp for fp in fps if not os.path.basename(fp).startswith(dsets)]

        if sum('orog_' in fp for fp in fps) > 1:
            orog_fps = [fp for fp in fps if 'orog_' in fp]
            for fp in orog_fps[1:]:
                fps.remove(fp)
        for fp in fps:
            if '_overwrite_coords' in fp:
                fp_og = fp.replace('_overwrite_coords', '')
                if fp_og in fps:
                    fps.remove(fp_og)

    else:
        fps = [fp for fp in fps if os.path.basename(fp).startswith(feature + '_')]

    return fps


def make_summary_files(model, tag, feature, scenario, fp_out, fp_base='/projects/alcaps/cmip6/{}/*.nc', max_workers=1):

    dh_targets, dh_shapes = get_targets_shapes()

    model_feature = FEATURE_MAP[feature]
    fps = get_fps(model, scenario, model_feature, fp_base=fp_base)

    if not any(fps):
        msg = (f'Could not find any files for {model} {scenario} {feature}')
        logger.error(msg)
        raise RuntimeError(msg)

    DataHandlerClass = DataHandlerNCforCC
    if any('uas_' in fp for fp in fps) and not any('ua_' in fps for fp in fps):
        DataHandlerClass = DataHandlerNCforCCwithPowerLaw

    #cache_pattern = f'/projects/alcaps/gcm_eval/analysis/cache/{model}_{scenario}'
    #cache_pattern += '_{feature}.pkl'

    logger.info(f'Initializing data handler for {model} {scenario} {feature}')
    try:
        dh = DataHandlerClass(fps, [feature], target=dh_targets[tag], shape=dh_shapes[tag],
                              worker_kwargs={'max_workers': max_workers}, time_chunk_size=int(1e6),
                              )
    except Exception as e:
        msg = f'Failed to init data handler for {model} {scenario} {feature}'
        logger.exception(msg)
        raise RuntimeError(msg)
    logger.info(f'Finished initializing data handler for {model} {scenario}, {feature}')

    try:
        countries, countries_col = get_countries_shape()
        states, states_col = get_states_shape()
        eez, eez_col = get_eez_shape()
        meta = RegionClassifier(dh.meta, countries, countries_col).classify()
        meta = RegionClassifier(meta, states, states_col).classify()
        meta = RegionClassifier(meta, eez, eez_col).classify()
        meta['atlantic'] = (meta[countries_col] == '-999') & (meta[eez_col] != '-999') & (meta['longitude'] < -105)
        meta['gulf'] = (meta[countries_col] == '-999') & (meta[eez_col] != '-999') & (meta['longitude'] > -105) & (meta['longitude'] < -81.5)
        meta['pacific'] = (meta[countries_col] == '-999') & (meta[eez_col] != '-999') & (meta['longitude'] > -81.5)

        for rname, states in REGIONS.items():
            smask = meta['NAME'].values.reshape(dh_shapes[tag])
            smask = np.isin(smask, states)
            pincl = 100 * (smask.sum() / smask.size)
            tmask = dh.time_index.year.isin(range(1980, 2060))

            arr = dh.data[:, :, tmask, :]
            arr[~smask] = np.nan
            arr = np.nanmean(arr, axis=(0, 1))
            df = pd.DataFrame({dset: arr[:, i] for i, dset in enumerate(dh.features)}, index=dh.time_index[tmask])

            r_fp_out = fp_out.replace('conus_', rname.lower().replace(' ', '_') + '_')
            df.to_csv(r_fp_out)
            logger.info(f'Finished writing: {r_fp_out}')

        for rname in ('atlantic', 'gulf', 'pacific'):
            smask = meta[rname].values.reshape(dh.data.shape[:2])
            arr = dh.data[:, :, tmask, :]
            arr[~smask] = np.nan
            arr = np.nanmean(arr, axis=(0, 1))
            df = pd.DataFrame({dset: arr[:, i] for i, dset in enumerate(dh.features)}, index=dh.time_index[tmask])

            r_fp_out = fp_out.replace('conus_', rname.lower().replace(' ', '_') + '_')
            df.to_csv(r_fp_out)
            logger.info(f'Finished writing: {r_fp_out}')
    except Exception as e:
        msg = f'Failed to make files for {model} {scenario} {feature}'
        logger.exception(msg)
        raise RuntimeError(msg)

    return dh, meta, df



if __name__ == '__main__':
    init_logger(__name__, log_file='./make_projection_summaries_cmip.log')
    # init_logger('sup3r', log_level='DEBUG')

    futures = []
    with ProcessPoolExecutor(max_workers=10) as exe:
        for scenario in ('ssp585', 'ssp245'):
            for model, tag in zip(MODELS, TAGS):
                for feature in FEATURES:
                    fp_out = f'./projections/conus_{tag}_{scenario}_{feature}.csv'
                    if not os.path.exists(fp_out):
                        # try:
                        #     make_summary_files(model, tag, feature, scenario, fp_out)
                        # except Exception as e:
                        #     pass
                            
                        future = exe.submit(make_summary_files, model, tag, feature, scenario, fp_out)
                        futures.append(future)

        logger.info(f'Submitted {len(futures)} futures')
        for i, future in enumerate(as_completed(futures)):
            _ = future.result()
            logger.info(f'Completed {i+1} out of {len(futures)} futures')
