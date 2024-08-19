##############################################################
Welcome to the NREL Global Climate Model Evaluation Repository
##############################################################

The interplay between energy, climate, and weather is becoming more complex due to increasing
contributions of renewable energy generation, energy storage, electrified end uses, and the
increasing frequency of extreme weather events. Energy system analyses commonly rely on
meteorological inputs to estimate renewable energy generation and energy demand; however,
these inputs rarely represent the estimated impacts of future climate change. Climate models and
publicly available climate change datasets can be used for this purpose, but the selection of
inputs from the myriad of available models and datasets is a nuanced and subjective process. In
this work, we assess datasets from various global climate models (GCMs) from the Coupled
Model Intercomparison Project Phase 6 (CMIP6). We present evaluations of their skills with
respect to the historical climate and comparisons of their future projections of climate change for
two climate change scenarios. We present the results for different climatic and energy system
regions and include interactive figures in the accompanying software repository. Previous work
has presented similar GCM evaluations, but none have presented variables and metrics
specifically intended for comprehensive energy systems analysis including impacts on energy
demand, thermal cooling, hydropower, water availability, solar energy generation, and wind
energy generation. We focus on GCM output meteorological variables that directly affect these
energy system components including the representation of extreme values that can drive grid
resilience events. The objective of this work is not to recommend the best climate model and
dataset for a given analysis, but instead to provide a reference to facilitate the selection of
climate models and scenarios in subsequent work. 

For interactive comparisons of GCM projections, check out the regional
results `here <https://nrel.github.io/gcm_eval/regions/conus.html>`_.
All of the plots after the skill tables are interactive. Try hovering your
mouse over data points, clicking and dragging, scrolling, and double clicking
on the legends.

For details on the methods and a discussion of the results, see the NREL technical report here:

::

    Buster, Grant, Slater Podgorny, Laura Vimmerstedt, Brandon Benton, and Nicholas D.
    Lybarger. 2024. Evaluation of Global Climate Models for Use in Energy Analysis. 
    Golden, CO: National Renewable Energy Laboratory. NREL/TP-6A20-90166.
    https://www.nrel.gov/docs/fy24osti/90166.pdf.

The NREL software record for this repository is SWR-24-37

Acknowledgments
===============

This work was authored by the National Renewable Energy Laboratory, operated by
Alliance for Sustainable Energy, LLC, for the U.S. Department of Energy (DOE)
under Contract No. DE-AC36-08GO28308. Funding provided by the DOE Office of
Energy Efficiency and Renewable Energy (EERE), the DOE Office of Electricity
(OE), the DOE Office of Fossil Energy and Carbon Management (FECM), and the DOE
Office of Cybersecurity, Energy Security, and Emergency Response (CESER). The
research was performed using computational resources sponsored by the DOE
Office of Energy Efficiency and Renewable Energy and located at the National
Renewable Energy Laboratory. The views expressed in the article do not
necessarily represent the views of the DOE or the U.S. Government. The U.S.
Government retains and the publisher, by accepting the article for publication,
acknowledges that the U.S. Government retains a nonexclusive, paid-up,
irrevocable, worldwide license to publish or reproduce the published form of
this work, or allow others to do so, for U.S. Government purposes.
