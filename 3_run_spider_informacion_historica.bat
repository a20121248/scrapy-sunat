call C:\ProgramData\Anaconda3\Scripts\activate.bat
call conda activate scrapy_01
scrapy crawl informacion_historica -a filename=empresas.txt
pause
