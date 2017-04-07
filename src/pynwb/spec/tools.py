from .spec import GroupSpec, SpecCatalog


class SpecFormatter(object):
    """
    Helper class for formatting spec documents
    """
    @staticmethod
    def spec_to_json(spec, pretty=False):
        """
        Convert a given specification to json.

        :param spec: Specification data structure
        :type spec: GroupSpec, DatasetSpec, AttributeSpec, LinkSpec

        :param pretty: Should a pretty formatting be used when encoding the JSON.

        :return: JSON string for the current specification
        """
        import json
        if pretty:
            return json.dumps(spec, sort_keys=True, indent=4, separators=(',', ': '))
        else:
            return json.dumps(spec)

    @staticmethod
    def spec_to_yaml(spec):
        """
        Convert a given specification to yaml.

        :param spec: Specification data structure
        :type spec: GroupSpec, DatasetSpec, AttributeSpec, LinkSpec

        :return: YAML string for the current specification
        """
        import json
        try:
            from ruamel import yaml
        except:
            import yaml
        clean_spec = json.loads(SpecFormatter.spec_to_json(spec, pretty=True))
        return yaml.dump(clean_spec, default_flow_style=False)

    @classmethod
    def spec_to_rst(cls, spec):
        """
        Create an RST document for the given spec

        :param spec: Specification data structure
        :type spec: GroupSpec, DatasetSpec, AttributeSpec, LinkSpec

        :return: RSTDocument for the given spec
        """
        rst_doc = RSTDocument()
        rst_doc.add_spec(spec)
        return rst_doc

    @staticmethod
    def spec_from_file(filenames):
        """
        Generate a SpecCatalog for the fiven list of spec files

        :param filenames: List of YAML/JSON specification files
        :type filenames: List of strings
        :return: SpecCatalog
        """
        try:
            from ruamel import yaml
        except:
            import yaml
        spec_catalog = SpecCatalog()
        for path in filenames:
            with open(path, 'r') as stream:
                for obj in yaml.safe_load(stream):
                    spec_obj = GroupSpec.build_spec(obj)
                    spec_catalog.auto_register(spec_obj)
        return spec_catalog


