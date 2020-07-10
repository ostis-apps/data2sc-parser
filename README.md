About
------------

This is a set of loaders and translators for extracting knowledge from external sources.

### Supported external sources:

* WikiData
* Google Search

How it works
------------

You input entities to get from external source. Loader make requests to source and gives all info in JSON format. After that info in JSON translates to SCS and saves to directory you choose.

Requirements
------------

For requirements installation use

    $ pip install -r requirements.txt

Usage
------------

Example

    $ py parse.py Minsk Belarus "Belarusian State University of Informatics and Radioelectronics"

* Input all entities titles with a space. 
* Then type language of title with --lang attribute (by default its 'en'). 
* Don't forget to choose directory for saving scs files and images. Make it with --dir attribute (by default its 'sc_out'). 
* Select external source with attribute --source from 'wiki' and 'google' (by default its 'wiki'). 
* If you want to get information about entity with context (relations with other entities and etc.) use --context=yes (by default its 'no'). 
* To get an intermediate JSON file use --debug=yes (by default its 'no').

Example with attributes

    $ py parse.py Минск --lang=ru --dir=output_dir --debug=yes

For help enter

    $ py parse.py --help