from shapely.geometry import Polygon,MultiPolygon,Point,LineString,MultiLineString
import numpy as np
import json
from shapely.ops import unary_union
import tensorflow as tf
import tensorflow
from shapely.validation import make_valid,explain_validity
from shapely import affinity

Z_scale_factor = (2/3)**0.5



def parse_contest(index_list,geo_data):

    layout_all = []
    for i in index_list:
        room = geo_data[i][10:-2].split(",")
        room_corners = []
        for j in room:
            xy = j.strip().split(" ")
            if xy[1][-1] == ')':
                xy[1] = xy[1][:-1]
            if xy[0][0] == '(':
                xy[0] = xy[0][1:]
            room_corners.append((float(xy[0]),float(xy[1])))
        rooms_poly = Polygon(room_corners)
        layout_all.append(rooms_poly)
    floorplan_all_polygon = MultiPolygon(layout_all)
    boundary = unary_union(floorplan_all_polygon.buffer(0.01,join_style=2))
    while boundary.geom_type == 'MultiPolygon':
        boundary = boundary.buffer(0.01,join_style=2)
    return boundary

def parse_rooms(index_list,geo_data,subtype,room_types,types_index):

    rooms = []
    front_door = None
    types = []
    for i in index_list:
        room_type = subtype[i]
        room = geo_data[i][10:-2].split(",")
        room_corners = []
        for j in room:
            xy = j.strip().split(" ")
            if xy[1][-1] == ')':
                xy[1] = xy[1][:-1]
            if xy[0][0] == '(':
                xy[0] = xy[0][1:]
            room_corners.append((float(xy[0]),float(xy[1])))
        rooms_poly = Polygon(room_corners)
        if room_type in room_types and room_type not in ['TERRACE','BALCONY','LOGGIA']:
            rooms.append(rooms_poly)
            types.append(types_index[room_types.index(room_type)])
        elif room_type == 'ENTRANCE_DOOR':
            front_door=rooms_poly

    rooms_poly_segement = MultiPolygon(rooms)
    rooms_polygon = unary_union(rooms_poly_segement.buffer(0.5,join_style=2))
    if rooms_polygon.geom_type == 'MultiPolygon': rooms_polygon = union_multipoly(rooms_polygon,0.01)

    if rooms_polygon.geom_type != 'GeometryCollection' and list(rooms_polygon.interiors) != []: rooms_polygon = fillgap_poly(rooms_polygon,0.1)

    if front_door: front_door = front_door.centroid.buffer(0.3)

    return rooms_polygon, rooms_poly_segement, types, front_door

def parse_floor(index_list,geo_data,subtype,floor_types,elevation,height):

    layout_all = []
    layout_apart = []
    public = []
    front_door = []
    stairs = []
    windows = []
    balcony = []
    railings = []
    room_eleva = 100
    window_eleva = 100
    rail_eleva = 100
    room_height = 100
    window_height = 100
    rail_height = 100

    for i in index_list:
        room_type = subtype[i]
        room = geo_data[i][10:-2].split(",")
        room_corners = []
        for j in room:
            xy = j.strip().split(" ")
            if xy[1][-1] == ')':
                xy[1] = xy[1][:-1]
            if xy[0][0] == '(':
                xy[0] = xy[0][1:]
            room_corners.append((float(xy[0]),float(xy[1])))
        rooms_poly = Polygon(room_corners)
        layout_all.append(rooms_poly)
        if room_type not in ['TERRACE','BALCONY','LOGGIA']: 
            layout_apart.append(rooms_poly)
            if room_eleva == 100:
                room_eleva = elevation[i]
                room_height = height[i]
        # if room_type in room_types or room_type == 'VOID':
        #     type_list.append(room_type)
        #     loc_list.append([rooms_poly.centroid.x,rooms_poly.centroid.y])
        if room_type in floor_types: 
            public.append(rooms_poly)
        elif room_type == 'ENTRANCE_DOOR': front_door.append(rooms_poly)
        elif room_type == 'STAIRCASE': stairs.append(rooms_poly)
        elif room_type == 'WINDOW': 
            windows.append(rooms_poly)
            if window_eleva == 100:
                window_eleva = elevation[i]
                window_height = height[i]
        elif room_type in ['TERRACE','BALCONY','LOGGIA']: 
            balcony.append(rooms_poly)
        elif room_type == 'RAILING': 
            railings.append(rooms_poly)
            if rail_eleva == 100:            
                rail_eleva = elevation[i]
                rail_height = height[i]

    floorplan_all_polygon = MultiPolygon(layout_apart)
    all_polygon = MultiPolygon(layout_all) 
    public_polygon = MultiPolygon(public)
    stair_polygon = MultiPolygon(stairs)
    window_polygon = MultiPolygon(windows)
    rail_polygon = MultiPolygon(railings)

    floorplan_all_polygon = union_multipoly(floorplan_all_polygon,0.01)
    all_polygon = union_multipoly(all_polygon,0.01)
    boundary_domainxy = floorplan_all_polygon.bounds # (minx, miny, maxx, maxy)
    x = boundary_domainxy[2] - boundary_domainxy[0]
    y = boundary_domainxy[3] - boundary_domainxy[1]
    public_polygon = unary_union(public_polygon.buffer(0.3,join_style=2))
    # private_polygon = unary_union(private_polygon.buffer(0.3,join_style=2))

    if list(floorplan_all_polygon.interiors) != []: floorplan_all_polygon = fillgap_poly(floorplan_all_polygon,0.1)
    if public_polygon.geom_type == 'MultiPolygon':
        modified = []
        for m,n in enumerate(public_polygon.geoms):
            if list(n.interiors) != []: modified.append(fillgap_poly(n,0.1))
            else: modified.append(n)
        public_polygon = MultiPolygon(modified)
    elif public_polygon.geom_type == 'GeometryCollection':
        public_polygon = Point((0,0)).buffer(0.001)
    else:
        if list(public_polygon.interiors) != []: public_polygon = fillgap_poly(public_polygon,0.1)

    public_polygon = public_polygon.intersection(floorplan_all_polygon)

    if len(front_door) == 1: newfrondoor = front_door[0].centroid.buffer(0.75)
    else: newfrondoor = [i.centroid.buffer(0.75) for i in front_door]

    return all_polygon, floorplan_all_polygon, public_polygon, stair_polygon, window_polygon, rail_polygon, balcony, \
            newfrondoor, x, y, room_eleva, window_eleva, rail_eleva, room_height, window_height, rail_height

