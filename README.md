# reinfCalcEngine

## About the computation engine

The engine can be used to dimension selected types of reinforced concrete elements within assumed calculations scope.
It uses algorithms, prepared by the author on the basis of information covered by books [Tablice i wzory...] and [Przykłady obliczania...], converted to Python statements.


## App's Tech Stack

Computing engine module
   - [Python3] - Main coding language of the module
   - [jsonschema] - Python module used for json files validation

*The application is a part of Reinforcement Calculator Project, see its other parts: [web application], [reinfCalc] desktop application*

## Using the engine

### Installation

In order to work with the module, its source code must be downloaded and dependencies installed.

First, download the source code or copy repository to the desired location.

Next, install all the required modules using: `<path to python script>\python -m pip install -r requirements.txt`

Use of virtual environment for running the script is advised in order to avoid conflicts between modules.
Instructions on creating a virtual environment in Python can be found in [Python docs on venv installation].

Finally, to use the module's functionalities, user should place the module's directory in desired location and import 
the `main.py` script within the script aiming to use it.

### Working with the engine

The files used for calculations must be valid with accordance to the schemas placed in the `json_schema` directory.

First, data for calculations must be parsed to a Python dictionary.

Next step is choosing proper element class or getting it using the dispatcher by providing information about
the element type in form of a string (e.g., `dispatcher['plate']` returns `Plate` class, available options are: 
plate, beam, column, foot)

Then, an element instance must be created using the obtained element class (e.g., rc_element = `Plate(<data_dictionary>)`)

Finally, calculations can be performed calling `calc_reinforcement` method and saved to a variable in order
to access them later (e.g., `results = rc_element.calc_reinforcement()`).


   [Python3]: <https://www.python.org/>
   [jsonschema]: <https://json-schema.org/>
   [reinfCalc]: <https://github.com/michalkowal66/reinfCalc>
   [Web application]: <https://github.com/michalkowal66/reinfCalcServer>
   [Python docs on venv installation]: <https://docs.python.org/3/library/venv.html>
   [Tablice i wzory...]: <https://www.researchgate.net/publication/303311463_Tablice_i_wzory_do_projektowania_konstrukcji_zelbetowych_z_przykladami_obliczen>
   [Przykłady obliczania...]: <https://www.researchgate.net/publication/303311278_Przyklady_obliczania_konstrukcji_zelbetowychBudynek_ze_stopami_plytowo-zebrowymi>
