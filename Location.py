import psycopg2, pickle, numpy as np
import sys, os, cv2
from pyproj import Proj, transform

try:
    import mapnik2 as mapnik
except:
    import mapnik

class Location():
    
    def __init__(self, X, Y, epsg):
        # Data is a list containing infor asociated with each point 
        # [lat, lon, name, highway, juntion, sidewalk, lit, lanes, noexit]
        def create_cursor():
            db = "dbname='gis' user='postgres' host='{}'"
            db = db.format(self.host)
            conn = psycopg2.connect(db)
            cur = conn.cursor()
            return cur
        
        def transform_proj(X, Y):
            inProj = Proj(init='epsg:3857')
            outProj = Proj(init='epsg:4326')
            lat, lon = transform(inProj,outProj,X,Y)
            return lat, lon

        def transform_to_3857(X, Y):
            inProj = Proj(init='epsg:4326')
            outProj = Proj(init='epsg:3857')
            lat, lon = transform(inProj,outProj,X,Y)
            return lon, lat
        
        if epsg == 3857:
            self.X = X
            self.Y = Y
            self.lon, self.lat = transform_proj(self.X,self.Y)
        else:
            self.lat = X
            self.lon = Y
            self.X, self.Y = transform_to_3857(self.lat,self.lon)

        
        self.host = "localhost"
        self.size = 0.0005
        self.cursor = create_cursor()
    
    def __str__(self):
        message = """
        Point: {},{} 
        """
        message = message.format(self.lat, self.lon)
        return message

    def render(self):
        # spherical mercator (most common target map projection of osm data imported with osm2pgsql)
        merc = mapnik.Projection('+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs +over')
        longlat = mapnik.Projection('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
        mapfile = "map_data/styles/bs_complete.xml"
        bounds = (self.lon-self.size, self.lat-self.size, self.lon+self.size,self.lat+self.size)
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
        cv2.waitKey(0)
        #image_uri = 'image.png'
        #im.save(image_uri,'png')
        #sys.stdout.write('output image to %s!\n' % image_uri)

    def near_roads(self):
        query = """ SELECT DISTINCT name
        FROM planet_osm_line
        WHERE planet_osm_line.way &&
        ST_Transform(
        ST_MakeEnvelope({}, {}, {}, {}, 
        4326),3857
        ) and name <> 'Park Row' and highway <> '';
        """
        query = query.format(self.lon-self.size,self.lat-self.size,self.lon+self.size,self.lat+self.size)
        cur = self.cursor
        cur.execute(query)
        near_streets = cur.fetchall()
        streets = []
        for street in near_streets:
            streets.append(street[0]) # Just to remove the empty element at the end of the list            
        return streets

    # def intersections(self, near_roads, point_or_box):
    #     cur = self.cursor
    #     if point_or_box == "box":
    #         intersections = []
    #         for street in near_roads:
    #             qmark = street.find("'") 
    #             if qmark != -1:
    #                 street = street[:qmark] + "'" + street[qmark:]          
    #             query = """
    #             select ST_Y(ST_Transform(the_intersection, 4326)), ST_X(ST_Transform(the_intersection, 4326))
    #             from
    #             (select distinct(ST_Intersection(b.way, a.way)) as the_intersection
    #             from
    #             (select way from planet_osm_line where name = '{}' ) as a,
    #             (select way from planet_osm_line where name = '{}') as b
    #             where a.way && b.way and ST_Intersects(b.way, a.way)
    #             ) as Foo;
    #             """
    #             query = query.format(self.name, street)
    #             cur.execute(query)
    #             intersection = cur.fetchall()
    #             if intersection != None:
    #                 intersections.append(intersection)
    #         return intersections
    #     elif point_or_box == "point":
    #         for street in near_roads:
    #             qmark = street.find("'") 
    #             if qmark != -1:
    #                 street = street[:qmark] + "'" + street[qmark:]
    #             query = """
    #             SELECT ST_Y(foo.the_intersection), ST_X(foo.the_intersection) 
    #             FROM
    #             (SELECT ST_Intersection(ST_SetSRID(ST_MakePoint({},{}), 3857), way) as the_intersection
    #             FROM planet_osm_line
    #             WHERE name = '{}' and way &&ST_Intersection(ST_SetSRID(ST_MakePoint({},{}), 3857), way)
    #             ) As Foo;
    #             """
    #             query = query.format(self.X,self.Y, street,self.X,self.Y, street)
    #             cur.execute(query)
    #             intersection = cur.fetchall()
    #             if intersection != []:
    #                 intersection = 1
    #             else:
    #                 intersection = 0
    #             return intersection
        
    def landuse(self):
        query = """ SELECT DISTINCT landuse, water, tourism
        FROM planet_osm_polygon
        WHERE planet_osm_polygon.way &&
        ST_MakeEnvelope({}, {}, {}, {}, 
        3857)
        """
        query = query.format(self.X-self.size,self.Y-self.size,self.X+self.size,self.Y+self.size)
        query = query.format(self.X-self.size,self.Y-self.size,self.X+self.size,self.Y+self.size)
        cur = self.cursor
        cur.execute(query)
        landuse = cur.fetchall()
        landuse_list = []
        for use in landuse:
            if use != [None]:
                landuse_list.append(use[0]) # Just to remove the empty element at the end of the list            
        return landuse