def parse_floor2D(index_list,geo_data,subtype,floor_types,elevation,height):

    layout_all = []
    layout_apart = []
    public = []
    front_door = []
    stairs = []
    windows = []
    balcony = []
    railings = []
    room_eleva = 100
    window_eleva = 100
    rail_eleva = 100
    room_height = 100
    window_height = 100
    rail_height = 100

    for i in index_list:
        room_type = subtype[i]
        room = geo_data[i][10:-2].split(",")
        room_corners = []
        for j in room:
            xy = j.strip().split(" ")
            if xy[1][-1] == ')':
                xy[1] = xy[1][:-1]
            if xy[0][0] == '(':
                xy[0] = xy[0][1:]
            room_corners.append((float(xy[0]),float(xy[1])))
        rooms_poly = Polygon(room_corners)
        # if room_type not in ['WALL','DOOR','WINDOW','RAILING']: 
        layout_all.append(rooms_poly)
        if room_type not in ['TERRACE','BALCONY','LOGGIA']: 
            layout_apart.append(rooms_poly)
            # if room_eleva == 100:
            #     room_eleva = elevation[i]
            #     room_height = height[i]
        # if room_type in room_types or room_type == 'VOID':
        #     type_list.append(room_type)
        #     loc_list.append([rooms_poly.centroid.x,rooms_poly.centroid.y])
        if room_type in floor_types: 
            public.append(rooms_poly)
        elif room_type == 'ENTRANCE_DOOR': front_door.append(rooms_poly)
        elif room_type == 'STAIRCASE': stairs.append(rooms_poly)
        elif room_type == 'WINDOW': 
            windows.append(rooms_poly)
            # if window_eleva == 100:
            #     window_eleva = elevation[i]
            #     window_height = height[i]
        elif room_type in ['TERRACE','BALCONY','LOGGIA']: 
            balcony.append(rooms_poly)
        elif room_type == 'RAILING': 
            railings.append(rooms_poly)
            # if rail_eleva == 100:            
            #     rail_eleva = elevation[i]
            #     rail_height = height[i]

    floorplan_all_polygon = MultiPolygon(layout_apart)
    all_polygon = MultiPolygon(layout_all) 
    public_polygon = MultiPolygon(public)
    stair_polygon = MultiPolygon(stairs)
    window_polygon = MultiPolygon(windows)
    rail_polygon = MultiPolygon(railings)

    floorplan_all_polygon = union_multipoly(floorplan_all_polygon,0.01)
    # all_polygon = union_multipoly(all_polygon,0.01)
    boundary_domainxy = floorplan_all_polygon.bounds # (minx, miny, maxx, maxy)
    x = boundary_domainxy[2] - boundary_domainxy[0]
    y = boundary_domainxy[3] - boundary_domainxy[1]
    public_polygon = unary_union(public_polygon.buffer(0.3,join_style=2))
    # private_polygon = unary_union(private_polygon.buffer(0.3,join_style=2))

    if list(floorplan_all_polygon.interiors) != []: floorplan_all_polygon = fillgap_poly(floorplan_all_polygon,0.1)
    if public_polygon.geom_type == 'MultiPolygon':
        modified = []
        for m,n in enumerate(public_polygon.geoms):
            if list(n.interiors) != []: modified.append(fillgap_poly(n,0.1))
            else: modified.append(n)
        public_polygon = MultiPolygon(modified)
    elif public_polygon.geom_type == 'GeometryCollection':
        public_polygon = Point((0,0)).buffer(0.001)
    else:
        if list(public_polygon.interiors) != []: public_polygon = fillgap_poly(public_polygon,0.1)

    public_polygon = public_polygon.intersection(floorplan_all_polygon)

    if len(front_door) == 1: newfrondoor = front_door[0].centroid.buffer(0.75)
    else: newfrondoor = [i.centroid.buffer(0.75) for i in front_door]

    return all_polygon, floorplan_all_polygon, public_polygon, stair_polygon, window_polygon, rail_polygon, balcony, \
            newfrondoor, x, y, room_eleva, window_eleva, rail_eleva, room_height, window_height, rail_height


def check_vertical_connect(floor_list):
    vertical_lines = []
    corner_list = []
    lens = len(floor_list)
    for i in range(lens): corner_list.append(floor_list[i].exterior.coords[:-1])
    for f in range(lens-1):
        for p1 in corner_list[f]:
            for p2 in corner_list[f+1]:
                if p1.distance(p2) < 0.1: vertical_lines.append([p1.xy,p2.xy])
    
    return vertical_lines
        
