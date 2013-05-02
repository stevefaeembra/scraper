# encoding: utf-8
'''
Simple Scraper

    A trivial HTML/XML scraper written in Python, designed to be used as a shell script -
    reads in from stdin, writes to stdout.

    You provide one (or more) XPath expressions. 

    If more than one expression is supplied, it is assumed that you are attempting to 
    scrape rows from a table, and the results go into a list of lists, with values held
    column-wise. 
    
    If any of these column lists are shorter than the longest column list, 
    they are padded out. If this happens, you should not assume that the Nth entry in each
    list correspond to a single coherent row. If you use the optional -w/--warn option, it
    will not pad the shorter lists and will throw an exception. This should be used if you need 
    to make sure that the CSV/TSV output is consistent

 Prerequisites
 
   Requires lxml to be installed (http://lxml.de/)

 Copyright 2013 Steven Kay

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''


from lxml import etree
from io import BytesIO
import re
import sys
import os
from lxml import etree
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from lxml.html import *
from xml.etree.ElementTree import *

'''
Simple pluggable postprocessor classes
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
        print listofresults
    
class TSVOutput(outputprocessor):
    
    def __init__(self,file_like_object):
        super(TSVOutput,self).__init__(file_like_object)
        
    def write(self,list_of_results):
        ncols = len(list_of_results)
        nrows = len(list_of_results[0])
        for rownum in range(0, nrows-1):
            row=[]
            for colnum in range(0,ncols):
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
- [optional] an instance of outputprocessor
'''
    
class scraper(object):
    
    def __init__(self,name,XPathpatterns,parser,postprocessors=[],output=sys.stdout,writer=None,padwarning=False):
        self.XPathPatterns=XPathpatterns
        self.name=name
        self.parser=parser
        self.postprocessors=postprocessors
        self.op=output
        self.padwarning=False
        if not padwarning:
            self.givepadwarning=False
        else:
            self.givepadwarning=padwarning
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
                    #print "Found [%s]" % z
                    if (len(z)>0):
                        result.append(z)
                    else:
                        result.append("")
            results.append(result)
        processedresults = self._padListsToEqualLength(results)
        if self.padwarning and self.givepadwarning:
            raise Exception("Padding warning - expressions dont result in consistent numbers of matches")
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
                self.padwarning=True
                listoflists[x].append("-")
        return listoflists
    
    
class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "Error: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def getparserinstancefor(type_name):
    typename=type_name[0].lower()
    if typename=="html":
        return etree.HTMLParser()
    if typename=="xml":
        return etree.XMLParser()
    raise CLIError("Parser option should be one of html,xml")
    

def getformatinstancefor(format_name):
    if not format_name:
        raise CLIError("Format option not supplied")
    format=format_name[0].lower()
    if format=="tsv":
        return TSVOutput(sys.stdout)
    raise CLIError("Format option not recognised")

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''
    
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    try:
        parser = ArgumentParser(description="scraper.py", formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-m", "--match", dest="patterns", action="store", nargs="+", help="One or more XPath expressions to match")
        parser.add_argument("-t", "--text", dest="textmode", action="store_true", help="effect is to implicitly append /text()")
        parser.add_argument("-p", "--parser", dest="parser", action="store", nargs=1, help="parser to use, one of {html,xml,html5}")
        parser.add_argument("-f", "--format", dest="format", action="store", nargs=1, help="output format to use, one of {tsv,csv}")
        parser.add_argument("-w", "--warning", dest="padwarning", action="store_true", help="throw exception if the number of matches for each pattern varies")
        
        args = parser.parse_args()
        
        patterns = args.patterns
        if not patterns:
            raise CLIError("You need to provide one or more XPath expressions using -m")
        givepadwarning = args.padwarning
        textmode = args.textmode
        parser = getparserinstancefor(args.parser)
        formatter = getformatinstancefor(args.format)
        
        scr = scraper("Untitled",patterns,parser,postprocessors=[],output=sys.stdout,writer=formatter,padwarning=givepadwarning)
        scr.parse(sys.stdin)
        return 0
    
    except KeyboardInterrupt:
        return 0
    
    except Exception, e:
        sys.stderr.write(repr(e.message) + "\n")
        sys.stderr.write("for help use --help\n")
        return 2

if __name__ == "__main__":
    sys.exit(main())