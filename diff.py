#!/usr/bin/python
 # -*- coding: utf-8 -*-
 
"""HTML Diff: http://www.aaronsw.com/2002/diff
Rough code, badly documented. Send me comments and patches.
Modified by Max Gaukler to return valid HTML, but no longer the deleted/old version. Only highlights the new/modified text
"""

__author__ = 'Aaron Swartz <me@aaronsw.com>'
__copyright__ = '(C) 2003 Aaron Swartz. GNU GPL 2 or 3.'
__version__ = '0.22'

import difflib, string,  re

def isTag(x): return x[0] == "<" and x[-1] == ">"

def markAs(cssClass, list):
    out=""
    
    # merge all adjacent non-tags:
    mergedList=[]
    for item in list:
        if isTag(item) or len(mergedList)==0:
            mergedList.append(item)
        else:
            mergedList[-1]+=item
    
    # mark all texts (non-tags)
    for item in mergedList:
        if isTag(item):
            out += item
        else:
            out += '<div class="diff {} ">{}</div>'.format(cssClass, item)
    return out

def textDiff(a, b):
    """Takes in strings a and b and returns a human-readable HTML diff."""

    out = []
    a, b = html2list(a), html2list(b)
    try: # autojunk can cause malformed HTML, but also speeds up processing.
        s = difflib.SequenceMatcher(None, a, b, autojunk=False)
    except TypeError:
        s = difflib.SequenceMatcher(None, a, b)
    for e in s.get_opcodes():
        # debug: print e,  a[e[1]:e[2]],  b[e[3]:e[4]]
        if e[0] == "replace":
            # @@ need to do something more complicated here
            # call textDiff but not for html, but for some html... ugh
            # gonna cop-out for now
            out.append(markAs("ins modified", b[e[3]:e[4]]))
            # out.append('<div class="diff del modified">'+''.join(a[e[1]:e[2]]) + '</div><div class="diff ins modified ">'+''.join(b[e[3]:e[4]])+"</div>")
        elif e[0] == "delete":
            pass
            # out.append('<div class="diff del">'+ ''.join(a[e[1]:e[2]]) + "</div>")
        elif e[0] == "insert":
            out.append(markAs("ins",b[e[3]:e[4]]))
        elif e[0] == "equal":
            out.append(''.join(b[e[3]:e[4]]))
        else: 
            raise "Um, something's broken. I didn't expect a '" + `e[0]` + "'."
    return ''.join(out)

def html2list(x, b=0):
    mode = 'char'
    cur = ''
    out = []
    for c in x:
        if mode == 'tag':
            if c == '>': 
                if b: cur += ']'
                else: cur += c
                out.append(cur); cur = ''; mode = 'char'
            else: cur += c
        elif mode == 'char':
            if c == '<': 
                out.append(cur)
                if b: cur = '['
                else: cur = c
                mode = 'tag'
            elif c in string.whitespace: out.append(cur+c); cur = ''
            else: cur += c
    out.append(cur)
    return filter(lambda x: x is not '', out)

if __name__ == '__main__':
    import sys
    try:
        a, b = sys.argv[1:3]
    except ValueError:
        print "htmldiff: highlight the differences between two html files"
        print "usage: " + sys.argv[0] + " a b"
        sys.exit(1)
        
    
    astr=open(a).read()
    bstr=open(b).read()
    
    # Hacks to make etherpad output better
    # headings are missing in export, reconstruct:
    astr=re.sub("<br>\*([^<>]*)<br>", lambda x: "<h1>"+x.group(1)+"</h1><br>",  astr)
    bstr=re.sub("<br>\*([^<>]*)<br>", lambda x: "<h1>"+x.group(1)+"</h1><br>",  bstr)
    diff=textDiff(astr, bstr)
    
    # style
    diff=diff.replace("font-size: 13px;", "")
    diff=diff.replace("line-height: 17px;", "")
    diff=diff.replace('</head>','<style>'
        'body, .normal {color:gray}'
        'ul, ol { margin-left:0; padding-left:1.5em;}'
        'li { margin-left:0; padding-left:0;} '
        'div.ins { color:black; background:#bfb; display:inline; } '
        '.ins * { background:#bfb; }'
        '.del { color:red; background:#fcc; display:none; } .del * { background:#fcc; }'
        '.modified.ins { background:#ffc;  }'
        '  </style></head>'
        )
    headingText='<div style="color:black; font-weight:bold;line-height:2em;margin-bottom:2em;"> Dokument: {}, Vergleich mit: {}  <br>Farben: <div class="diff ins">Eingefügt</div>, <div class="diff ins modified">Bearbeitet</div>, <span class="normal">Unverändert</span>. Gelöschtes wird nicht angezeigt.</div>'.format(b, a)
    diff=re.sub("(<body[^<>]*>)", lambda x: x.group(1)+headingText  ,diff)
    print diff
    
    
