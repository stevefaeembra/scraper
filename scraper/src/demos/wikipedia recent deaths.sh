curl -s https://en.wikipedia.org/wiki/Deaths_in_2013 | ./scrape --relaxed --f ".//div[@id='mw-content-text']/ul/li/a[1]" --x | less
