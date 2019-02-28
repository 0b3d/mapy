import psycopg2, pickle, numpy as np, random
import overpy
import sys, os, cv2
try:
    import mapnik2 as mapnik
except:
    import mapnik



class Map():

    def __init__(self, container_id):
        
        def create_cursor():
            db = "dbname='gis' user='postgres' host='{}'"
            db = db.format(self.container_id)
            conn = psycopg2.connect(db)
            cur = conn.cursor()
            return cur

        self.container_id = container_id
        self.database = "gis"
        self.cursor = create_cursor()
        self.size = 0.0005
    
    def add_qmark(self, name):
        qmark = name.find("'") 
        if qmark != -1:
            name = name[:qmark] + "'" + name[qmark:]    
        return name      

    def roads(self, highway):
        if highway == "all":
            query = """ SELECT DISTINCT name from planet_osm_line where name <> '' and highway <> ''
            """
        else:
            query = """ SELECT DISTINCT name from planet_osm_line where name <> '' and highway = '{}' """
            query = query.format(highway)

        cur = self.cursor
        cur.execute(query)
        roads = cur.fetchall()
        roads_list = []
        for road in roads:
            roads_list.append(road[0])
        return roads_list

    def roads_point_list(self):
        # Query the main information
        cur = self.cursor
        query = """
        SELECT ST_Y((dp).geom), ST_X((dp).geom), ST_Y((dp2).geom), ST_X((dp2).geom), name, highway, junction, sidewalk, lit, lanes, noexit
        FROM(
            SELECT ST_DumpPoints(ST_Transform(way,4326)) AS dp, ST_DumpPoints(way) AS dp2, name, highway, junction, tags->'sidewalk' as sidewalk, tags->'lit' as lit, tags->'lanes' as lanes, tags->'noexit' as noexit
            FROM planet_osm_line 
            WHERE name <> '' and highway <> ''
            ORDER BY name
        ) As foo;
        """
        query = query.format()
        cur.execute(query)
        points = cur.fetchall()
        return points
    
    def limits(self, epsg):
        if epsg == 900913:
            query_limits = """
            select min(st_xmin(way)), min(st_ymin(way)), max(st_xmax(way)), max(st_ymax(way)) from planet_osm_line where name<>'' and highway<>'';
            """
        elif epsg == 4326:
            query_limits = """
            select  min(st_ymin(st_transform(way,4326))), min(st_xmin(st_transform(way,4326))), max(st_ymax(st_transform(way,4326))), max(st_xmax(st_transform(way,4326))) from planet_osm_line where name<>'' and highway<>'';
            """
        self.cursor.execute(query_limits)
        limits = self.cursor.fetchall()
        return limits

    def execute_query(self, query):
        self.cursor.execute(query)
        res = self.cursor.fetchall()
        return res

    def show_locations(self, locations, mapfile):
        # spherical mercator (most common target map projection of osm data imported with osm2pgsql)
        merc = mapnik.Projection('+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs +over')
        longlat = mapnik.Projection('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
        mapfile = "map_data/styles/bs_" + mapfile + ".xml"
        for location in locations:
            lat, lon = location[0], location[1]
            bounds = (lon- self.size, lat- self.size, lon+ self.size, lat+ self.size)
            z = 1
            imgx = 500 * z
            imgy = 500 * z
            m = mapnik.Map(imgx,imgy)
            mapnik.load_map(m,mapfile)
            m.srs = merc.params()
            if hasattr(mapnik,'Box2d'):
                bbox = mapnik.Box2d(*bounds)
            else:
                bbox = mapnik.Envelope(*bounds)
            transform = mapnik.ProjTransform(longlat,merc)
            merc_bbox = transform.forward(bbox)
            m.zoom_to_box(merc_bbox)
            #render the map to an image
            im = mapnik.Image(imgx,imgy)
            mapnik.render(m, im)
            img = im.tostring('png256')
            img = cv2.imdecode(np.fromstring(img, dtype=np.uint8), 1)
            img =np.asarray(img)
            window_name = "Location"
            cv2.imshow(window_name, img)
            cv2.waitKey(1)

    def roundabout(self, highway_type):
        cur = self.cursor
        query = """
        SELECT ST_Y((dp).geom), ST_X((dp).geom), ST_Y((dp2).geom), ST_X((dp2).geom), name, highway, junction, sidewalk, lit, lanes, noexit
        FROM(
            SELECT ST_DumpPoints(ST_Transform(way,4326)) AS dp, ST_DumpPoints(way) AS dp2, name, highway, junction, tags->'sidewalk' as sidewalk, tags->'lit' as lit, tags->'lanes' as lanes, tags->'noexit' as noexit
            FROM planet_osm_line 
            WHERE name <> '' and highway = '{}' and junction='roundabout'
            ORDER BY name
        ) As foo;
        """
        query = query.format(highway_type)
        cur.execute(query)
        points = cur.fetchall()
        return points