def union_multipoly(geo,step):
    geo = unary_union(geo.buffer(step,join_style=2))
    while geo.geom_type == 'MultiPolygon':
        geo = geo.buffer(step,join_style=2)
    
    return geo

def fillgap_poly(geo,gap):
    for inte in list(geo.interiors):
        geo = unary_union(MultiPolygon([geo,Polygon(inte).buffer(gap,join_style=2)]))
    
    return geo

def scale_to_img(ratio,Mx,My,geo):

    return np.array([[[x*ratio + Mx, y*ratio + My] for x, y in zip(*geo.exterior.coords.xy)]])

def scale_to_img_list(ratio,Mx,My,geo):
    geo_list = []
    for i in geo:
        if i.geom_type != 'GeometryCollection':
            geo_list.append(np.array([[[x*ratio + Mx, y*ratio + My] for x, y in zip(*i.exterior.coords.xy)]]))
    
    return geo_list

def find_maxgeo(geo):
    area = []
    for i in geo.geoms:
        area.append(i.area)
    
    return geo.geoms[area.index(max(area))]

def find_longest_crv(geo):
    pts = geo.exterior.coords
    count = len(pts)
    length = []
    for i in range(count-1):
        length.append((pts[i+1,0]-pts[i,0])**2+(pts[i+1,1]-pts[i,1])**2)
    maxid = length.index(max(length))
    return LineString([pts[maxid],pts[maxid+1]])

def deform_iso(geo,pt,noise):
    geo = affinity.rotate(geo, noise, pt)
    geo = affinity.scale(geo, xfact=Z_scale_factor, origin=pt)

    return geo

def deform_multipoly_iso(geo,pt,noise):
    deformed = []
    for i in geo.geoms:
        deform = affinity.rotate(i, noise, pt)
        deformed.append(affinity.scale(deform, xfact=Z_scale_factor, origin=pt))
    
    return MultiPolygon(deformed)

def deform_multicrv_iso(geo,pt,noise):
    deformed = []
    for i in geo:
        deform = affinity.rotate(i, noise, pt)
        deformed.append(affinity.scale(deform, xfact=Z_scale_factor, origin=pt))
    
    return MultiLineString(deformed)

def prepare_MaskPLAN_data_Twice(T, L, A, S, R, num_layout, sqe_length, ada_length):

    T_mask1,L_mask1,A_mask1,S_mask1,R_mask1 = random_mask(T, L, A, S, R, num_layout, sqe_length, ada_length)
    T_mask2,L_mask2,A_mask2,S_mask2,R_mask2 = random_mask(T, L, A, S, R, num_layout, sqe_length, ada_length)

    T_mask = np.concatenate((T_mask1,T_mask2),axis=0)
    L_mask = np.concatenate((L_mask1,L_mask2),axis=0)
    A_mask = np.concatenate((A_mask1,A_mask2),axis=0)
    S_mask = np.concatenate((S_mask1,S_mask2),axis=0)
    R_mask = np.concatenate((R_mask1,R_mask2),axis=0)

    T_ou = np.concatenate((T[:,1:],np.zeros((42548,1))),axis=-1)
    L_ou = np.concatenate((L[:,1:],np.zeros((42548,1,2))),axis=-2)
    A_ou = np.concatenate((A[:,1:],np.zeros((42548,1,14))),axis=-2)
    S_ou = np.concatenate((S[:,1:],np.zeros((42548,1))),axis=-1)
    R_ou = np.concatenate((R[:,1:],np.zeros((42548,1,25))),axis=-2)

    T_in = np.concatenate((T,T),axis=0)
    L_in = np.concatenate((L,L),axis=0)
    A_in = np.concatenate((A,A),axis=0)
    S_in = np.concatenate((S,S),axis=0)
    R_in = np.concatenate((R,R),axis=0)

    T_out = np.concatenate((T_ou,T_ou),axis=0)
    L_out = np.concatenate((L_ou,L_ou),axis=0)
    A_out = np.concatenate((A_ou,A_ou),axis=0)
    S_out = np.concatenate((S_ou,S_ou),axis=0)
    R_out = np.concatenate((R_ou,R_ou),axis=0)

    np.savez('swissD_mask_Train.npz',T=T_mask,L=L_mask,A=A_mask,S=S_mask,R=R_mask)
    np.savez('swissD_input_Train.npz',T=T_in,L=L_in,A=A_in,S=S_in,R=R_in)
    np.savez('swissD_output_Train.npz',T=T_out,L=L_out,A=A_out,S=S_out,R=R_out)

def prepare_MaskPLAN_data_Twice75(T, L, A, S, R, num_layout, sqe_length, ada_length):

    T_mask1,L_mask1,A_mask1,S_mask1,R_mask1 = random_mask75(T, L, A, S, R, num_layout, sqe_length, ada_length)
    T_mask2,L_mask2,A_mask2,S_mask2,R_mask2 = random_mask75(T, L, A, S, R, num_layout, sqe_length, ada_length)

    T_mask = np.concatenate((T_mask1,T_mask2),axis=0)
    L_mask = np.concatenate((L_mask1,L_mask2),axis=0)
    A_mask = np.concatenate((A_mask1,A_mask2),axis=0)
    S_mask = np.concatenate((S_mask1,S_mask2),axis=0)
    R_mask = np.concatenate((R_mask1,R_mask2),axis=0)

    np.savez('swissD_mask_Train75.npz',T=T_mask,L=L_mask,A=A_mask,S=S_mask,R=R_mask)

