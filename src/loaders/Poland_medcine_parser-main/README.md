# Poland_medcine_parser

This repository contains a Python script, translator.py, which provides functions for translating and processing medicine data from an Excel file. The script utilizes the openpyxl library for reading Excel files and the googletrans library for translating text.

## Requirements

To run the script, you need to have the following dependencies installed:

- openpyxl: A library for reading and writing Excel files.

- googletrans: A library for Google Translate API.

You can install these dependencies using the following command:

pip install openpyxl googletrans
## Usage

1. Clone the repository to your local machine.

2. Install the required dependencies as mentioned above.

3. Open the translator.py file in a text editor.

4. Modify the excel_file variable to specify the path to your Excel file containing medicine data.

5. Adjust the number_of_files and number_of_scs variables according to your desired configuration.

6. Run the script using the following command:

python translator.py
The script will parse the medicine data from the Excel file, translate relevant information to English, and generate multiple .scs files based on the specified configuration.

## File Structure

The script generates multiple .scs files, each containing the translated and processed medicine data. The number of files and the number of records per file are determined by the number_of_files and number_of_scs variables, respectively.

## Translation and Processing

The script performs the following translation and processing tasks:

- Translates medicine names and other text fields from Polish to English using the Google Translate API.

- Fixes and standardizes various fields, such as medicine names, dosages, alternative names, pharmaceutical forms, and routes of administration.

- Extracts information such as ATC codes, marketing authorization holders, active substances, countries of sale, and dosage forms.

- Generates a template for each medicine record in the form of an .scs file, following a specific structure.

## Note

Please note that the script relies on the Google Translate API for translation. Make sure to comply with the terms of service and usage limits of the API to avoid any issues.

## License

This project is licensed under the [MIT License](LICENSE). Feel free to modify and distribute the code as per the terms of the license.
