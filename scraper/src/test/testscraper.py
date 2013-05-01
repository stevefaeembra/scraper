'''
Created on 26 Apr 2013

@author: steven
'''
import unittest
from scraper2.scraper import scraper
from lxml import etree

class Test(unittest.TestCase):

    def setUp(self):
        self.parser = etree.HTMLParser()
        
    def testConstruct(self):
        patterns = [".//div",".//div[@class='test']/*/a"]
        scr = scraper("test",patterns,self.parser)
        assert scr.name == "test"
        assert scr.XPathPatterns == patterns
        assert scr.parser == self.parser
        
    def testValidXPath(self):
        patterns = [".//div",".//div[@class='test']/*/a"]
        scr=scraper("test",patterns,self.parser)
        assert scr._checkPatterns()
        
    def testInvalidXPath(self):
        patterns = [".//div/foo()",".//div[@class='test']/*/a"]
        try:
            scr=scraper("test",patterns,self.parser)
        except Exception as ex:
            assert ex.message==".//div/foo() is not a valid XPath Expression"

    def testNoneXPath(self):
        patterns=None
        try:
            scr=scraper("test",patterns,self.parser)
        except Exception as ex:
            assert ex.message=="No XPath expressions passed to scraper"

    def testEmptyXPath(self):
        patterns=[]
        try:
            scr=scraper("test",patterns,self.parser)
        except Exception as ex:
            assert ex.message=="No XPath expressions passed to scraper"

    def testAmazonBestSellers(self):
        fi = open("./amazonbestsellers.html")
        patterns = ["//a"]
        scr = scraper("test",patterns,self.parser)
        results = scr.parse(fi)
        fi.close()
        assert len(results)==1 # one column
        assert len(results[0])==256
        
    def testBBCNewsHeadlines_1(self):
        fi = open("./bbcnews.html")
        patterns = ["//a"]
        scr = scraper("test",patterns,self.parser)
        results = scr.parse(fi)
        fi.close()
        assert len(results[0])==161
        
    def testPaddingListsToEqualLengthOneList(self):
        patterns = ["//a"]
        scr = scraper("test",patterns,self.parser)
        testlist=[["a","b","c"]]
        result=scr._padListsToEqualLength(testlist)
        assert result==testlist

    def testPaddingListsToEqualLengthMoreThanOneList(self):
        patterns = ["//a"]
        scr = scraper("test",patterns,self.parser)
        testlist=[["a","b","c"],["e"],["f","g","h","i"]]
        expect=[["a","b","c","-"],["e","-","-","-"],["f","g","h","i"]]
        result=scr._padListsToEqualLength(testlist)
        assert result==expect
        
    def testPaddingListsToEqualLength(self):
        fi = open("./bbcnews.html")
        patterns = ["//a","//h1"]
        scr = scraper("test",patterns,self.parser)
        results = scr.parse(fi)
        fi.close()
        print results[0]
        print results[1]
        assert len(results[0])==161
        assert len(results[1])==161
    
    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()