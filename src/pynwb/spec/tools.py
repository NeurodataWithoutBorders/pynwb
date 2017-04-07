from .spec import GroupSpec, SpecCatalog
from pynwb.core import docval, getargs


class SpecFormatter(object):
    """
    Helper class for formatting spec documents to string
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


class HierarchyDescription(dict):
    """
    Dictionary data structure used in combination with the HierarchyRenderer class to describe the contents
    of the specification or NWB file hierarchy. This simple helper datasstructure was designed to ease the
    use of HiearchyRendered but may be useful for other purposes as well.
    """
    RELATIONSHIP_TYPES = {'managed_by': 'Object managed by',
                          'attribute_of': 'Object is attribute of'}


    def __init__(self):
        super(HierarchyDescription, self).__init__()
        super(HierarchyDescription, self).__setitem__('datasets', [])
        super(HierarchyDescription, self).__setitem__('groups', [])
        super(HierarchyDescription, self).__setitem__('attributes', [])
        super(HierarchyDescription, self).__setitem__('relationships', [])

    def __setitem__(self, key, value):
        raise ValueError("Explicit setting of objects not allowed. Use the add_* functions to add objects")

    def add_dataset(self, name, shape=None, dtype=None, neurodata_type=None):
        """
        Add a dataset to the description

        :param name: Name of the dataset (full path)
        :param shape: Shape of the dataset
        :param dtype: Data type of the data
        :param neurodata_type: NWB neurodata_type
        """
        self['datasets'].append({
            'name': name,
            'shape': shape,
            'dtype': dtype,
            'neurodata_type': neurodata_type

        })

    def add_group(self, name, neurodata_type=None):
        """
        Add a group to the description

        :param name: Name of the group (full path)
        :param neurodata_type: NWB neurodata type
        """
        self['groups'].append({
            'name': name,
            'neurodata_type': neurodata_type
        })

    def add_attribute(self,  name, value):
        """
        Add an attribute

        :param name: Name of the attribute (Full name, including the path of the parent object)
        :param value: Value of the attribute
        :return:
        """
        self['attributes'].append({
            'name': name,
            'value': value
        })

    def add_relationship(self, source, target, name, type):
        """
        Add a relationship between two objects

        :param source: Name of the source object (full path)
        :param target: Name of the target object (full path)
        :param name: Name of the relationship
        :param type: Type of the relationship
        """
        self['relationships'].append({
            'source': source,
            'target': target,
            'name': name,
            'type': type
        })

    @classmethod
    def from_hdf5(cls, hdf_object, root='/'):
        """
        Traverse the file to compute file related statistics, e.g., the number of objects
        of a given type etc.

        :param hdf_object: The h5py.Group or h5py.File object. If a string is given then the function assumes
                           that this is a path to and HDF5 file and will open the file.
        :param root: String indicating the root object starting from which we should compute the file statistics.
                     Default value is "/", i.e., starting from the root itself
        :type root: String

        :return: Instance of HierarchyRendererDescription with the hierarchy of the objects

        """
        import h5py
        import os

        filestats = cls()

        def update_stats(name, obj):
            """
            Callback function used in conjunction with the visititems function to compile
            statistics for the file

            :param name: the name of the object in the file
            :param obj: the hdf5 object itsel
            """
            obj_name = os.path.join(root, name)
            # Group and dataset metadata
            if isinstance(obj, h5py.Dataset):
                filestats.add_dataset(name=obj_name, shape=obj.shape, dtype=obj.dtype)
            elif isinstance(obj, h5py.Group):
                ntype = None
                try:
                    ntype = obj.attrs['neurodata_type'][()]
                except:
                    pass
                filestats.add_group(name=obj_name, neurodata_type=ntype)
            # Visit all attributes of the object
            for attr_name, attr_value in obj.attrs.items():
                attr_path = os.path.join(obj_name, attr_name)
                filestats.add_attribute(name=attr_path, value=attr_value)
                filestats.add_relationship(source=attr_path,
                                           target=obj_name,
                                           name=attr_name + '_attribute_of_' + obj_name,
                                           type='attribute_of')


            # Create the relationship for the object
            if obj_name != '/':
                filestats.add_relationship(source=os.path.dirname(obj_name),
                                           target=obj_name,
                                           name=obj_name + '_managed_by_' + root,
                                           type='managed_by')
        # Determine the main HDF5 object
        if isinstance(hdf_object, str):
            main_hdf_object = h5py.File(hdf_object, 'r')
            close_main_hdf_object = True
        else:
            main_hdf_object = hdf_object
            close_main_hdf_object = False

        # Visit all items in the hdf5 object to compile the object statistics
        main_hdf_object[root].visititems(update_stats)
        if root == '/':
            update_stats(name='/', obj=main_hdf_object['/'])

        # Close the hdf5 object if we opened it
        if close_main_hdf_object:
            main_hdf_object.close()
            del main_hdf_object

        # Return the results
        return filestats


class NXGraphHierarchyDescription(object):
    """
    Description of the object hierarchy as an nx graph
    """

    @docval({'name': 'data', 'type': HierarchyDescription, 'doc': 'Data of the hierarchy'},
            {'name': 'include_groups', 'type': bool, 'doc': 'Bool indicating whether we should include groups in the hiararchy', 'default': True},
            {'name': 'include_datasets', 'type': bool, 'doc': 'Bool indicating whether we should include datasets in the hiararchy', 'default': True},
            {'name': 'include_attributes', 'type': bool, 'doc': 'Bool indicating whether we should include attributes in the hiararchy', 'default': True},
            {'name': 'include_relationships', 'type': bool, 'doc': 'Bool or list of strings indicating which types of relationships should be included', 'default': True})
    def __init__(self, **kwargs):
        self.data, self.include_groups, self.include_datasets, self.include_attributes, self.include_relationships = \
            getargs('data', 'include_groups', 'include_datasets', 'include_attributes', 'include_relationships', kwargs)
        self.graph = self.nxgraph_from_data(self.data,
                                            self.include_groups,
                                            self.include_datasets,
                                            self.include_attributes,
                                            self.include_relationships)
        self.pos = self.normalize_graph_layout(self.create_hierarchical_graph_layout(self.graph))

    def draw(self, **kwargs):
        """
        Draw the graph using the draw_graph method
        :param kwargs: Additional keyword arguments to be passed to the static draw_graph method
        :return:
        """
        return self.draw_graph(G=self.graph, pos=self.pos, object_stats=self.data, **kwargs)

    @staticmethod
    def nxgraph_from_data(data, include_groups=True, include_datasets=True, include_attributes=True, include_relationships=True):
        """
        Create a networkX representation of the objects in the HiearchyDescription stored in self.data

        :return:  NXGraph from self.data
        """
        import networkx as nx

        G = nx.Graph() # nx.MultiDiGraph()
        # Add all nodes
        if include_datasets:
            for d in data['datasets']:
                G.add_node(d['name'])
        if include_groups:
            for g in data['groups']:
                G.add_node(g['name'])
        if include_attributes:
            for g in data['attributes']:
                G.add_node(g['name'])

        # Create edges from relationships
        rel_list = include_relationships if isinstance(include_relationships, list) else data.RELATIONSHIP_TYPES if include_relationships is True else []
        all_nodes = G.nodes(data=False)
        if len(rel_list) > 0:
            for r in data['relationships']:
                # Add only those relationships we were asked to include
                if r['type'] in rel_list:
                     # Add only relationships for which we have both the source and target in the graph
                    if r['source'] in all_nodes and r['target'] in all_nodes:
                        G.add_edge(r['source'], r['target'])
        return G

    @staticmethod
    def create_hierarchical_graph_layout(graph):
        """
        Given a networkX graph of file hierarchy, comput the positions of all nodes of the
        graph (i.e., groups and datasets) in a hierarchical layout

        :param graph: Network X graph of file objects
        :param v_min_space: Minimum vertical space between notes in the hierarchy

        :return: Dictionary where the keys are the names of the nodes in the graph and the values are
                 tuples with the floating point x and y coordinates for that node.
        """

        import numpy as np

        pos_hierarchy = {}
        allnodes = graph.nodes(data=False)
        nodes_at_level = {} # {i:0 for i in range(7)}
        for v in allnodes:
            xpos = len(v.split('/')) if v != '/' else 1
            try:
                nodes_at_level[xpos] += 1
            except KeyError:
                nodes_at_level[xpos] = 1

        curr_nodes_at_level = {i:0 for i in nodes_at_level.keys()}
        for i, v in enumerate(np.sort(allnodes)):
            xpos = len(v.split('/')) if v != '/' else 1
            ypos = 1 - float(curr_nodes_at_level[xpos]) / nodes_at_level[xpos] * 1
            curr_nodes_at_level[xpos] += 1
            pos_hierarchy[v] = np.asarray([np.power(xpos,2),ypos])

        return pos_hierarchy

    @staticmethod
    def create_warped_hierarchial_graph_layout(graph):
        """
        Given a networkX graph of file hierarchy, compute the positions of all nodes of the
        graph (i.e., groups and datasets) in a hierarchical layout where the levels of the
        hierarchy are warped to follow a semi-circle shape.

        :param graph: Network X graph of file objects

        :return: Dictionary where the keys are the names of the nodes in the graph and the values are
                 tuples with the floating point x and y coordinates for that node.
        """
        import numpy as np

        pos_hierarchy = {}
        allnodes = graph.nodes(data=False)
        nodes_at_level = {} # {i:0 for i in range(7)}
        for v in allnodes:
            xpos = len(v.split('/')) if v != '/' else 1
            try:
                nodes_at_level[xpos] += 1
            except KeyError:
                nodes_at_level[xpos] = 1

        curr_nodes_at_level = {i:0 for i in range(7)}
        for i, v in enumerate(np.sort(allnodes)):
            xpos = len(v.split('/')) if v != '/' else 1
            ypos = float(curr_nodes_at_level[xpos]) / nodes_at_level[xpos]
            curr_nodes_at_level[xpos] += 1
            if xpos > 3:
                xpos += np.sin(ypos*np.pi)
            xpos = np.power(xpos,2)
            pos_hierarchy[v] = np.asarray([xpos,-ypos])

        return pos_hierarchy

    @staticmethod
    def normalize_graph_layout(graph_layout):
        """
        Normalize the positions in the given graph layout so that the x and y
        values have a range of [0,1]
        :param graph_layout: Dict where the keys are the names of the nodes in the graph
               and the values are tuples with the (x,y) locations for the nodes
        :return: New graph layout with normalized coordinates
        """
        import numpy as np
        # Compute positions stats
        xpos = np.asarray([i[0] for i in graph_layout.values()])
        ypos = np.asarray([i[1] for i in graph_layout.values()])
        xmin = xpos.min()
        xmax = xpos.max()
        xr = xmax - xmin
        ymin = ypos.min()
        ymax = ypos.max()
        yr = ymax - ymin

        # Create the output layout
        normlized_layout = {k: np.asarray([(n[0] - xmin)/ xr, (n[1] - xmin) / yr]) for k,n in graph_layout.items()}
        return normlized_layout

    @staticmethod
    def draw_graph(G,
               pos,
               object_stats,
               show_labels=True,
               node_size=800,
               relationship_types=None,
               figsize=None,
               label_offset=None,
               label_font_size=8,
               xlim=None,
               ylim=None,
               legend_location='lower left',
               axis_on=False,
               relationship_counts=None,
               show_plot=True):
        """
        Helper function used to render the file hierarchy and the inter-object relationships

        :param G: The networkx graph
        :param pos: Dict with the position for each node generated, e.g., via nx.shell_layout(G)
        :param show_lables: Boolean indicating whether we should show the names of the nodes
        :param node_size: Size of the nodes
        :param relationship_type: List of edge types that should be rendered. If None, then all edges will be rendered.
        :param figsize: The size of the matplotlib figure
        :param lable_offset: Offsets for the node lables. This may be either: i) None (default),
                   ii) Tuple with constant (x,y) offset for the text labels, or
                   iii) Dict of tuples where the keys are the names of the nodes for which labels should be moved
                        and the values are the (x,y) offsets for the given nodes.
        :param label_font_size: Font size for the lables
        :param xlim: The x limits to be used for the plot
        :param ylim: The y limits to be used for the plot
        :param legend_locations: The legend location (e.g., 'upper left' , 'lower right')
        :param axis_on: Boolean indicating whether the axes should be turned on or not.
        :param relationship_counts: Boolean indicating if edge/relationship counts should be shown.
        :param show_plot: If true call show to display the figure. If False return the matplotlib figure
                          without showing it.

        :return: Matplotlib figure of the data

        """
        from matplotlib import pyplot as plt
        import networkx as nx
        import os
        from copy import deepcopy
        from matplotlib.ticker import NullLocator


        figsize = figsize if figsize is not None else (12,12)
        fig = plt.figure(figsize=figsize)
        # List of object names
        untyped_group_names = [i['name'] for i in object_stats['groups'] if i['neurodata_type'] is None]
        typed_group_names   = [i['name'] for i in object_stats['groups'] if i['neurodata_type'] is not None]
        dataset_names       = [i['name'] for i in object_stats['datasets']]

        # Draw the nodes of the network
        nx.draw_networkx_nodes(G,pos,
                               nodelist=dataset_names,
                               node_color='gray',
                               node_shape='o',
                               node_size=node_size,
                               alpha=0.7,
                               font_family='STIXGeneral',
                               label='Dataset (%i)' % len(dataset_names) )
        # All groups in the rat data are managed so we don't need to handle unmanged groups sparately
        nx.draw_networkx_nodes(G,pos,
                               nodelist=typed_group_names,
                               node_color='r',
                               node_shape='o',
                               node_size=node_size,
                               font_family='STIXGeneral',
                               alpha=1.0,
                               label='Typed Group (%i)' % len(typed_group_names))
        # Overplot the dataset nodes that are in fact managed datasets
        # managed_datasets = set(object_stats['datasets']) & set(object_stats['managed'])
        nx.draw_networkx_nodes(G,pos,
                               nodelist= untyped_group_names,
                               node_color='cyan',
                               node_shape='o',
                               node_size=node_size,
                               font_family='STIXGeneral',
                               alpha=1.0,
                               label='Group (%i)' % len(untyped_group_names))

        # Draw the network edges
        rel_colors = {'shared_encoding': 'steelblue',
                      'indexes_values': 'cyan',
                      'equivalent': 'gray',
                      'indexes': 'orange',
                      'user': 'green',
                      'shared_ascending_encoding': 'blue',
                      'order': 'red',
                      'managed_by': 'black',
                      'attribute_of': 'magenta'}
        # nx.draw_networkx_edges(G, pos)

        # Resort edges by type
        edge_by_type = {}
        for r in object_stats['relationships']:
            if r['type'] in edge_by_type:
                edge_by_type[r['type']].append((r['source'], r['target']))
            else:
                edge_by_type[r['type']] = [(r['source'], r['target'])]

        if relationship_counts:
            relationship_counts = {rt: len(rl) for rt, rl in edge_by_type.items()}
        else:
            relationship_counts= None

        for rt, rl in edge_by_type.items():
            if relationship_types is None or rt in relationship_types:
                nx.draw_networkx_edges(G,
                                       pos,
                                       edgelist=rl,
                                       width=1.0,
                                       alpha=0.9 if rt != 'managed_by' else 0.3,
                                       edge_color=rel_colors[rt],
                                       label=rt if relationship_counts is None else (rt+' (%i)' % relationship_counts[rt])
                                       )

        if show_labels:
            # Create node lables
            labels={i:os.path.basename(i) if len(os.path.basename(i)) > 0 else i for i in G.nodes(data=False)}
            # Determine lable positions
            if label_offset is not None:
                # Move individual lables by the user-defined offsets
                if isinstance(label_offset, dict):
                    label_pos = deepcopy(pos)
                    for k, v in label_offset.items():
                        label_pos[k] += v
                # Move all labels by a single, user-defined offset
                else:
                    label_pos = {k: (v+label_offset) for k, v in pos.items()}
            else:
                # Use the node positions as label positions
                label_pos = pos
            # Draw the labels
            nx.draw_networkx_labels(G,label_pos,labels,font_size=label_font_size)

        if axis_on:
            plt.axis('on')
        else:
            plt.axis('off')
            # Get rid of large whitespace around the figure
            plt.gca().xaxis.set_major_locator(NullLocator())
            plt.gca().yaxis.set_major_locator(NullLocator())
        plt.legend(prop={'size': label_font_size}, loc=legend_location)
        plt.autoscale(True)
        plt.tight_layout()
        if xlim:
            plt.xlim(xlim)
        if ylim:
            plt.ylim(ylim)
        if show_plot:
            plt.show()
        return fig


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


