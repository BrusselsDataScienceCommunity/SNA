
# Contents

### Meetup Analysis
file | notes
----|-------
`extract.py` | script that combines the various `.json` files obtained from the meetup crawlers and outputs to 4 `.json` files in `/output`. **Warning**: json does not support integers as dictonnary keys, so there are type inconsistencies (see [here](http://stackoverflow.com/questions/1450957/pythons-json-module-converts-int-dictionary-keys-to-strings))
`extract_pickle.py` | same as `extract.py` except the outputs are pickle files, bypassing the json problem.
`find_new_members.py`| script computing 3 metrics and outputting lists for new members in `/output`
`graph_walk.py` | script producing the metrics from `find_new_members` + 4 other ones. Outputs to `output/metrics.csv`. Uses the `Sliced_graph` class in `sliced_graph.py` and requires previous use of `extract_pickle.py`


### Visualisation

see also the content of the `html/` subfolder

file | content | produced by 
---- | ------- | -----------
`common_topic_graph.json` | groups linked by common topics | `topics.py`
`force.json` | *idem* | `meetup_graphs.py`
`common_member_graph.json` | groups linked by common members | `topics.py`
`member_force.json` | *idem* | `meetup_graphs.py`
`group.json`| nodes = BruDataSci + members + similar groups (common members), edges +-= membership | `meetup_graphs.py`
`topics_and_groups_graph.json` | nodes = topics + groups, edge = 'topic of' | `topics.py`
`topics_graph.json` | topics linked by common groups | `topics.py`

`foo_tech.json` = same as `foo.json` restricted to tech meetup groups, produced by `topics_tech.py`

N.B.: "A linked by common B" means that an edge between nodes A1 and A2 is drawn whenever the overlap between A1 and A2 is *substantial* (substantial can have different meanings / thresholds for different graphs)

Technical N.B.: in `foo.json` (non-tech) there is only a `name`attribute which is displayed on mouseover only.
in `foo_tech.json`, the `name` attribute of a node is a shortened version of the `fullname` and is displayed on top of every node in `index_tech.html`.