'''
Created on 26 Apr 2013

@author: steven
'''
import unittest
from scraper2.scraper import *
from lxml import etree
import StringIO

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
        fi = open("./testfiles/amazonbestsellers.html")
        patterns = ["//a"]
        scr = scraper("test",patterns,self.parser)
        results = scr.parse(fi)
        fi.close()
        assert len(results)==1 # one column
        assert len(results[0])==256
        
    def testBBCNewsHeadlines_1(self):
        fi = open("./testfiles/bbcnews.html")
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
        fi = open("./testfiles/bbcnews.html")
        patterns = ["//a","//h1"]
        scr = scraper("test",patterns,self.parser)
        results = scr.parse(fi)
        fi.close()
        assert len(results[0])==161
        assert len(results[1])==161
    
    def testPostProcessor_NOOP(self):
        p = postprocessor()
        assert p.process("hello world!")=="hello world!"

    def testPostProcessor_Trim(self):
        p = trimwhitespace()
        assert p.process("  hello\t   world!\r\n")=="hello world!"
        
    def testPostProcessor_ToLower(self):
        p = lowercase()
        assert p.process("HellO WORLd!")=="hello world!"

    def testPostProcessorExample(self):
        fi = open("./testfiles/bbcnews.html")
        patterns = ["//a","//h1"]
        scr = scraper("test",patterns,self.parser,[lowercase()])
        results = scr.parse(fi)
        for y in range(0,len(patterns)):
            for x in results[y]:
                assert x==x.lower()
        fi.close()
        
    def testWriter(self):
        fi = open("./testfiles/bbcnews.html")
        patterns = ["//a","//h1"]
        output = StringIO.StringIO()
        opwriter=TSVOutput(output)
        scr = scraper("test",patterns,self.parser,[lowercase()],writer=opwriter)
        results = scr.parse(fi)
        assert len(results[0])==161
        assert len(output.getvalue())==3196
    
if __name__ == "__main__":
    unittest.main()