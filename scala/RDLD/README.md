# Really Distributed Linked Data

This project is based on the thought experiment in
[Dbd](https://github.com/petervandenabeele/dbd), but using different implementation aspects:

* Drop the Context as an intrinsic storage item of a Fact
  (context can still be added, using regular facts)
* emphasize the streaming/"Event Sourcing" aspect of the
  fact stream (particularly for the windowed caching option);
  this also refers to the ideas published on
  [distributed joins for linked data](https://data.vandenabeele.com/docs/distributed-joins)
* Use Scala/Spark/GraphX as a core technology
  (this is required as the windowed caching/Event Sourcing will
  trigger a massive amount of data, so a horizontally scalable
  graph solution is required)

