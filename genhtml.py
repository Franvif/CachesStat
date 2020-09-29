# module to generate html

class dochtml:
    """ class for html document generation """

    def __init__(self, typedoc = 'root', content = ''):
        self.typedoc = typedoc
        assert(not(typedoc == 'root' and content != '')), "A root document has no content."
        if typedoc == 'root':
            self.children = []
        elif typedoc == 'text':
            self.content = content
        elif typedoc == 'image':
            self.content = content # path of the image
        elif typedoc == 'array':
            self.content = content # tuple with number of rows and number of columns
            self.children = [] # children are the content of the cells (0--> cell(0,0), 1--> cell(0,1) ...)
        else:
            print("typedoc unknown, unexpected results can happen")


    def addchild(self,fils):
        """ add the child fils to the node """

        assert(type(fils) is dochtml), "addchild waits an argument of type dochtml"
        assert(fils.typedoc != 'root'), "A root document cannot be child"
        self.children.append(fils)


    def writehtmlfile(self, nomfichier=""):
        """ create the html file"""

        if self.typedoc == 'root':
            preamble = "<html>\n  <head>\n    <title>Geocaching stat by Franvif</title>\n" \
                       "    <style>\n      table, th, td {\n      padding: 10px;\n" \
                       "      border: 2px solid black;\n      border-collapse: collapse;\n" \
                       "      }\n    </style>\n" \
                       "  </head>\n  <body>\n"
            postamble = "  </body>\n</html>"
            body = ""
            for doc in self.children:
                body = body + doc.writehtmlfile()
            if nomfichier != "":
                with open(nomfichier,'w') as fid:
                    fid.write(preamble + body + postamble)
            return preamble + body + postamble
        elif self.typedoc == 'text':
            return "    <p>" + self.content + "</p>\n"
        elif self.typedoc == 'array':
            preamble = "<table>\n  <tbody>\n"
            postamble = "  </tbody>\n</table>\n"
            numcell = 0
            nbrows = self.content[0]
            nbcols = self.content[1]
            body = ""
            for doc in self.children:
                if numcell%nbcols == 0: # new row
                    body = body + "    <tr>\n"
                body = body + "      <td>\n        " + doc.writehtmlfile() + "\n      </td>\n"
                if numcell%nbcols == nbcols-1:
                    body = body + "    </tr>\n"
                numcell += 1
            return preamble + body + postamble
        elif self.typedoc == 'image':
            return '<img src="' + self.content + '" />'




