from carousel.pool import Pool, PoolException
from carousel.resource import ResourceException

pool = Pool("test")
pool.connect("127.0.0.1:2181")

# Load or create the pool
try:
    pool.load()
except PoolException:
    pool.create()

# Get a node and join the pool
node = pool.get_node()
node.join()

# Grab some resources
a = pool.get_resource("a")
b = pool.get_resource("b")
c = pool.get_resource("c")

# Load the resources
for res in [a, b, c]:
    try:
        res.load()
    except ResourceException:
        res.create()

# Force a node to be the leader of this resource
# a.elect_leader(node)
# assert(a.get_leader() == node)

# Call a vote to determine a new leader
# b.call_vote()

import time
while True:
    time.sleep(1)

