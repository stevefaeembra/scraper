'''
Simple XPath-based HTML/XML scraper utility class
Created on 26 Apr 2013

@author: steven
'''

from lxml import etree
from io import BytesIO
import re
import sys

'''
simple pluggable postprocessor classes
'''

class postprocessor(object):
       
    def process(self,stringinput):
        return stringinput
    
class trimwhitespace(postprocessor):
    
    ''' remove redundant whitespaces from HTML i.e. newline, tab, duplicate spaces '''
    
    def process(self,stringinput):
        s = stringinput
        s = s.lstrip()
        s = s.replace("\r\n","\n")
        s = s.replace("\n","")
        s = re.sub("\s{2,}", " ", s)
        return s

class lowercase(postprocessor):
    
    def process(self,stringinput):
        return stringinput.lower()


'''
Writer classes
These should take a list of lists of matches, and output them somehow
Only one per scraper
'''

class outputprocessor(object):
    
    def __init__(self,file_like_object):
        self.op = file_like_object
        
    def write(self,list_of_results):
        pass
        
class NullOutput(outputprocessor):
    
    def __init__(self,file_like_object):
        super(NullOutput,self).__init__(file_like_object)
        
    def write(self,listofresults):
        pass
    
class TSVOutput(outputprocessor):
    
    def __init__(self,file_like_object):
        super(TSVOutput,self).__init__(file_like_object)
        
    def write(self,list_of_results):
        ncols = len(list_of_results)
        nrows = len(list_of_results[0])
        for rownum in range(0, nrows-1):
            row=[]
            for colnum in range(0,ncols-1):
                row.append(list_of_results[colnum][rownum])
            rowtext = "%s\n" % ("\t".join(row))
            self.op.write(rowtext)

'''
Scraper class

When you create, you need to provide the following:- 
- name
- list of XPath patterns
- an instance of an XML parser
- [optional] a list of postprocessor instances. These will be called in order provided on the text of each match.
- an output (file-like object), defaults to sys.stdout
- [option]
'''
    
class scraper(object):
    
    def __init__(self,name,XPathpatterns,parser,postprocessors=[],output=sys.stdout,writer=None):
        self.XPathPatterns=XPathpatterns
        self.name=name
        self.parser=parser
        self.postprocessors=postprocessors
        self.op=output
        if not writer:
            self.writer=NullOutput(self.op)
        else:
            self.writer=writer
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
        '''
        pass in a file-like object, e.g. sys.stdin, a file, BytesIO etc.
        returns a list of one or more lists of matching values
        these lists will be padded to be of equal length
        '''
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
                    z = self._runThroughPostProcessing(z)
                    if (len(z)>0):
                        result.append(z)
                    else:
                        result.append("")
            results.append(result)
        processedresults = self._padListsToEqualLength(results)
        self.writer.write(processedresults)
        return processedresults
    
    def _runThroughPostProcessing(self,matchingtext):
        for processor in self.postprocessors:
            matchingtext = processor.process(matchingtext)
        return matchingtext
        
    def _padListsToEqualLength(self,listoflists):
        '''
        Ensures that N lists are padded so that they are all the same length,
        equal to the length of the longest of these lists
        '''
        maxlen = max([len(x) for x in listoflists])
        for x in range(0,len(listoflists)):
            while (len(listoflists[x])<maxlen):
                listoflists[x].append("-")
        return listoflists