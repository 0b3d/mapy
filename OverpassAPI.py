import overpy
import pickle

class Overpass():
  def __init__(self, south, west, north, east):
    self.overpass_url = "http://overpass-api.de/api/interpreter"
    self.api = overpy.Overpass()
    self.north = north
    self.south = south
    self.east = east
    self.west = west
    self.bbox = '('+ str(self.south) + ',' +str(self.west) + ',' +str(self.north) + ',' +str(self.east) + ')'

  def intersections(self, type1, type2):
    print("Extracting "+type1+'-'+type2 +" intersections")
    query = """
    [timeout:3600];
    way
        ["highway" = "%s"]
        ["junction"!="roundabout"]
        %s
        -> .relevant_ways;
    
    foreach.relevant_ways -> .this_way{
    .this_way;
    convert elem
    ::id=id(),
    name = t["name"];
    //out body; 
    
    node(w.this_way)->.this_way_nodes;
    way(bn.this_way_nodes)->.linked_ways;
    way.linked_ways
        ["highway"]
        ["highway"="%s"]
        ["junction"!="roundabout"]
        ->.linked_ways;
    //.linked_ways;
    //out body;
    
    complete.this_way{way["highway"="%s"][name]            
    (around:0)(if: t["name"]==u(t["name"])) -> .same_way;
    };
    //.same_way;
    //out body;
    
    (.linked_ways; - .same_way;) -> .linked_ways_only;
    
    node(w.same_way)-> .same_way_nodes;
    node(w.linked_ways_only)->.linked_ways_only_nodes;
    node.linked_ways_only_nodes.same_way_nodes;
    out;
    }
    """ % (type1, self.bbox, type2, type2)

    result = self.api.query(query)

    coords = []
    coords += [(float(node.lat), float(node.lon)) 
              for node in result.nodes]
    coords += [(float(way.center_lat), float(way.center_lon)) 
              for way in result.ways]
    coords += [(float(rel.center_lat), float(rel.center_lon)) 
              for rel in result.relations]
    file_name = type1 + '-' + type2 + '.pkl'
    with open(file_name, 'wb') as f:
      pickle.dump(coords, f)
    print("Intersections saved in " + file_name)

