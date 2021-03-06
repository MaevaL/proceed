#!/usr/bin/python
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#         ___    __    ___    ___  ____  ____   __
#         |  \  |  \  |   |  /     |     |     |  \   Automatic
#         |__/  |__/  |   |  |     |__   |__   |   |    Conference
#         |     |\_   |   |  |     |     |     |   |    Proceedings
#         |     |  \  |___|  \___  |___  |___  |__/   Generator
#        ==========================================================
#
#           http://www.lpl-aix.fr/~bigi/
#
# ---------------------------------------------------------------------------
# developed at:
#
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2013-2014  Brigitte Bigi
#
#       Use of this software is governed by the GPL, v3
#       This banner notice must not be removed
# ---------------------------------------------------------------------------
#
# SPPAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPPAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPPAS. If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------

import codecs
import re
import datetime
from DataIO.Documents.style import documentsLaTeXStyle, documentsProp

# ---------------------------------------------------------------------------

class LaTeXWriter:
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL
    @summary: Write documents, one per LaTeX file with title, authors, abstract, or
    all documents title/authors in a single LaTeX file.

    To do: some <span> in abstracts are not properly removed.

    """

    def __init__( self, docprops, status=1 ):
        self.docProp  = docprops
        self._status  = status
        self._compiler = "LATEX"
        self._style    = documentsLaTeXStyle()


    def change_style(self, stylename):
        if stylename.lower().strip() == "taln":
            self._style.set_taln()
        elif stylename.lower().strip() == "amlap":
            self._style.set_amlap()
        else:
            self._style.set_simple()


    def write_as_list( self, docs, filename ):
        with codecs.open ( filename , 'w' , 'utf-8') as fp:

            self.__write_header(fp)
            self.__write_style(fp)
            self.__write_separator(fp)
            self.__write_begindoc(fp)
            fp.write('\\begin{tabular}{ll}\n')
            for doc in docs:
                if doc.get_status()==self._status:
                    for auth in doc.get_authors():
                        fp.write(self.__format(auth.get_lastname())+' '+self.__format(auth.get_firstname())+', ')
                    fp.write(' & ')
                    fp.write(doc.get_title())
                    fp.write(' \\\\ \n')
                    fp.write('\n')
            fp.write('\\end{tabular}\n')
            self.__write_end(fp)


    def write_doc( self, doc , filename ):
        with codecs.open ( filename , 'w' , 'utf-8') as fp:

            self.__write_header(fp,doc.get_docid())
            self.__write_properties(fp)
            self.__write_style(fp)
            self.__write_separator(fp)
            self.__write_title(fp,doc.get_title())
            self.__write_authors(fp,doc)
            self.__write_separator(fp)
            self.__write_begindoc(fp)
            self.__write_maketitle(fp)
            if len(doc.get_keywords()) > 0:
                fp.write('\\keywords{ ')
                self.__write_keywords(fp,doc.get_keywords())
                fp.write('}\n')
                fp.write('\\abstract{}\n')
            self.__write_abstract(fp,doc.get_abstract())
            self.__write_end(fp)


    def __write_separator(self,fp):
        fp.write('% % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % %\n')


    def __write_header(self,fp,docid=None):
        now = datetime.datetime.now()
        self.__write_separator(fp)
        fp.write('% % Document generated automatically                                      % %\n')
        if docid is not None:
            fp.write('% % Abstract submission number '+str(docid)+ '                                      % %\n')
        fp.write('% % '+str(now.year)+'-'+str(now.month)+'-'+str(now.day)+'                                                             % %\n')
        self.__write_separator(fp)
        fp.write('\n')
        fp.write('\documentclass['+self.docProp.GetFontSize()+']{article}\n')
        fp.write('\n')

        ## Fix included package depending the compiler (and the encoding...)
        if self._compiler == "LATEX":
            fp.write('\usepackage['+self.docProp.GetEncoding()+'x]{inputenc}\n')
            fp.write('\usepackage[T1]{fontenc} %% get hyphenation and accented letters right\n')
            fp.write('\n')
            fp.write('\usepackage[pdftex]{graphicx}\n')
            fp.write('\usepackage{amsfonts}\n')
            fp.write('\usepackage{amssymb}\n')
            fp.write('\usepackage{amsmath}\n')
            fp.write('\usepackage{mathptmx}        %% use fitting times fonts also in formulas\n')
        elif self._compiler == "XELATEX":
            fp.write('\usepackage{fontspec}       %% we will use a specific font\n')
            fp.write('\usepackage{xunicode}       %% this file is UTF8 \n')
            fp.write('\usepackage{lmodern}        %%  \n')
            fp.write('\setmainfont{Times New Roman} \n')
            #fp.write('\setmainfont{DejaVu Serif}  %%  \n')
            #fp.write('\setmainfont{WenQuanYi Zen Hei Sharp}  %% The choosed font \n')
            fp.write('\n')
        else:
            raise Exception('Unknown compiler')
        fp.write('\usepackage{authblk}\n')
        fp.write('\usepackage{tipa}\n')
        fp.write('\n')

        self.__write_separator(fp)
        fp.write('\n')


    def __write_properties(self,fp):
        fp.write('% % set margins\n')
        fp.write('\usepackage['+self.docProp.GetPaperSize()+',')
        fp.write('left='+str(self.docProp.GetMargins().GetLeft())+'mm,')
        fp.write('right='+str(self.docProp.GetMargins().GetRight())+'mm,')
        fp.write('top='+str(self.docProp.GetMargins().GetTop())+'mm,')
        fp.write('bottom='+str(self.docProp.GetMargins().GetBottom())+'mm,')
        fp.write('noheadfoot]{geometry}\n')
        fp.write('\n')
        fp.write('% % paragraph indentation\n')
        fp.write('\setlength{\parindent}{'+str(self.docProp.GetParindent())+'cm}\n')
        fp.write('\setlength{\parskip}{'+str(self.docProp.GetParskip())+'pt}\n')
        fp.write('\n')
        fp.write('% % no page numbers\n')
        fp.write('\\renewcommand\\thepage{}\n')
        fp.write('\n')


    def __write_style(self,fp):
        fp.write('% % fix title style\n')
        fp.write('\let\LaTeXtitle\\title\n')
        fp.write(self._style._title + '\n')
        #fp.write('\\renewcommand{\\title}[1]{\LaTeXtitle{\Large\\textsf{\\textbf{#1}}}}\n')
        fp.write('\n')
        fp.write('% % Fix authors style\n')
        fp.write(self._style._authors + '\n')
        #fp.write('\\renewcommand\Authfont{\scshape\small}\n')
        # Remove the "AND" between authors, replace by a comma
        fp.write('\\renewcommand\Authsep{, }\n')
        fp.write('\\renewcommand\Authand{, }\n')
        fp.write('\\renewcommand\Authands{, }\n')
        fp.write('\n')
        fp.write('% % Fix affiliation style\n')
        fp.write(self._style._labos + '\n')
        #fp.write('\\renewcommand\Affilfont{\itshape\small}\n')
        fp.write('\setlength{\\affilsep}{1em}\n')
        fp.write('\n')
        fp.write('% % fix e-mail style\n')
        #fp.write('\\newcommand{\emailaddress}[1]{\\newline{\sf#1}}\n')
        fp.write(self._style._email + '\n')
        fp.write('\n')
        fp.write('% % fix keywords style\n')
        fp.write('\\newcommand{\smalllineskip}{\\baselineskip=15pt}\n')
        fp.write(self._style._keywords + '\n')
        #fp.write('\\newcommand{\keywords}[1]{\\noindent{\small{\\textit{Keywords}: }#1\par \\vskip.7\\baselineskip}}\n')
        fp.write('\n')
        fp.write(self._style._abstract + '\n')
        fp.write('\\renewcommand\paragraph[1]{\\vspace{1em}{\\bfseries #1}}\n\n')


    def __write_title(self,fp,title): # title is a string
        fp.write('\n')
        fp.write('% % Fix title\n')
        fp.write('\\title{'+unicode(self.__format(title))+'}\n')
        fp.write('\date{}\n')
        fp.write('\n')


    def __write_authors(self,fp,doc): # authors is a list of authors instances
        fp.write('% % Fix authors then affiliation and email for each author\n')
        i = 0
        for auth in doc.get_authors():
            i = i+1
            fp.write('\\author['+str(i)+']{'+self.__format(auth.get_firstname())+' '+self.__format(auth.get_middlename())+' '+self.__format(auth.get_lastname())+'}\n')
        i = 0
        for auth in doc.get_authors():
            i = i+1
            for lab in auth.get_labos():
                labo = doc.get_laboratory()[int(lab)]
                fp.write('\\affil['+str(i)+']{')
                fp.write(unicode(self.__format(labo.get_nom()))+', ')
                fp.write(unicode(self.__format(labo.get_address()))+' ')
                fp.write(unicode(self.__format(labo.get_country()))+' ')
                fp.write('\emailaddress{'+unicode(self.__format(auth.get_email())))
                fp.write('}}\n')


    def __write_begindoc(self,fp):
        fp.write('\n')
        fp.write('% % BEGIN DOCUMENT % %\n')
        fp.write('\\begin{document}\n')
        fp.write('\n')


    def __write_maketitle(self,fp):
        fp.write('% % MAKE THE TITLE\n')
        fp.write('\maketitle\n')
        fp.write('\n')


    def __write_keywords(self,fp,kwds): # kwds is a list of strings
        for kwidx in range(len(kwds)-1):
            fp.write(unicode(self.__format(kwds[kwidx])))
            fp.write(', ')
        fp.write(unicode(self.__format(kwds[len(kwds)-1])))


    def __write_abstract(self,fp,abstract): # abstract is a string
        fp.write('% % ABSTRACT CONTENT\n')
        fp.write('\n')
        # Clean the string
        a = abstract
        # remove HTML comments
        a = re.sub(u'\\<!--[\[\]{}<>"\\/%*#\/!:;,.="\-\'\s\w\xaa-\xff]+-->', ur' ', a, re.UNICODE)
        # remove simple tags
        a = a.replace("<p>", "\n")
        a = a.replace("</p>", "\n\n")
        a = a.replace("<span>", " ")
        a = a.replace("</span>", " ")
        a = a.replace("<div>", " ")
        a = a.replace("</div>", " ")
        a = a.replace("<ul>", "\n\\begin{itemize}\n")
        a = a.replace("</ul>", "\n\\end{itemize}\n")
        a = a.replace("<ol>", "\n\\begin{enumerate}\n")
        a = a.replace("</ol>", "\n\\end{enumerate}\n")
        a = a.replace("<li>", "\n\item")
        a = a.replace("</li>", "\n")
        a = a.replace("<i>", "{\it ")
        a = a.replace("</i>", "}")
        a = a.replace("<b>", "{\\bf ")
        a = a.replace("</b>", "}")
        a = a.replace("<strong>", "{\\em ")
        a = a.replace("</strong>", "}")
        a = a.replace("<br />", "\n")
        a = a.replace('<a target="_blank">', "")
        a = a.replace("</a>", "")
        # remove complex html tags:
        a = a.replace("'Times New Roman',", "")
        a = a.replace("'Times New Roman';", "")
        a = a.replace("Times New Roman,", "")
        a = a.replace("Arial,", "")
        a = a.replace("serif;", "")
        a = a.replace("sans-;", "")
        a = a.replace("mso-spacerun: yes;", "")
        a = a.replace("mso-fareast-font-family:", "")
        a = a.replace("mso-ansi-language: EN-US;", "")
        a = a.replace("mso-ansi-language: EN-GB;", "")
        a = a.replace('<span style="font-size: small;">', '')
        a = a.replace('<span style="">', '')
        a = a.replace('<span style="font-family: ">', '')
        a = a.replace('<span style="text-decoration: underline;">', '')
        a = re.sub(u'<span style="font-family:[\s ]*">', ur' ', a, re.UNICODE)
        a = re.sub(u'<span style="font-size: [\-\s\w\xaa-\xff]+;">', ur' ', a, re.UNICODE)
        a = re.sub(u'<span style="text-decoration: [;\-\s\w\xaa-\xff]+">', ur' ', a, re.UNICODE)
        a = re.sub(u'<span style="color: ["#;\-\s\w\xaa-\xff]+>', ur' ', a, re.UNICODE)
        a = re.sub(u'<p align=["\s\w\xaa-\xff]+>', ur' ', a, re.UNICODE)
        # Then, normalize the string
        a = self.__format(a)
        # finally: write!
        fp.write(unicode(a))
        fp.write('\n')


    def __write_end(self,fp):
        fp.write('\n')
        fp.write('% % END DOCUMENT % %\n')
        fp.write('\end{document}\n')
        fp.write('% % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % %\n')
        fp.write('\n')


    def __write_figure(self,fp,filename):
        ##NOT USED FOR NOW!
        fp.write('\n')
        fp.write('% % FIGURE\n')
        fp.write('\\begin{figure}[h]\n')
        fp.write('   \centerline{\includegraphics[width=0.8\\textwidth]{'+filename+'}}\n')
        fp.write('\end{figure}\n')
        fp.write('\n')


    def __format(self,s):
        a = s.replace("_", "\_")
        a = a.replace("%", "\%")
        a = a.replace("&", "\&")
        a = a.replace("#", "\#")
        a = a.replace("^", "\^{}")
        a = a.replace("\s", " ")
        a = re.sub(u' ', u" ", a, re.UNICODE)   # espace insecable
        a = re.sub(u'　', u" ", a, re.UNICODE)  # espace insecable version 2!
        a = re.sub(u' ­­', u" ", a, re.UNICODE) # espace insecable version 3!
        a = re.sub(u"ʼ", u"'", a, re.UNICODE)   # apostrophe
        a = re.sub(u"‘", u"'", a, re.UNICODE)   # apostrophe
        a = re.sub(u"É", u"\\'e", a, re.UNICODE)   #
        a = re.sub(u"é", u"\\'e", a, re.UNICODE)   #
        a = re.sub(u"è", u"\\`e", a, re.UNICODE)   #
        a = re.sub(u"ë", u'\\"e', a, re.UNICODE)   #
        a = re.sub(u"ê", u"\\^e", a, re.UNICODE)   #
        a = re.sub(u"à", u"\\`a", a, re.UNICODE)   #
        a = re.sub(u"â", u"\\^a", a, re.UNICODE)   #
        a = re.sub(u"ã", u"\\~a", a, re.UNICODE)   #
        a = re.sub(u"î", u"\\^i", a, re.UNICODE)   #
        a = re.sub(u"ï", u'\\"i', a, re.UNICODE)   #
        a = re.sub(u"í", u"\\'i", a, re.UNICODE)
        a = re.sub(u"ù", u"\\`u", a, re.UNICODE)   #
        a = re.sub(u"ü", u'\\"u', a, re.UNICODE)
        a = re.sub(u"ú", u"\\'u", a, re.UNICODE)
        a = re.sub(u"ç", u"\\c{c}", a, re.UNICODE)   #
        a = re.sub(u"ô", u"\\^o", a, re.UNICODE)   #
        a = re.sub(u"ó", u"\\'o", a, re.UNICODE)
       
        a = re.sub(u"–", u"-", a, re.UNICODE)
        a = re.sub(u"’", u"'", a, re.UNICODE)   # apostrophe
        a = re.sub(u"ˈ", "'", a, re.UNICODE)
        a = re.sub(u'´', "'", a, re.UNICODE)
        
        a = re.sub(u"é", u"\\'e", a, re.UNICODE)
        a = re.sub(u"è", u"\\`e", a, re.UNICODE)
        a = re.sub(u"à", u"\\`a", a, re.UNICODE)
        a = re.sub(u"ã", u"\\~a", a, re.UNICODE)
        a = re.sub(u"û", u"\\^u", a, re.UNICODE)
        a = re.sub(u"ú", u"\\'u", a, re.UNICODE)
        a = re.sub(u"â", u"\\^a", a, re.UNICODE)
        a = re.sub(u"á", u"\\'a", a, re.UNICODE)
        a = re.sub(u"ç", u"\\c{c}", a, re.UNICODE)   #
        a = a.replace(u'≤', '$\leq$')
        a = a.replace(u'‐', '--')
        a = a.replace(u'ﬂ', 'fl')
        a = a.replace(u'í', "\\'i")
        
        a = a.replace(u'η', "$\eta$") # grec
        
        a = a.replace(u'ɛ̃','\\textipa{\~E}')
        a = a.replace(u'ɑ̃','\\textipa{\~A}')
        a = a.replace(u'ɐ̃','\\textipa{\~5}')
        a = a.replace(u'Ā', '\\textipa{\=A}')
        a = a.replace(u'Ē', '\\textipa{\=E}')
        a = a.replace(u'Ī', '\\textipa{\=I}')
        a = a.replace(u'Ō', '\\textipa{\=O}')
        a = a.replace(u'Ū', '\\textipa{\=U}')
        a = a.replace(u'Ă', '\\textipa{\\v{A}}')
        a = a.replace(u'Ĕ', '\\textipa{\\v{E}}')
        a = a.replace(u'Ĭ', '\\textipa{\\v{I}}')
        a = a.replace(u'Ŏ', '\\textipa{\\v{O}}')
        a = a.replace(u'Ŭ', '\\textipa{\\v{U}}')
        a = a.replace(u'Ṽ','\\~V')
        a = a.replace(u'i͂','\\~i')
        a = a.replace(u'w̃','\\~w')
        a = a.replace(u'j̃','\\~j')

        a = a.replace(u'ɨ', "\\textipa{1}") # IPA
        a = a.replace(u'ʃ','\\textipa{S}')
        a = a.replace(u'ʝ','\\textipa{J}')
        a = a.replace(u'ɛ','\\textipa{E}')
        a = a.replace(u'æ','\\textipa{\\ae}')
        a = a.replace(u'ɾ','\\textipa{R}')
        a = a.replace(u'ɹ','\\textipa{\*r}')
        a = a.replace(u'ɻ','\\textipa{\:r}')
        a = a.replace(u'ʎ','\\textipa{L}')
        a = a.replace(u'ə','\\textipa{@}')
        a = a.replace(u'ɑ','\\textipa{A}')
        a = a.replace(u'ɔ','\\textipa{O}')
        a = a.replace(u'ʒ','\\textipa{Z}')
        a = a.replace(u'ʀ','\\textipa{\;R}')
        a = a.replace(u'ʁ','\\textipa{K}')
        a = a.replace(u'ʔ','\\textipa{P}')
        a = a.replace(u'ø','\\textipa{\o}')

        return a

