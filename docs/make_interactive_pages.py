"""
Programatically make docs pages for interactive plots per region.
Run this before running ``make html``
"""
import glob

REGIONS = ['CONUS']

VARS = {'t2m': 'Change in Temperature (Celsius)',
        't2m_degf': 'Change in Temperature (Fahrenheit)',
        't2m_max': 'Daily Max Temperature (Celsius)',
        't2m_max_degf': 'Daily Max Temperature (Fahrenheit)',
        't2m_min': 'Daily Min Temperature (Celsius)',
        't2m_min_degf': 'Daily Min Temperature (Fahrenheit)',
        'rh': 'Change in Relative Humidity',
        'pr': 'Change in Precipitation',
        'ws100m': 'Change in Windspeed',
        'ghi': 'Change in Global Horizontal Irradiance',
        }


if __name__ == '__main__':
    index = ['.. toctree::\n',
             '   :hidden:\n\n',
             '   Home page <self>\n',
             '\n.. include:: ../../README.rst\n']

    for region in REGIONS:
        tag = region.lower().replace(' ', '_')
        fps = sorted(glob.glob(f'./source/_static/trend_plots/{tag}*.html'))
        region_rst = f'./source/regions/{tag}.rst'

        region_pointer = region_rst.replace('./source/', '')
        index.insert(3, f'   {region} <{region_pointer}>\n')

        with open(region_rst, 'w') as f:
            f.write(f'{"#"*len(region)}\n')
            f.write(f'{region}\n')
            f.write(f'{"#"*len(region)}\n\n')
            for var, title in VARS.items():
                f.write(f'\n{title}\n')
                f.write(f'{"="*len(title)}\n\n')
                f.write('.. raw:: html\n')
                f.write(f'   :file: ../_static/trend_plots/{tag}_{var}.html\n')

        with open('./source/index.rst', 'w') as f:
            f.writelines(index)
