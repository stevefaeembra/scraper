curl -s https://en.wikipedia.org/wiki/Deaths_in_2013 | python ../scraper2/scraper.py -phtML --m ".//div[@id='mw-content-text']/ul/li/a[1]" -fTSV -t | less
 
 
