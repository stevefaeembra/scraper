'''
Created on 26 Apr 2013

@author: steven
'''

from lxml import etree
from io import BytesIO

class scraper(object):
    
    def __init__(self,name,XPathpatterns,parser):
        self.XPathPatterns=XPathpatterns
        self.name=name
        self.parser=parser
        self._checkPatterns()
        
    def _checkPatterns(self):
        if not self.XPathPatterns or len(self.XPathPatterns)==0:
            raise Exception("No XPath expressions passed to scraper")
        junk = BytesIO("<root>data</root>")
        tree = etree.parse(junk, self.parser)
        for query in self.XPathPatterns:
            try:
                tree.xpath(query)
            except etree.XPathError:
                mess = "%s is not a valid XPath Expression" % query
                raise Exception(mess)
        return True
    
    def parse(self,file_like_object):
        flo=file_like_object
        tree = etree.parse(flo, self.parser)   
        root = tree.getroot()
        results=[]
        for query in self.XPathPatterns:
            allmatching= tree.xpath(query)
            result=[]
            for x in allmatching:
                if x.text:
                    z = x.text.encode('utf-8')
                    z = z.replace("\r\n","")
                    if (len(z)>0):
                        result.append(z)
                    else:
                        result.append("")
            results.append(result)
        return self._padListsToEqualLength(results)
        
    def _padListsToEqualLength(self,listoflists):
        maxlen = max([len(x) for x in listoflists])
        for x in range(0,len(listoflists)):
            while (len(listoflists[x])<maxlen):
                listoflists[x].append("-")
        return listoflists