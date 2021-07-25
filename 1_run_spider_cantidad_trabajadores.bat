call C:\ProgramData\Anaconda3\Scripts\activate.bat
call conda activate scrapy_01
scrapy crawl cantidad_trabajadores -a filename=empresas.txt
pause
