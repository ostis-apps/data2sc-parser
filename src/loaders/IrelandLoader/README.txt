Для работы программы необходимо установить несколько библиотек:

	pip install requests

	pip install googletrans==4.0.0-rc1

Для запуска парсера нужно запустить файл IrelandLoader.py.

В результате работы программы автоматически создадутся два файла: products.json и medicine_products.scs. Файл products.json будет содержать форматированные данные о всех лекарственных препаратах с сайта "https://www.hpra.ie/img/uploaded/swedocuments/latestHMlist.xml" в виде словарей, а файл medicine_products.scs будет содержать SCs-код. 