class RSTDocument(object):
    """
    Helper class for generating an reStructuredText (RST) document

    :ivar document: The string with the RST document
    :ivar newline: Newline string
    """
    ADMONITIONS = ['attention', 'caution', 'danger', 'error', 'hint', 'important', 'note', 'tip', 'warning']
    ALIGN = ['top', 'middle', 'bottom', 'left', 'center', 'right']

    def __init__(self):
        """Initalize empty RST document"""
        self.document = ""
        self.newline = "\n"
        self.default_indent = '    '

    def __get_headingline(self, title, heading_char):
        """Create a headingline for a given title"""
        heading = ""
        for i in range(len(title)):
            heading += heading_char
        return heading

    def add_part(self, title):
        """
        Add a document part heading

        :param title: Title of the reading
        """
        heading = self.__get_headingline(title, '#')
        self.document += (heading + self.newline)
        self.document += (title + self.newline)
        self.document += (heading + self.newline)
        self.document += self.newline

    def add_chapter(self, title):
        """
        Add a document chapter heading

        :param title: Title of the reading
        """
        heading = self.__get_headingline(title, '*')
        self.document += (heading + self.newline)
        self.document += (title + self.newline)
        self.document += (heading + self.newline)
        self.document += self.newline

    def add_section(self, title):
        """
        Add a document section heading

        :param title: Title of the reading
        """
        heading = self.__get_headingline(title, '=')
        self.document += (title + self.newline)
        self.document += (heading + self.newline)
        self.document += self.newline

    def add_subsection(self, title):
        """
        Add a document subsection heading

        :param title: Title of the reading
        """
        heading = self.__get_headingline(title, '-')
        self.document += (title + self.newline)
        self.document += (heading + self.newline)
        self.document += self.newline

    def add_subsubsection(self, title):
        """
        Add a document subsubsection heading

        :param title: Title of the reading
        """
        heading = self.__get_headingline(title, '^')
        self.document += (title + self.newline)
        self.document += (heading + self.newline)
        self.document += self.newline

    def add_paragraph(self, title):
        """
        Add a document paragraph heading

        :param title: Title of the reading
        """
        heading = self.__get_headingline(title, '"')
        self.document += (title + self.newline)
        self.document += (heading + self.newline)
        self.document += self.newline

    def add_code(self, code_block, code_type='python'):
        """
        Add code block to the document
        :param code_block: String with the code block
        :param code_type: The language type to be used for source code highlighting in the rst doc
        """
        self.document += ".. code-block:: %s%s%s" % (code_type, self.newline, self.newline)
        self.document += self.indent_text(code_block)  # Indent text by 4 spaces
        self.document += self.newline
        self.document += self.newline

    def indent_text(self, text, indent=None):
        """
        Helper function used to indent a given text by a given prefix. Usually 4 spaces.

        :param text: String with the text to be indented
        :param indent: String with the prefix to be added to each line of the string. If None then self.default_indent
                       will be used.

        :return: New string with each line indented by the current indent
        """
        curr_indent = indent if indent is not None else self.default_indent
        return curr_indent + curr_indent.join(text.splitlines(True))

    def add_admonitions(self, atype, text):
        """
        Add and admonition to the text. Admonitions are specially marked "topics"
        that can appear anywhere an ordinary body element can

        :param atype: One of RTDDocument.ADMONITIONS
        :param text: The RTD formatted text to be shown or the RTDDocument to be rendered as part of the admonition
        """
        curr_text = text if not isinstance(text, RSTDocument) else text.document
        self.document += self.newline
        self.document += ".. %s::" % atype
        self.document += self.newline
        self.document += self.indent_text(text)
        self.document += self.newline
        self.document += self.newline

    def add_figure(self, img, caption=None, legend=None, alt=None, height=None, width=None, scale=None, align=None, target=None):
        """

        :param img: Path to the image to be shown as part of the figure.
        :param caption: Optional caption for the figure
        :type caption: String or RSTDocument
        :param legend: Figure legend
        :type legend: String or RST Document
        :param alt: Alternate text.  A short description of the image used when the image cannot be displayed.
        :param height: Height of the figure in pixel
        :type height: Int
        :param width: Width of the figure in pixel
        :type width: Int
        :param scale: Uniform scaling of the figure in %. Default is 100.
        :type scale: Int
        :param align: Alignment of the figure. One of RTDDocument.ALIGN
        :param target: Hyperlink to be placed on the image.
        """
        self.document += self.newline
        self.document += ".. figure:: %s" % img
        self.document += self.newline
        if scale is not None:
            self.document += (self.indent_text(':scale: %i' % scale ) + ' %' + self.newline)
        if alt is not None:
            self.document += (self.indent_text(':alt: %s' % alt) + self.newline)
        if height is not None:
            self.document += (self.indent_text(':height: %i px' % height ) + self.newline)
        if width is not None:
            self.document += (self.indent_text(':width: %i px' % width ) + self.newline)
        if align is not None:
            if align not in self.ALIGN:
                raise ValueError('align not valid. Found %s expected one of %s' % (str(align), str(self.ALIGN)))
            self.document += (self.indent_text(':align: %s' % align) + self.newline)
        if target is not None:
            self.document += (self.indent_text(':target: %s' % target) + self.newline)
        self.document += self.newline
        if caption is not None:
            curr_caption = caption if not isinstance(caption, RSTDocument) else caption.document
            self.document += (self.indent_text(curr_caption) + self.newline)
        if legend is not None:
            if caption is None:
                self.document += (self.indent_text('.. ') + self.newline + self.default_indent + self.newline)
            curr_legend = legend if not isinstance(legend, RSTDocument) else legend.document
            self.document += (self.indent_text(curr_legend) + self.newline)
        self.document += self.newline

    def add_sidebar(self, text, title, subtitle=None):
        """
        Add a sidebar. Sidebars are like miniature, parallel documents that occur inside other
        documents, providing related or reference material.

        :param text: The content of the sidebar
        :type text: String or RSTDocument
        :param title: Title of the sidebar
        :type title: String
        :param subtitle: Optional subtitel of the sidebar
        :type subtitle: String
        """
        self.document += self.newline
        self.document += '.. sidebar:: ' + title + self.newline
        if subtitle is not None:
            self.document += (self.indent_text(':subtitle: %s' % subtitle) + self.newline)
        self.document += self.newline
        curr_text = text if not isinstance(text, RSTDocument) else text.document
        self.document += (self.indent_text(curr_text)) + self.newline + self.newline

    def add_topic(self, text, title):
        """
        Add a topic. A topic is like a block quote with a title, or a self-contained section with no subsections.

        :param text: The content of the sidebar
        :type text: String or RSTDocument
        :param title: Title of the sidebar
        :type title: String
        """
        self.document += self.newline
        self.document += '.. sidebar:: ' + title + self.newline
        self.document += self.newline
        curr_text = text if not isinstance(text, RSTDocument) else text.document
        self.document += (self.indent_text(curr_text)) + self.newline + self.newline

    def add_spec(self, spec, show_json=False, show_yaml=False):
        """
        Convert the given spec to RST and add it to the document

        :param spec: Specification data structure
        :param show_json: Show JSON-based spec as part of the RST
        :param show_yaml: Show YAML-based spec as part of the RST
        :type spec: GroupSpec, DatasetSpec, AttributeSpec, LinkSpec
        """
        if show_json:
            self.add_code(SpecFormatter.spec_to_json(spec, True), code_type='python')
        if show_yaml:
            self.add_code(SpecFormatter.spec_to_yaml(spec), code_type='python')

    def write(self, filename, mode='w'):
        """
        Write the document to file

        :param filename: Name of the output file
        :param mode: file open mode
        """
        outfile = open(filename, mode=mode)
        outfile.write(self.document)
        outfile.flush()
        outfile.close()


