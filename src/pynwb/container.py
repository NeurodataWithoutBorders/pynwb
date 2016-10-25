


class Container(object):
    
    def __init__(self, parent=None, container_source=None):
        self.__fields = list()
        self.__subcontainers = list()
        self.__parent = parent
        self.__container_source = container_source

    @property
    def container_source(self):
        return self.__container_source
    
    @property
    def fields(self):
        return self.__fields
    
    @property
    def subcontainers(self):
        return self.__subcontainers

    @property
    def parent(self):
        return self.__parent
    
    @parent.setter
    def set_parent(self, parent_container):
        self.__parent = parent_container
    
    def add_subcontainer(self, container):
        self.__subcontainers.append(container)
