import json, os

from kazoo.client import KazooClient
from kazoo.recipe.watchers import DataWatch, ChildrenWatch

from .node import Node
from .resource import Resource

class PoolException(Exception):
    pass

class Pool(object):
    def __init__(self, name):
        self.name = name
        self.zk = None
        self.path = '/carousel/{}'.format(name)

        # Pool meta-data
        self.meta = None
        self.meta_stat = None

        self.resources = set()

    def on_resources_change(self, res):
        self.resources = set(res)

    def create(self, metadata={}):
        # Create the base pool path with metadata
        self.zk.create(self.path, str.encode(json.dumps(metadata)), makepath=True)

        for path in ['resources', 'nodes', 'leaders']:
            self.zk.create(os.path.join(self.path, path))

        self.load()

    def connect(self, *hosts, timeout=4):
        self.zk = KazooClient(','.join(hosts), timeout=timeout)
        self.zk.start()

    def load(self):
        # Check whether the pool exists
        if not self.zk.exists(self.path):
            raise PoolException("Pool with name {} does not exist!".format(self.name))

        # Next load the pool meta-data
        self.meta, self.meta_stat = self.zk.get(self.path)
        self.meta = json.loads(self.meta.decode())

        # Finally, we need to keep track of all resources in this pool
        ChildrenWatch(self.zk, os.path.join(self.path, 'resources'), self.on_resources_change)

    def disconnect(self):
        self.zk.stop()

    def get_node(self):
        return Node(self)

    def get_resource(self, name):
        return Resource(self, name)

    def __eq__(self, other):
        return other.name == self.name

    def test(self, wat):
        print(wat)

