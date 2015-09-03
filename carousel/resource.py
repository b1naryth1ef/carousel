import os, json

import kazoo

class ResourceException(Exception):
    pass

class Resource(object):
    def __init__(self, pool, name):
        self.pool = pool
        self.name = name
        self.zk = pool.zk

        self.path = os.path.join(pool.path, 'resources', name)

        self.meta = None
        self.meta_stat = None

    @property
    def leader_path(self):
        return os.path.join(self.pool.path, 'leaders', self.name)

    def load(self):
        # Check whether the resource exists
        if not self.zk.exists(self.path):
            raise ResourceException("Resource with name {} does not exist!".format(self.name))

        # Now load the resource metadata
        self.meta, self.meta_stat = self.zk.get(self.path)
        self.meta = json.loads(self.meta.decode())

    def create(self, meta={}):
        self.zk.create(self.path, str.encode(json.dumps(meta)))

    def try_elect_leader(self, node):
        self.zk.create(self.leader_path, str.encode(node.id), ephemeral=True)

        if self.zk.exists(os.path.join(self.path, 'leader')):
            self.zk.delete(os.path.join(self.path, 'leader'))

        self.zk.create(os.path.join(self.path, 'leader'), str.encode(node.id), ephemeral=True)

        node.start_lead(self)

        return True

    def elect_leader(self, node):
        print("Electing {} as the leader for {}".format(node.id, self.name))
        
        # If we already have a leader, make sure we actually change it
        if self.zk.exists(self.leader_path):
            _, stat = self.zk.get(self.leader_path)
            
            # Now, in a single transaction, take over. This prevents other nodes from attempting to take leadership.
            t = self.zk.transaction()
            t.delete(self.leader_path, stat.version)
            t.create(self.leader_path, str.encode(node.id), ephemeral=True)
            t.commit()
        else:
            self.zk.create(self.leader_path, str.encode(node.id), ephemeral=True)
        
        # First, delete the local leader znode. This will not cause a reeleciton
        if self.zk.exists(os.path.join(self.path, 'leader')):
            self.zk.delete(os.path.join(self.path, 'leader'))

        # Now update the local leader znode
        self.zk.create(os.path.join(self.path, 'leader'), str.encode(node.id), ephemeral=True)

        node.start_lead(self)

    def get_leader(self):
        from .node import Node
        try:
            leader, _ = self.zk.get(self.leader_path)
        except kazoo.exceptions.NoNodeError:
            return None

        return Node.from_id(self.pool, leader.decode())

    def call_vote(self):
        self.zk.delete(self.leader_path)

