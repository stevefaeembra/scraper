curl -s http://www.bbc.co.uk/news/ | python ../scraper2/scraper.py -phtML --m ".//a[@class='headline-anchor']" -fTSV -t | sort | less