def prepare_MaskPLAN_data_Triple75new(T, L, A, S, R, num_layout, sqe_length, ada_length):

    T_mask1,L_mask1,A_mask1,S_mask1,R_mask1 = random_mask75(T, L, A, S, R, num_layout, sqe_length, ada_length)
    T_mask2,L_mask2,A_mask2,S_mask2,R_mask2 = random_mask75(T, L, A, S, R, num_layout, sqe_length, ada_length)
    T_mask3,L_mask3,A_mask3,S_mask3,R_mask3 = random_mask75(T, L, A, S, R, num_layout, sqe_length, ada_length)

    T_mask = np.concatenate((T_mask1,T_mask2,T_mask3),axis=0)
    L_mask = np.concatenate((L_mask1,L_mask2,L_mask3),axis=0)
    A_mask = np.concatenate((A_mask1,A_mask2,A_mask3),axis=0)
    S_mask = np.concatenate((S_mask1,S_mask2,S_mask3),axis=0)
    R_mask = np.concatenate((R_mask1,R_mask2,R_mask3),axis=0)

    T_ou = np.concatenate((T[:,1:],np.zeros((num_layout,1))),axis=-1)
    L_ou = np.concatenate((L[:,1:],np.zeros((num_layout,1,2))),axis=-2)
    A_ou = np.concatenate((A[:,1:],np.zeros((num_layout,1,14))),axis=-2)
    S_ou = np.concatenate((S[:,1:],np.zeros((num_layout,1))),axis=-1)
    R_ou = np.concatenate((R[:,1:],np.zeros((num_layout,1,25))),axis=-2)

    T_in = np.concatenate((T,T,T),axis=0)
    L_in = np.concatenate((L,L,L),axis=0)
    A_in = np.concatenate((A,A,A),axis=0)
    S_in = np.concatenate((S,S,S),axis=0)
    R_in = np.concatenate((R,R,R),axis=0)

    T_out = np.concatenate((T_ou,T_ou,T_ou),axis=0)
    L_out = np.concatenate((L_ou,L_ou,L_ou),axis=0)
    S_out = np.concatenate((S_ou,S_ou,S_ou),axis=0)
    A_out = np.concatenate((A_ou,A_ou,A_ou),axis=0)
    R_out = np.concatenate((R_ou,R_ou,R_ou),axis=0)

    np.savez('swissD_input_Trainnew.npz',T=T_in,L=L_in,A=A_in,S=S_in,R=R_in)
    np.savez('swissD_output_Trainnew.npz',T=T_out,L=L_out,A=A_out,S=S_out,R=R_out)
    np.savez('swissD_mask_Train75new.npz',T=T_mask,L=L_mask,A=A_mask,S=S_mask,R=R_mask)

def bound_type_analy(index_list,geo_data,subtype,house_room_types,house_type_index):

    layout_all = []
    type_list = []
    house_type_list = np.zeros((14))
    area = []
    convex = []
    id = []
    layout_house = np.zeros((30))

    for s,i in enumerate(index_list):
        room = geo_data[i][10:-2].split(",")
        room_type = subtype[i]
        room_corners = []
        for j in room:
            xy = j.strip().split(" ")
            if xy[1][-1] == ')':
                xy[1] = xy[1][:-1]
            if xy[0][0] == '(':
                xy[0] = xy[0][1:]
            room_corners.append((float(xy[0]),float(xy[1])))
        rooms_poly = Polygon(room_corners)
        # layout_all.append(rooms_poly)
        if room_type in house_room_types and rooms_poly.area > 2:
            #house_type_list.append(house_type_index[house_room_types.index(room_type)])
            # house_type_list[house_room_types.index(room_type)] += 1
            temp = np.zeros((128,128))

            count = int(len(room_corners)-1)
            if count > 29: count = 29
            layout_house[count] += 1
            # boundbox = rooms_poly.minimum_rotated_rectangle
            # if explain_validity(boundbox) == 'Valid Geometry' and explain_validity(rooms_poly) == 'Valid Geometry':
            #     type_list.append(house_type_index[house_room_types.index(room_type)])
            #     area.append(rooms_poly.area)
            #     cut = boundbox.difference(rooms_poly)
            #     if explain_validity(cut) != 'Valid Geometry':
            #         cut = make_valid(cut).geoms[0]
            #     ratio = cut.area/rooms_poly.area
            #     convex.append(ratio)#count+
            #     id.append(s)

    return layout_house,type_list,house_type_list,area,convex,id

def get_adjacency_graph(extended_house):

    ada = []
    if extended_house.geom_type == 'MultiPolygon':
        geo = extended_house.geoms#.geoms
        num = len(geo)
        for i in range(num):
            if i == num - 1:
                break
            else:
                for m in range(i+1,num):
                    if geo[i].intersects(geo[m]):
                        ada.append([i,m])
    
    return np.array(ada)

def floorplan_to_Json(filename,polygons,names_List,locations_List,types_List,Graph_List,area,Bound,Door,Windows,RDoors):

    rooms = polygons.geoms

    data = {
        "Edges": Graph_List.tolist(),
        "boundary_Corners": Bound,
        "Front_Door": Door,
        "Windows": Windows,
        "Room_Door": RDoors,
        "nodes": [
            {
                "name": names_List[indx],
                "id": type,
                "polygon": list(rooms[indx].exterior.coords),
                "area": area[indx],
                "location": locations_List[indx]
            }
            for indx,type in enumerate(types_List) if type != 0
        ]
    }
    with open(filename, "w") as f:
        json.dump(data, f)
    
