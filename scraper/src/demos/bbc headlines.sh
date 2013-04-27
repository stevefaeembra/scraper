curl -s http://www.bbc.co.uk/news/ | ./scrape --f ".//a[@class='headline-anchor']" | less
