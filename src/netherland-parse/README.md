# README

This repository contains two Python scripts: `translator.py` and `parser.py`. These scripts are designed to assist in translating and parsing medicine data from a CSV file and a website.

## Translator

The `translator.py` script provides functions for translating json database into scs files by using sample. It includes the following functions:

- `translate_to_russian(text)`: Translates the given text to Russian using the Google Translate API.

- `substances_check(substances)`: Check if substance is in active.scs(database for all substances).
  
- `main()`: Build scs-file using json data.

These functions can be used to translate medicines into scs by default in scs-out folder

## Parser

The `parser.py` script is used to parse medicine data from a CSV file and a website. It utilizes the Selenium library to scrape data from the website and the pandas library to read data from the CSV file. The script performs the following tasks:

- Function `fix_name(data)`: This function takes a string or a list of strings as input and applies several transformations to ensure consistent naming conventions. It replaces whitespace, special characters, and converts the text to lowercase.

- Function `get_composition_for_medicine(url)`: This function takes a URL of a medicine information page as input and scrapes the composition, active substances, and marketing authorization holder from the page using web scraping techniques.

- Function `parse_medicines_from_csv(csv_url)`: This function reads medicine data from a CSV file located at the given URL. It iterates over the rows of the CSV file, extracts relevant information such as product names, potency, ATC codes, alternative names, pharmaceutical forms, and usage methods. It then calls the `get_composition_for_medicine` function to retrieve the composition, active substances, and marketing authorization holder for each medicine.
  
The parsed data is stored in a JSON file named `result.json`.

## Dependencies

The following dependencies are required to run the scripts:

- `googletrans`: A Python library for Google Translate API.

- `selenium`: A Python library for web scraping and automation.

- `pandas`: A powerful data manipulation library.

Make sure to install these dependencies before running the scripts using the following command:

```
pip install googletrans selenium pandas
```

## Usage

To use the scripts, follow these steps:

1. Clone the repository to your local machine.

2. Install the required dependencies using the command mentioned above.

3. Open a terminal or command prompt and navigate to the directory containing the scripts.

4. Run the `parser.py` script using the following command:

```
python parser.py
```

This will parse the medicine data from the CSV file and generate the `result.json` file containing the parsed data.

5. Optionally, you can modify and use the `translator.py` script to perform translations or use the provided translation functions in your own code.

## Note

Please note that the `parser.py` script relies on web scraping techniques to extract data from a specific website. Make sure to comply with the website's terms of service and do not abuse or overload the website with excessive requests.

## License

This project is licensed under the [MIT License](LICENSE). Feel free to modify and distribute the code as per the terms of the license.