def floorplan_to_Json_fab(filename,polygons,names_List,locations_List,types_List,Graph_List,area,Bound,Door,Windows,RDoors,walls_lines,walls_types,module_id, module_coords,prompts):

    rooms = polygons.geoms

    # wall_type_list for reference
    wall_type_list = ['inner_door_waterproof', 'inner_waterproof','inner_door_normal', 'inner_normal',
                       'outter_window_waterproof', 'outter_waterproof','outter_window_normal', 'outter_normal','outter_door_normal']

    # Convert Polygon objects to coordinate lists if needed
    def convert_to_coords(obj):
        """Convert Polygon objects to coordinate lists for JSON serialization"""
        if hasattr(obj, 'exterior'):
            # It's a Polygon object
            return list(obj.exterior.coords)
        elif isinstance(obj, list):
            # It's a list, convert each item
            return [convert_to_coords(item) for item in obj]
        else:
            # It's already serializable
            return obj

    data = {
        "Edges": Graph_List.tolist(),
        # "boundary_Corners": convert_to_coords(Bound),
        # "Front_Door": convert_to_coords(Door),
        # "Windows": convert_to_coords(Windows),
        # "Room_Door": convert_to_coords(RDoors),

        "nodes": [
            {
                "name": names_List[indx],
                "id": type,
                # "polygon": list(rooms[indx].exterior.coords),
                "area": area[indx],
                "location": locations_List[indx]
            }
            for indx,type in enumerate(types_List) if type != 0
        ]
    }

    data['structured_prompt'] = prompts

    # Add modules if module_id is not 0
    if module_id != 0 and module_coords != 0:
        data["modules"] = [
            {
                "id": module_id,
                "coords": module_coords
            }
        ]

    # Add panels (wall panels)
    panels = []
    for wall_line, wall_type in zip(walls_lines, walls_types):
        # Get endpoints from wall_line (LineString returned from get_polygon_centerline_endpoints)
        
        endpoint1 = (wall_line[0],wall_line[1])  # (x1, y1)
        endpoint2 = (wall_line[2],wall_line[3])  # (x2, y2)

        # Calculate wall length
        wall_length = Point(endpoint1).distance(Point(endpoint2))

        # Calculate panel id (max 30) based on length // 0.2
        panel_id = min(int(wall_length // 5), 30)

        # Get wall type index from wall_type_list
        try:
            type_index = wall_type_list.index(wall_type)
        except ValueError:
            # If wall_type not found in list, skip or use default
            type_index = 0

        # Format coords as [endpoint1[0], endpoint1[1], endpoint2[0], endpoint2[1]]
        # which is [x1, y1, x2, y2]
        panel_coords = [int(endpoint1[0]), int(endpoint1[1]), int(endpoint2[0]), int(endpoint2[1])]

        panels.append({
            "type": type_index,
            "id": panel_id,
            "coords": panel_coords
        })

    data["panels"] = panels

    # Count panels for fabrication_info
    total_panels = len(panels)
    panels_with_windows = sum(1 for panel in panels if 'window' in wall_type_list[panel['type']])
    panels_with_doors = sum(1 for panel in panels if 'door' in wall_type_list[panel['type']])

    # Determine descriptors based on thresholds
    if total_panels < 15:
        panels_desc = "less"
    elif total_panels > 30:
        panels_desc = "more"
    else:
        panels_desc = "medium"

    if panels_with_windows < 4:
        windows_desc = "less"
    elif panels_with_windows > 8:
        windows_desc = "more"
    else:
        windows_desc = "medium"

    if panels_with_doors < 4:
        doors_desc = "less"
    elif panels_with_doors > 8:
        doors_desc = "more"
    else:
        doors_desc = "medium"

    # Create fabrication_info string
    data["fabrication_info"] = f"use {panels_desc} panels. use {windows_desc} windows. use {doors_desc} doors."

    with open(filename, "w") as f:
        json.dump(data, f)

def np_rotate(vec,degree):
    # calling np will much faster than shapely rotation
    alpha = degree*np.pi
    x_ = vec[1]*np.sin(alpha)+vec[0]*np.cos(alpha)
    y_ = vec[1]*np.cos(alpha)-vec[0]*np.sin(alpha)
    new = np.array([x_,y_])

    return new

def get_boundbox(center,vec,size):

    pt1 = (center.x + size*(vec[1]-vec[0]),center.y - size*(vec[1]+vec[0]))
    pt2 = (center.x + size*(vec[1]+vec[0]),center.y + size*(vec[1]-vec[0]))
    pt3 = (center.x + size*(vec[0]-vec[1]),center.y + size*(vec[1]+vec[0]))
    pt4 = (center.x - size*(vec[1]+vec[0]),center.y - size*(vec[1]-vec[0]))

    return [pt1,pt2,pt3,pt4,pt1]

def ada_sparse(adacency):

    graph = np.zeros((14,14))
    for i,j in enumerate(adacency):
        for f in range(14):
            graph[i][f][f] = 1
        for m,n in enumerate(j):
            if (n[0] != 0 or n[1] != 0):
                graph[i][int(n[0])][int(n[1])] = 1
                graph[i][int(n[1])][int(n[0])] = 1
    
    return graph

def location_normalize(loc,boundx,boundy,minx,miny):

    return np.array([(loc[0]-minx)/boundx,(loc[1]-miny)/boundy])

def location_onehot(loc,dimension):

    step = 1/dimension
    loc[np.where((0.001<=loc) & (loc<(step*1.5)))] = step
    loc[np.where(loc<0.001)] = 0
    for i in range(dimension-3):
        loc[np.where(((step*i+(step*1.5))<=loc) & (loc<(step*i+(step*2.5))))] = i*step + 2*step
    loc[np.where((1-(step*1.5))<=loc)] = 1 - step
    loc_onehot = np.array(loc.copy()*dimension,dtype=np.int32)

    return loc_onehot

def size_onehot(size,dimension):

    domain = 40
    step = domain/dimension
    step_ind = 1/dimension
    size[np.where((0.001<=size) & (size<(step*1.5)))] = step_ind
    size[np.where(size<0.001)] = 0
    for i in range(dimension-3):
        size[np.where(((step*i+(step*1.5))<=size) & (size<(step*i+(step*2.5))))] = i*step_ind + 2*step_ind
    size[np.where((domain-(step*1.5))<=size)] = 1 - step_ind
    sizes_onehot = np.array(size.copy()*dimension,dtype=np.int32)

    return sizes_onehot

def randint_size75(n, N): 

    if n > 0:

        out = np.random.choice(N, n, replace=True) + 1

    else:
        out = np.array([15])

    return out

def randint_size(n, N, replace=True): 

    return np.random.choice(N, n, replace=False)

def randint_diff(valid): 

    if valid == 1 or valid == 2:

        out = np.array([1])

    else:

        n = np.random.randint(1,round(valid*0.6))

        out = np.sort(np.random.choice(valid-1, n, replace=False)) + 1

    return out

def randint_diff_room123(valid): 

    if valid == 1 or valid == 2:

        out = np.array([1])

    elif valid == 3:

        out = np.array([1,2])

    else:

        n = np.random.randint(1,4)

        out = np.sort(np.random.choice(valid-1, n, replace=False)) + 1

    return out

def mask_ada(idx):
    mask_init = np.zeros((16,14))
    mask_init[0] = 1
    if idx.shape[0] > 1:
        for m,n in enumerate(idx):
            if m == idx.shape[0]-1:
                break
            else:
                mask_init[n+1,idx[m+1]] = 1
                mask_init[idx[m+1]+1,n] = 1
    return mask_init

def random_mask(T, L, A, S, R, num_layout, list_len, list_ada): 
        
        mask_index_T = np.ones((num_layout,list_len))
        mask_index_L = np.ones((num_layout,list_len,2))
        mask_index_A = np.ones((num_layout,list_ada))
        mask_index_S = np.ones((num_layout,list_len))
        mask_index_R = np.ones((num_layout,list_len,25))

        for i in range(num_layout):
            mask_index_T[i][randint_size(np.random.randint(int(list_len/2),int(list_len+1)),list_len)] = 0
            mask_index_L[i][randint_size(np.random.randint(int(list_len/2),int(list_len+1)),list_len)] = 0
            mask_index_A[i][randint_size(np.random.randint(int(list_ada/2),int(list_ada)),list_ada)] = 0
            mask_index_S[i][randint_size(np.random.randint(int(list_len/2),int(list_len+1)),list_len)] = 0
            mask_index_R[i][randint_size(np.random.randint(int(list_len/2),int(list_len+1)),list_len)] = 0
        
        mask_index_A = mask_index_A.reshape((num_layout,list_len,int(list_ada/list_len)))

        T_mask = T*mask_index_T
        L_mask = L*mask_index_L
        A_mask = A*mask_index_A
        S_mask = S*mask_index_S
        R_mask = R*mask_index_R

        return T_mask,L_mask,A_mask,S_mask,R_mask

def random_mask75(T, L, A, S, R, num_layout, list_len, list_ada): 
        
        mask_index_T = np.ones((num_layout,list_len))
        mask_index_L = np.ones((num_layout,list_len,2))
        mask_index_A = np.ones((num_layout,list_len,14))
        mask_index_S = np.ones((num_layout,list_len))
        mask_index_R = np.ones((num_layout,list_len,25))

        for i in range(num_layout):
            mask_index_T[i][randint_size75(np.random.randint(int(list_len*0.5),int(list_len)),list_len-1)] = 0
            mask_index_L[i][randint_size75(np.random.randint(int(list_len*0.5),int(list_len)),list_len-1)] = 0
            mask_index_A[i] = mask_ada(randint_size75(np.random.randint(6,12),13))
            mask_index_S[i][randint_size75(np.random.randint(int(list_len*0.5),int(list_len)),list_len-1)] = 0
            mask_index_R[i][randint_size75(np.random.randint(int(list_len*0.5),int(list_len)),list_len-1)] = 0
        
        # mask_index_A = mask_index_A.reshape((num_layout,list_len,int(list_ada/list_len)))

        T_mask = T*mask_index_T
        L_mask = L*mask_index_L
        A_mask = A*mask_index_A
        S_mask = S*mask_index_S
        R_mask = R*mask_index_R

        return T_mask,L_mask,A_mask,S_mask,R_mask

def random_maskdiff(T, L, A, S, num_layout, list_len): 
        
        T_mask = np.zeros((num_layout,list_len))
        L_mask = np.zeros((num_layout,list_len,2))
        A_mask = np.zeros((num_layout,list_len,14))
        S_mask = np.zeros((num_layout,list_len))

        T_new = np.zeros((num_layout,list_len))
        L_new = np.zeros((num_layout,list_len,2))
        A_new = np.zeros((num_layout,list_len,14))
        S_new = np.zeros((num_layout,list_len))

        entire_sqe = np.arange(list_len)[1:]

        for i in range(num_layout):

            valid = (T[i]==9).argmax(axis=0)-1
            select = randint_diff(valid)
            select_len = select.shape[0]+1

            T_mask[i][1:select_len] = T[i][select]
            T_mask[i][0] = T[i][0]
            remained = np.setdiff1d(entire_sqe, select, assume_unique=False)
            new_sqe = np.hstack((select,remained)) - 1
            T_new[i][1:select_len] = T[i][select]
            T_new[i][select_len:] = T[i][remained]
            T_new[i][0] = T[i][0]
            L_new[i][1:select_len] = L[i][select]
            L_new[i][select_len:] = L[i][remained]
            L_new[i][0] = L[i][0]
            L_mask[i][0] = L[i][0]
            S_new[i][1:select_len] = S[i][select]
            S_new[i][select_len:] = S[i][remained]
            S_new[i][0] = S[i][0]
            S_mask[i][0] = S[i][0]

            A_new[i][0] = A[i][0]
            ada = []
            if valid > 2 :
                for t in range(valid-1):
                    for g in range(t+1,valid):
                        if A[i][t+1][g] == 1:
                            ada.append([t,g])
                ada_np = np.array(ada)
                for h in range(valid):
                    ada_np[np.where(ada_np==new_sqe[h])] = h + 100
                ada_np -= 100
                for q in ada_np:
                    A_new[i][q[0]+1][q[1]] = 1
                    A_new[i][q[1]+1][q[0]] = 1
                A_new[i][valid+1] = np.array([1,0]*7)
            elif valid == 2:
                A_new[i][1][1] = 1
                A_new[i][2][0] = 1
                A_new[i][3] = np.array([1,0]*7)
            else:
                A_new[i][1][0] = 1
                A_new[i][2] = np.array([1,0]*7)
            
            for j in range(2):

                sampled = np.sort(np.random.choice(select_len, round(select_len/2), replace=False))

                if j==0: L_mask[i][sampled] = L_new[i][sampled]
                elif j==1: S_mask[i][sampled] = S_new[i][sampled]

            A_mask[i][1:select_len] = A_new[i][1:select_len].copy()
            A_mask[i][:,select_len-1:] = 0
            A_mask[i][0] = A_new[i][0]

        return T_mask,L_mask,A_mask,S_mask,T_new, L_new, A_new, S_new

def random_maskdiff_123room(T, L, A, S, R, num_layout, list_len): 
        
        T_mask = np.zeros((num_layout,list_len))
        L_mask = np.zeros((num_layout,list_len,2))
        A_mask = np.zeros((num_layout,list_len,14))
        S_mask = np.zeros((num_layout,list_len))
        R_mask = np.zeros((num_layout,list_len,25))

        T_new = np.zeros((num_layout,list_len))
        L_new = np.zeros((num_layout,list_len,2))
        A_new = np.zeros((num_layout,list_len,14))
        S_new = np.zeros((num_layout,list_len))
        R_new = np.zeros((num_layout,list_len,25))

        entire_sqe = np.arange(list_len)[1:]

        for i in range(num_layout):

            valid = (T[i]==9).argmax(axis=0)-1
            select = randint_diff_room123(valid)
            select_len = select.shape[0]+1

            T_mask[i][1:select_len] = T[i][select]
            T_mask[i][0] = T[i][0]
            remained = np.setdiff1d(entire_sqe, select, assume_unique=False)
            new_sqe = np.hstack((select,remained)) - 1
            T_new[i][1:select_len] = T[i][select]
            T_new[i][select_len:] = T[i][remained]
            T_new[i][0] = T[i][0]
            L_new[i][1:select_len] = L[i][select]
            L_new[i][select_len:] = L[i][remained]
            L_new[i][0] = L[i][0]
            L_mask[i][0] = L[i][0]
            S_new[i][1:select_len] = S[i][select]
            S_new[i][select_len:] = S[i][remained]
            S_new[i][0] = S[i][0]
            S_mask[i][0] = S[i][0]
            R_new[i][1:select_len] = R[i][select]
            R_new[i][select_len:] = R[i][remained]
            R_new[i][0] = R[i][0]
            R_mask[i][0] = R[i][0]

            A_new[i][0] = A[i][0]
            ada = []
            if valid > 2 :
                for t in range(valid-1):
                    for g in range(t+1,valid):
                        if A[i][t+1][g] == 1:
                            ada.append([t,g])
                ada_np = np.array(ada)
                for h in range(valid):
                    ada_np[np.where(ada_np==new_sqe[h])] = h + 100
                ada_np -= 100
                for q in ada_np:
                    A_new[i][q[0]+1][q[1]] = 1
                    A_new[i][q[1]+1][q[0]] = 1
                A_new[i][valid+1] = np.array([1,0]*7)
            elif valid == 2:
                A_new[i][1][1] = 1
                A_new[i][2][0] = 1
                A_new[i][3] = np.array([1,0]*7)
            else:
                A_new[i][1][0] = 1
                A_new[i][2] = np.array([1,0]*7)

            L_mask[i][1:select_len] = L_new[i][1:select_len]
            S_mask[i][1:select_len] = S_new[i][1:select_len]

            A_mask[i][1:select_len] = A_new[i][1:select_len].copy()
            A_mask[i][:,select_len-1:] = 0
            A_mask[i][0] = A_new[i][0]

        return T_mask,L_mask,A_mask,S_mask,T_new, L_new, A_new, S_new

def random_maskdiff_123roomL(T, L, A, S, R, num_layout, loops, list_len): 
        
        T_mask = np.zeros((num_layout*loops,list_len))
        L_mask = np.zeros((num_layout*loops,list_len,2))
        A_mask = np.zeros((num_layout*loops,list_len,14))
        S_mask = np.zeros((num_layout*loops,list_len))
        R_mask = np.zeros((num_layout*loops,list_len,25))

        T_new = np.zeros((num_layout*loops,list_len))
        L_new = np.zeros((num_layout*loops,list_len,2))
        A_new = np.zeros((num_layout*loops,list_len,14))
        S_new = np.zeros((num_layout*loops,list_len))
        R_new = np.zeros((num_layout*loops,list_len,25))

        entire_sqe = np.arange(list_len)[1:]

        for i in range(num_layout*loops):

            valid = (T[i%num_layout]==9).argmax(axis=0)-1
            select = randint_diff_room123(valid)
            select_len = select.shape[0]+1

            T_mask[i][1:select_len] = T[i%num_layout][select]
            T_mask[i][0] = T[i%num_layout][0]
            remained = np.setdiff1d(entire_sqe, select, assume_unique=False)
            new_sqe = np.hstack((select,remained)) - 1
            T_new[i][1:select_len] = T[i%num_layout][select]
            T_new[i][select_len:] = T[i%num_layout][remained]
            T_new[i][0] = T[i%num_layout][0]
            L_new[i][1:select_len] = L[i%num_layout][select]
            L_new[i][select_len:] = L[i%num_layout][remained]
            L_new[i][0] = L[i%num_layout][0]
            L_mask[i][0] = L[i%num_layout][0]
            S_new[i][1:select_len] = S[i%num_layout][select]
            S_new[i][select_len:] = S[i%num_layout][remained]
            S_new[i][0] = S[i%num_layout][0]
            S_mask[i][0] = S[i%num_layout][0]
            R_new[i][1:select_len] = R[i%num_layout][select]
            R_new[i][select_len:] = R[i%num_layout][remained]
            R_new[i][0] = R[i%num_layout][0]
            R_mask[i][0] = R[i%num_layout][0]

            A_new[i][0] = A[i%num_layout][0]
            ada = []
            if valid > 2 :
                for t in range(valid-1):
                    for g in range(t+1,valid):
                        if A[i%num_layout][t+1][g] == 1:
                            ada.append([t,g])
                ada_np = np.array(ada)
                for h in range(valid):
                    ada_np[np.where(ada_np==new_sqe[h])] = h + 100
                ada_np -= 100
                for q in ada_np:
                    A_new[i][q[0]+1][q[1]] = 1
                    A_new[i][q[1]+1][q[0]] = 1
                A_new[i][valid+1] = np.array([1,0]*7)
            elif valid == 2:
                A_new[i][1][1] = 1
                A_new[i][2][0] = 1
                A_new[i][3] = np.array([1,0]*7)
            else:
                A_new[i][1][0] = 1
                A_new[i][2] = np.array([1,0]*7)

            L_mask[i][1:select_len] = L_new[i][1:select_len]
            S_mask[i][1:select_len] = S_new[i][1:select_len]

            A_mask[i][1:select_len] = A_new[i][1:select_len]
            A_mask[i][:,select_len-1:] = 0
            A_mask[i][0] = A_new[i][0]

        return T_mask,L_mask,A_mask,S_mask,R_mask,T_new, L_new, A_new, S_new, R_new

def random_mask_inference(T, L, A, S, num_layout, list_len, ratio): 
        
        mask_index_T = np.ones((num_layout,list_len))
        mask_index_L = np.ones((num_layout,list_len,2))
        mask_index_A = np.ones((num_layout,list_len,14))
        mask_index_S = np.ones((num_layout,list_len))
        # mask_index_R = np.ones((num_layout,list_len,25))

        for i in range(num_layout):

            valid = (T[i]==9).argmax(axis=0)
            mask_index_T[i][randint_size75(int(valid*ratio),valid)] = 0
            mask_index_L[i][randint_size75(int(valid*ratio),valid)] = 0
            mask_index_A[i] = mask_ada(randint_size75(int((valid-2)*(1-ratio)),valid-2))
            mask_index_S[i][randint_size75(int(valid*ratio),valid)] = 0
            # mask_index_R[i][randint_size75(round(valid*ratio),valid)] = 0

        T_mask = T*mask_index_T
        L_mask = L*mask_index_L
        A_mask = A*mask_index_A
        S_mask = S*mask_index_S
        # R_mask = R*mask_index_R

        return T_mask,L_mask,A_mask,S_mask

def random_mask_inferenceR(T, L, A, S, R, num_layout, list_len, ratio): 
        
        mask_index_T = np.ones((num_layout,list_len))
        mask_index_L = np.ones((num_layout,list_len,2))
        mask_index_A = np.ones((num_layout,list_len,14))
        mask_index_S = np.ones((num_layout,list_len))
        mask_index_R = np.ones((num_layout,list_len,25))

        for i in range(num_layout):

            valid = (T[i]==9).argmax(axis=0)
            mask_index_T[i][randint_size75(int(valid*ratio),valid)] = 0
            mask_index_L[i][randint_size75(int(valid*ratio),valid)] = 0
            mask_index_A[i] = mask_ada(randint_size75(int((valid-2)*(1-ratio)),valid-2))
            mask_index_S[i][randint_size75(int(valid*ratio),valid)] = 0
            mask_index_R[i][randint_size75(int(valid*ratio),valid)] = 0

        T_mask = T*mask_index_T
        L_mask = L*mask_index_L
        A_mask = A*mask_index_A
        S_mask = S*mask_index_S
        R_mask = R*mask_index_R

        return T_mask,L_mask,A_mask,S_mask,R_mask