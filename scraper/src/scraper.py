# -*- coding: UTF-8 -*- #

'''
Created on 25 Apr 2013
Simple single-page HTML scraper unix tool
Requires lxml to be installed
Pipe in some HTML to stdin, and pass an XPath expression as an argument
Dumps the text content of matching nodes to stdout
example calling script.sh

python /path/to/scraper.py "$@"

e.g. cat path/to/my.html | ./scrape --f ".//a[@class='headline-anchor']" | less

example.showing headlines on BBC news site

cat ~/junk/bbcnews.html | ./scrape --f ".//a[@class='headline-anchor']" | less

@author: steven david kay, 2013
'''

from lxml import etree
import sys
import argparse


def getcommandlineargs():
    pp = argparse.ArgumentParser(description='Simple HTML scraper utility')
    pp.add_argument('--f',nargs='+',help='XPath query(-ies), may have more than one')
    pp.add_argument('--trim',nargs='+',help='Trim strings of whitespace including newlines and tabs')
    pp.add_argument('--relaxed', nargs='*', default='', help='Relaxed mode, lets you parse really badly formed HTML pages')
    args = pp.parse_args(sys.argv[1:])
    return args    
    
def getaparser(args):
    if 'relaxed' in args:
        parser = etree.HTMLParser()
    else:
        parser = etree.XMLParser()
    return parser

def getqueries(args):
    if not args.f:
        print ("Need to provide one or more Xpath expressions! Call with --f [xpath-expression...]")
        sys.exit(-1)
    return args.f


def checkqueriesarevalid(queries,tree):
    # check the expressions are valid
    for query in queries:
        try:
            tree.xpath(query)
        except etree.XPathError:
            print "%s is not a valid XPath Expression" % query
            sys.exit(-1)

def getresults(args,tree):
    results=[]
    if args['trim']:
        trimmer=args.trim
    for query in args.f:
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
    return results

def getlongestlistlength(results):
    lens=[len(list(x)) for x in results]
    maxlen=max(lens)
    return maxlen

def gettreeroot(args,queries):
    parser = getaparser(args)       
    tree = etree.parse(sys.stdin, parser)
    checkqueriesarevalid(queries,tree)   
    root = tree.getroot()
    return (tree,root)

def dumpasTSV(results):
    results=list(results)
    for ix in range(0,maxlen):
        s=[]
        for x in results:
            if (ix<len(x)):
                s.append(x[ix])
            else:
                s.append("-")
        s2="\t".join(s)
        #s2=s2.encode("utf-8")
        print s2
    
if __name__ == "__main__":
    
    try:
        
        args = getcommandlineargs()    
        queries = getqueries(args)        
        tree,root = gettreeroot(args, queries)
        results = getresults(args,tree)
        maxlen = getlongestlistlength(results)
        dumpasTSV(results)
                
    except Exception as ex:
        print ex
        sys.exit(-1)