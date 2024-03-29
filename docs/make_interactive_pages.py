"""
Programatically make docs pages for interactive plots per region.
Run this before running ``make html``
"""
import glob

REGIONS = ['CONUS',
           'Northeast', 'Northern Rockies and Plains',
           'Northwest', 'Ohio Valley', 'South', 'Southeast',
           'Southwest', 'Upper Midwest', 'West',
           'MRO', 'NPCC', 'RF', 'SERC', 'Texas RE', 'WECC',
           'Atlantic', 'Pacific', 'Gulf',
           'TVA', 'Southern Company']

NOAA = ['Northeast', 'Northern Rockies and Plains',
        'Northwest', 'Ohio Valley', 'South', 'Southeast',
        'Southwest', 'Upper Midwest', 'West']
NERC = ['MRO', 'NPCC', 'RF', 'SERC', 'Texas RE', 'WECC']
OFFSHORE = ['Atlantic', 'Pacific', 'Gulf']
UTILITIES = ['TVA', 'Southern Company']

VARS = {'t2m': 'Change in Temperature',
        't2m_max': 'Daily Maximum Temperature Events',
        't2m_min': 'Daily Minimum Temperature Events',
        'rh': 'Change in Relative Humidity',
        'pr': 'Change in Precipitation',
        'pr_min': 'Annual Minimum Precipitation Events',
        'ws100m': 'Change in Windspeed',
        'ghi': 'Change in Global Horizontal Irradiance',
        }

PLOT_DESC = ('All of the following plots are interactive. Try hovering your '
             'mouse over data points, clicking and dragging, scrolling, and '
             'double clicking on the legends.')


if __name__ == '__main__':
    index = ['.. toctree::\n',
             '   :hidden:\n\n',
             '   Home page <self>\n']

    for region in REGIONS:
        tag = region.lower().replace(' ', '_')
        fps = sorted(glob.glob(f'./source/_static/trend_plots/{tag}*.html'))
        region_rst = f'./source/regions/{tag}.rst'

        if region in NOAA:
            region = f'NOAA Region {region}'
        elif region in NERC:
            region = f'NERC Region {region}'
        elif region in OFFSHORE:
            region = f'Offshore Wind Region {region}'
        elif region in UTILITIES:
            region = f'Utility Partner {region}'

        region_pointer = region_rst.replace('./source/', '')
        index.append(f'   {region} <{region_pointer}>\n')

        with open(region_rst, 'w') as f:
            f.write(f'{"#"*len(region)}\n')
            f.write(f'{region}\n')
            f.write(f'{"#"*len(region)}\n\n')

            title = f'Map of {region}'
            f.write(f'\n{title}\n')
            f.write(f'{"="*len(title)}\n\n')
            f.write(f'.. image:: ../_static/region_maps/map_{tag}.png\n\n')
            if 'NERC' in region:
                f.write('Note that we used a simple state mask, and the '
                        'region may not perfectly match the spatial boundary '
                        'of the true NERC region.\n\n')

            title = 'GCM Historical Skill Summary (1980-2019)'
            f.write(f'\n{title}\n')
            f.write(f'{"="*len(title)}\n\n')
            f.write('.. raw:: html\n')
            f.write(f'   :file: ../_static/skill_tables/skill_{tag}.html\n')
            f.write('\n|\n|\n\n')

            title = 'GCM Changes from 1980-2019 to 2050-2059'
            f.write(f'\n{title}\n')
            f.write(f'{"="*len(title)}\n')
            f.write(f'{PLOT_DESC}\n\n')
            for scenario in ('ssp245', 'ssp370', 'ssp585'):
                f.write('.. raw:: html\n')
                f.write(f'   :file: ../_static/scatter_plots/{tag}_scatter_{scenario}.html\n')

            for var, title in VARS.items():
                f.write(f'\n|\n\n{title}\n')
                f.write(f'{"="*len(title)}\n\n')
                f.write('.. raw:: html\n')
                f.write(f'   :file: ../_static/trend_plots/{tag}_{var}.html\n')

        with open('./source/index.rst', 'w') as f:
            f.writelines(index)
            f.write('\n.. include:: ../../README.rst\n')
