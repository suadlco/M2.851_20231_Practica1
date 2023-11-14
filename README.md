# M2.851_20231_Practica1: Proyecto de Scraping de Datos Financieros

## Integrantes del Grupo
- Sua de la Cruz Odriozola
- Víctor Manuel Miñambres Chamorro

## Descripción

Esta actividad se ha realizado en el marco de la asignatura "Tipología y Ciclo de Vida de los Datos" del programa de Máster en Ciencia de Datos de la Universitat Oberta de Catalunya. En esta práctica, se han empleado técnicas de web scraping utilizando el lenguaje de programación Python con el propósito de obtener información financiera de la plataforma web de Yahoo Finanzas.

### Estructura de Archivos

- **source/scraper.py:** Contiene la clase `YahooFinanceScraper` con los métodos necesarios para realizar el scraping.
- **source/main.py:** Punto de inicio del programa que da comienzo al proceso de obtención de datos mediante scraping.
- **dataset/dataset.csv:** Archivo CSV que almacena el dataset generado.

## Cómo Usar el Código Generado

Para realizar web scraping usando el código generado, basta con replicar el código del archivo __main.py__:
```
    yahoo_scraper = YahooFinanceScraper()
    yahoo_scraper.get_robots_txt()
    quote_links = yahoo_scraper.get_top100_megaCap('https://es.finance.yahoo.com/screener/unsaved/5be828dc-55da-4794-9ed1-2412da5d8d88?offset=0&count=100')
    data = yahoo_scraper.scrape_all_history_data(quote_links)
    yahoo_scraper.data2csv("dataset.csv", data)
```

Hay que tener en cuenta que el enlace pasado al método __get_top100_megaCap__ debe generarse de manera manual, puesto que no está permitido el acceso automatizado a ese directorio. Además, es un enlace que se genera al momento y se borra a los pocos días.