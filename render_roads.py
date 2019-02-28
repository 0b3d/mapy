import psycopg2, pickle, random
from Map import Map
from Location import Location
from OverpassAPI import Overpass


overpass = Overpass(51.3400128720829, -2.92999633465543, 51.5899987860136, -2.27000409541281)
#overpass = Overpass(51.34, -2.62, 51.47, -2.57)
overpass.intersections("tertiary", "tertiary")
overpass.intersections("residential", "residential")
overpass.intersections("motorway", "motorway")
overpass.intersections("primary", "secondary")
overpass.intersections("primary", "tertiary")
overpass.intersections("primary", "residential")
overpass.intersections("primary", "motorway")
overpass.intersections("secondary", "tertiary")
overpass.intersections("secondary", "residential")
overpass.intersections("secondary", "motorway")
overpass.intersections("tertiary", "residential")
overpass.intersections("tertiary", "motorway")
overpass.intersections("residential", "motorway")

#bristol = Map("localhost")
# roundabouts = bristol.roundabout("secundary|primary")
#bristol.show_locations(roundabouts, "complete")
# with open('primary-primary.pkl', 'rb') as f:
#     intersections = pickle.load(f)
# random.shuffle(intersections)
# bristol.show_locations(intersections, "complete")


