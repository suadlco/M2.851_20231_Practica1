import requests
from bs4 import BeautifulSoup
import re
import time
import pandas as pd
import os
import random


class YahooFinanceScraper:
    def __init__(self):
        #Iniciando los atributos de la clase
        self.robots_txt_url = "https://finance.yahoo.com/robots.txt"
        self.sitemap_url_quotes = "https://finance.yahoo.com/sitemap_en-us_quotes_index.xml"
        self.disallowed_directories = []
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}


    # Función que recoge todos los directorios a los que no se permite el acceso (los cuales están en el archivo robots.txt)
    def get_robots_txt(self):
        response = requests.get(self.robots_txt_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            disallow_lines = [line for line in soup.get_text().splitlines() if 'Disallow' in line]
            self.disallowed_directories = [line.split(':')[1].replace('*', '').strip() for line in disallow_lines]
        else:
            print("No se pudo obtener el archivo robots.txt")
            
    # Devuelve una lista con todos los xml recogidos en el sitemap de los valores
    # El objetivo es conocer el tamaño de la web
    def get_quote_xmls(self):
        response = requests.get(self.sitemap_url_quotes)
        soup = BeautifulSoup(response.text, 'xml')
        urls = [loc.text for loc in soup.find_all('loc')]
        return urls

    # Devuelve una lista con todos los enlaces de los distintos valores que aparecen en un xml 
    def get_quote_links_from_xml(self, xml_url):
        # Espaciado entre peticiones basándose en el tiempo de respuesta
        t0 = time.time()
        response = requests.get(xml_url)
        response_delay = time.time() - t0
        time.sleep(10 * response_delay)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        links = [loc.text.replace("summary/", "") for loc in soup.find_all('loc') if re.search(r'/quote/[^/]+/summary/$', loc.text)]
        return links

    # Devuelve una lista con todos los enlaces de los distintos valores
    def get_all_quote_links(self):
        xml_urls = self.get_quote_xmls()
        all_links = []
        for xml_url in xml_urls:
            links = self.get_quote_links_from_xml(xml_url)
            all_links.extend(links)
        return all_links

    # Recibe un enlace como parametro y devuelve una lista de los 100 primeros nombres de la tabla del enlace
    # El objetivo es recoer los 100 valores más relevantes respecto a la capitalización de mercado
    def get_top100_megaCap(self, url):        
        try:
            respuesta = requests.get(url, headers=self.headers)
            respuesta.raise_for_status()
            html = respuesta.content
            soup = BeautifulSoup(html, 'html.parser')
            table = soup.find('table')
            column_texts = []
            url_quote = "https://es.finance.yahoo.com/quote/"
            if table:
                # Iterar a través de las filas de la tabla (ignorando la fila de encabezado)
                for row in table.find_all('tr')[1:101]:  
                    first_column = row.find('td')
                    column_texts.append(first_column.get_text(strip=True))
                return [url_quote + t + "/" for t in column_texts]
                
        except requests.exceptions.RequestException as e:
            print(e.strerror)
            
            
    # Recibe un enlace del cual hay que obtener datos de interés
    def scrape_history_data(self, quote_url):
        # Se le añade al link recibido la información necesaria para visibilizar la tabla con los datos que queremos:
        # Datos históricos del valor, intervalos de un mes, datos de los últimos 5 años
        url_completa = quote_url + "history?period1=1541721600&period2=1699488000&interval=1mo&filter=history&frequency=1mo&includeAdjustedClose=true"
        
        try:
            t0 = time.time()
            respuesta = requests.get(url_completa, headers=self.headers)
            response_delay = time.time() - t0
            respuesta.raise_for_status()
            # Espaciado aleatorio de peticiones basándose en el tiempo de respuesta
            time.sleep(random.randint(20,50)/10 * response_delay)
            soup = BeautifulSoup(respuesta.text, 'html.parser')

            # Obtener datos de interés
            titulo = soup.find('h1', class_='D(ib) Fz(18px)')
            div = soup.find('div', class_='C($tertiaryColor) Fz(12px)')   
            tabla = soup.find('table', class_='W(100%) M(0)')

            # Guardar los datos de interés solamente si todos los campos se han encontrado
            if titulo and div and tabla:
                encabezados = ["Nombre", "Divisa"] + [th.text.strip() for th in tabla.find_all('th')] + ["Dividendo"]
                filas = tabla.find_all('tr', class_='BdT Bdc($seperatorColor) Ta(end) Fz(s) Whs(nw)')
                rows_valores = []
                
                # Recopilar los valores de la tabla 
                for fila in filas:
                    celdas = fila.find_all('td')
                    valores = [titulo.text.strip(), div.text.strip().split()[-1]] + [celda.text.strip() for celda in celdas]
                    if len(encabezados)-1==len(valores):
                        rows_valores.append(valores+["-"])
                    elif len(valores)==4 and "Dividend" in valores[3]:
                        rows_valores.append(valores[:3]+len(encabezados[4:])*["-"]+valores[3:])
                return [encabezados] + rows_valores
            else:
                return None
            
        except requests.exceptions.RequestException as e:
            print(e.strerror)
            pass
        
    # Recibe una lista de enlaces de los que se quiere obtener datos de interés
    # Devuelve una lista con los datos de interés recopilados
    def scrape_all_history_data(self, all_links):
        data = []
        for link in all_links:
            # Se asegura que no se accede a ningún directorio no permitido
            disallowed_found = any(disallowed_dir in link for disallowed_dir in self.disallowed_directories)
            if not disallowed_found:
                r = self.scrape_history_data(link)
                if r!=None:
                    if len(data)==0:
                        data = data + r
                    else:
                        data = data + r[1:]
        return data
                
            
    # Transforma los datos recopilados para guardarlos en un archivo csv
    def data2csv(self, filename, data):
        df = pd.DataFrame(data[1:], columns=data[0])
        dataset_path = os.path.join(os.path.split(os.getcwd())[0], "dataset/"+filename)
        df.to_csv(dataset_path, index=False)




