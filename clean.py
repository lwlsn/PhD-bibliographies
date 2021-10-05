# perform some tests on ped.bib related to the pdf-directory (pdfdir)
# activate one or more tests by setting those control variables to 1

# 1. is_check_file: check objects with no or empty file entry
# 2. is_check_double_file: check if two or more different objects have the same pdf entry
# 3. is_check_unused_files: check <pdfdir> for unsused files

import os, sys, glob, copy
from os import path, access, R_OK  # W_OK for write permission.
from operator import itemgetter

#-------- control parameter ---------
is_check_file = 0
is_check_double_file = 0
is_check_unused_files = 1
#------------------------------------   

ROOT = os.getenv("HOME") # Home directory
#ROOT = path.expanduser("~") # works on all platforms  

pdfdir = ROOT + '/lit/pdf/'
print 'pdfdir', pdfdir
debug = 0 # shutdown debug/info messages

bib_data = open('ped.bib')

words = ['author', 'title', 'journal', 'year', 'volume', 'comment', 'issue', 'owner', 'file', 'timestamp', 'booktitle', 'editor', 'publisher', 'number', 'part', 'keywords', 'doi', 'month', 'organization', 'url']
#------------------------------------------------------------------------------

def check_missing_pdf(element):
    """
    following testes:
    1. element has no file entry
    2. element has empty file entry
    3. element has file entry with inexistant pdf-file
    """
    #check missing files
    if not element.has_key('file'): # element has no file
        print >>sys.stderr, '==== %s has no file entry'%element.get('key')
    elif not element.get('file'):  # .. or file is empty
            print >>sys.stderr, '**** %s has empty file entry'%element.get('key')
    else:
        # we have a file entry -----> check its existance in the pdf dir
        pdffile = pdfdir + element.get('file')
        if not( path.exists(pdffile) and path.isfile(pdffile) and access(pdffile, R_OK)):
            print >>sys.stderr, '#### %s with file entry [%s]: Either file is missing or is not readable'%(element.get('key'), element.get('file'))

#------------------------------------------------------------------------------

def check_doubles(elements):
    """
    check if two or more different objects have the same pdf-file 
    """
    doubles = {}
    for element in elements:
        pdffile = element.get("file")
        key = element.get("key")
        if not doubles.has_key(pdffile):
            doubles[pdffile] = [key]
        else:
            doubles[pdffile].append(key)
    for f, k in doubles.iteritems():
        if f and len(k) > 1: # if f excludes case f == None
            print >>sys.stderr, "Keys:", k, "have the same file <%s>"%f
#------------------------------------------------------------------------------

def check_unused_files(elements):
    """
    check dir pdfdir ("lit/pdf") for pdf-files that are not used
    in the ped.bib
    """
    pdf_files = glob.glob( pdfdir + "*.pdf") # pdfs in lit/pdf/
    dummy_files = copy.copy(pdf_files) # list of unused files
    for pdf in pdf_files:
        for element in elements:
            element_pdf =  element.get("file")
            if element_pdf is None:
                continue
            element_pdf = path.basename(element_pdf)

            if path.basename(pdf) == element_pdf:
                dummy_files.remove(pdf)
                break # check next files

    if dummy_files:
        print >>sys.stderr, "%d files are not used:"%len(dummy_files)
        for f in dummy_files:
            print >>sys.stderr, "---->",path.basename(f)
#------------------------------------------------------------------------------

def putWord(string, dic, line):
    """
    extract from <line> the value of the key <string> and put it in  <dic>
    """
    tmp = line[1].strip(' { } , .').split(':')
    # some files are like this :llll:aaaa. So tmp[0] is here == ''
    if not tmp[0]: 
        dic[string] = tmp[1]
    else:
        dic[string] = tmp[0]
#------------------------------------------------------------------------------

def getElement(f):
    """
    get ONE element from file f.
    return dict
    """
    dic = {}
    for line in f:
        line = line.strip(' \n\r')
        if not line:
            continue
        #get <key> and <type>
        if line[0] == '@':
            sline = line.split('{')
            typ = sline[0][1:]
            if typ == 'comment': # ignore jabref-meta
                continue
            dic['type'] = typ.strip(',') 
            key = sline[1].strip(',')
            if debug:
                print >> sys.stderr, '--------> type: <%s>'%typ
                print >> sys.stderr, '--------> key: <%s>'%key
            dic['key'] = key

        line = line.split('=')

        for word in words:
            if line[0].strip(' ') == word:
                putWord(word, dic, line)
                if debug:
                    print  >> sys.stderr, '--------> %s: <%s>'%(word, line[1].strip(' { },.') ) 

        # check for last line of element
        if line[0] == '}':
            if debug:
                print >> sys.stderr, '---------------------------------'
            return dic
#------------------------------------------------------------------------------


#----------------------- get content of file in elements ------------------------------
elements = []
while True:
    dic = getElement(bib_data) 
    if not dic:
        sorted(elements, key=itemgetter('key')) 
        break
    elements.append( dic )
#------------------------------------------------------------------------------

if is_check_file:
    print "check missing files ..."
    for element in elements:
        check_missing_pdf(element)

if is_check_double_file:
    print "check double files ..."
    check_doubles(elements)

if is_check_unused_files:
    print "is_check_unused_files ..."
    check_unused_files(elements)
