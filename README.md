# carousel
Carousel is a lightweight library for distributed resource management in Python. It utilizes zookeeper to safely manage master/slave ownership for many resources at once.

## Why
Carousel was built to help handle distributed resource management, when a single master per-resource is required, but internal routing and quick failover is desired. Take the following use case:

- We have N many shops, and Z many shop owners
- Any shop owner may own 0, 1, or more shops at any time
- There may only by a single owner per shop at any one time
- At any time, any shop should be able to transfer items to another shop through its owner easily
- At any time, if a shop owner is shot and killed, another shot owner must take over immediatly

## Terminology
Pools: Pools contain a set of nodes and resources. They are a form of segmentation for subentities, allowing resources to be catgorized better.
Nodes: Nodes are members of the network that can have one of three roles:

## Paths
```
/carousel/<pool> (meta data)
/carousel/<pool>/nodes/<node> (node metadata)
/carousel/<pool>/resources/<resource> (resource metadata)
/carousel/<pool>/leaders/<resource> (leader for a resource)

```

