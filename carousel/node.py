import os

from kazoo.recipe.watchers import DataWatch, ChildrenWatch

from .resource import Resource
from .util import wrapped

class Node(object):
    def __init__(self, pool, max_resources=1):
        self.pool = pool
        self.zk = pool.zk

        self.id = None
        self.path = None

        # Set of resources we own
        self.resources = set()
        self.max_resources = max_resources

    def start_lead(self, resource):
        print("Starting lead of {}...".format(resource.name))
        self.resources.add(resource.name)
        DataWatch(self.zk, os.path.join(resource.path, 'leader'), self.on_resource_master_change)

    def stop_lead(self, resource):
        self.resources.remove(resource.name)

    def on_resource_master_change(self, data, stat, event):
        if not event:
            return

        resource = Resource(self.pool, event.path.split('/')[-2])

        # If we don't track this resource, get it the hell out of here
        if resource.name not in self.resources:
            # TODO: check whether we should track this
            return False

        if event.type == 'DELETED' or resource.get_leader() != self:
            print("Lost leadership over resource {}".format(resource.name))
            self.stop_lead(resource)
            return False
        
    def attempt_election(self, resources):
        for res in resources:
            if len(self.resources) < self.max_resources:
                res = Resource(self.pool, res)
                res.try_elect_leader(self)

    def on_leader_change(self, children, event):
        children = set(children)
        lost = self.pool.resources - children
        self.attempt_election(lost)

    def join(self):
        path = self.zk.create(os.path.join(self.pool.path, 'nodes', ''), ephemeral=True, sequence=True)
        self.path = path
        self.id = path.rsplit('/', 1)[-1]
        
        # Watch for leadership changes so we can possibly take over
        ChildrenWatch(self.zk, os.path.join(self.pool.path, 'leaders'), self.on_leader_change, send_event=True)

    @classmethod
    def from_id(cls, pool, id):
        node = cls(pool)
        node.id = id
        node.path = os.path.join(pool.path, 'nodes', node.id)
        return node

    def __eq__(self, other):
        if isinstance(other, Node):
            return (self.pool == other.pool) and (self.id == other.id)
        return False
