from scraper import YahooFinanceScraper


yahoo_scraper = YahooFinanceScraper()
yahoo_scraper.get_robots_txt()
quote_links = yahoo_scraper.get_top100_megaCap('https://es.finance.yahoo.com/screener/unsaved/5be828dc-55da-4794-9ed1-2412da5d8d88?offset=0&count=100')
data = yahoo_scraper.scrape_all_history_data(quote_links)
yahoo_scraper.data2csv("dataset.csv", data)