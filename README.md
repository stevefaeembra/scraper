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
