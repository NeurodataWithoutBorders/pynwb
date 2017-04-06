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
    Helper class for generating an RST document

    :ivar document: The string with the RST document
    :ivar newline: Newline string
    """

    def __init__(self):
        """Initalize empty RST document"""
        self.document = ""
        self.newline = "\n"

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
        self.document += '    ' + '    '.join(code_block.splitlines(True))  # Add 4-space indent to code_block
        self.document += self.newline
        self.document += self.newline

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
