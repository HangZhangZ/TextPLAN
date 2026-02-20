from shapely.geometry import Polygon,MultiPolygon,LineString,Point
from shapely.plotting import plot_polygon, plot_line, plot_points
import numpy as np
import json
from shapely.ops import unary_union
from utils import *
from Inference.decode_function import *
import cv2
# import skfmm
import imageio
from shapely.validation import make_valid,explain_validity

def parse_swiss_dewelling_polygon(index_list,geo_data,subtype,house_room_types,house_type_index):

    house_centers = []
    layout_house = []
    rooms_extended = []
    house_type_list = []
    house_type_names = []
    front_door = None
    doors_pt = []
    windows = []
    areas = []
    kitchen = 0
    for i in index_list:
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
        if kitchen == 1 and (room_type == 'KITCHEN_DINING' or room_type == 'KITCHEN'):
            indx_kithen = house_type_list.index(5)
            exist = layout_house[indx_kithen]
            if exist.area < rooms_poly.area:
                layout_house[indx_kithen] = rooms_poly
                rooms_extended[indx_kithen] = rooms_poly.buffer(0.3,join_style=2)
                areas[indx_kithen] = rooms_poly.area
                house_centers[indx_kithen] = [rooms_poly.centroid.x,rooms_poly.centroid.y]
        elif room_type in house_room_types and rooms_poly.area>2:
            house_type_list.append(house_type_index[house_room_types.index(room_type)])
            house_type_names.append(room_type)
            layout_house.append(rooms_poly)
            house_centers.append([rooms_poly.centroid.x,rooms_poly.centroid.y])
            rooms_extended.append(rooms_poly.buffer(0.3,join_style=2))
            areas.append(rooms_poly.area)
            if room_type == 'KITCHEN_DINING' or room_type == 'KITCHEN':
                kitchen = 1
        elif room_type == 'ENTRANCE_DOOR':
            front_door = rooms_poly
        elif room_type == 'DOOR':
            doors_pt.append(rooms_poly)
        elif room_type == 'WINDOW':
            windows.append(rooms_poly)
            
    return layout_house,rooms_extended,house_type_list,house_type_names,house_centers,areas,front_door,doors_pt,windows

def parse_swiss_dewelling_polygon_fab(index_list,geo_data,subtype,house_room_types,house_type_index):

    house_centers = []
    layout_house = []
    rooms_extended = []
    house_type_list = []
    house_type_names = []
    front_door = None
    doors = []
    walls = []
    windows = []
    areas = []

    kitchen = 0
    for i in index_list:
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
        if kitchen == 1 and (room_type == 'KITCHEN_DINING' or room_type == 'KITCHEN'):
            indx_kithen = house_type_list.index(5)
            exist = layout_house[indx_kithen]
            if exist.area < rooms_poly.area:
                layout_house[indx_kithen] = rooms_poly
                rooms_extended[indx_kithen] = rooms_poly.buffer(0.3,join_style=2)
                areas[indx_kithen] = rooms_poly.area
                house_centers[indx_kithen] = [rooms_poly.centroid.x,rooms_poly.centroid.y]
        elif room_type in house_room_types and rooms_poly.area>2:
            house_type_list.append(house_type_index[house_room_types.index(room_type)])
            house_type_names.append(room_type)
            layout_house.append(rooms_poly)
            house_centers.append([rooms_poly.centroid.x,rooms_poly.centroid.y])
            rooms_extended.append(rooms_poly.buffer(0.3,join_style=2))
            areas.append(rooms_poly.area)
            if room_type == 'KITCHEN_DINING' or room_type == 'KITCHEN':
                kitchen = 1
        elif room_type == 'ENTRANCE_DOOR':
            front_door = rooms_poly
        elif room_type == 'DOOR':
            doors.append(rooms_poly)
        elif room_type == 'WINDOW':
            windows.append(rooms_poly)
        elif room_type == 'WALL':
            walls.append(rooms_poly)
            
    return layout_house,rooms_extended,house_type_list,house_type_names,house_centers,areas,front_door,doors,windows,walls


def parse_swiss_dewelling_polygon3D(index_list,geo_data,subtype,elevation,height,house_room_types,house_type_index):

    house_centers = []
    layout_house = []
    rooms_extended = []
    house_type_list = []
    house_type_names = []
    front_door = None
    doors_pt = []
    windows = []
    areas = []
    room_eleva = 100
    room_height = 100
    window_eleva = 100
    window_height = 100
    door_eleva = 100
    door_height = 100
    kitchen = 0
    for i in index_list:
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
        if kitchen == 1 and (room_type == 'KITCHEN_DINING' or room_type == 'KITCHEN'):
            indx_kithen = house_type_list.index(5)
            exist = layout_house[indx_kithen]
            if exist.area < rooms_poly.area:
                layout_house[indx_kithen] = rooms_poly
                rooms_extended[indx_kithen] = rooms_poly.buffer(0.3,join_style=2)
                areas[indx_kithen] = rooms_poly.area
                house_centers[indx_kithen] = [rooms_poly.centroid.x,rooms_poly.centroid.y]
        elif room_type in house_room_types and rooms_poly.area>2:
            house_type_list.append(house_type_index[house_room_types.index(room_type)])
            house_type_names.append(room_type)
            layout_house.append(rooms_poly)
            house_centers.append([rooms_poly.centroid.x,rooms_poly.centroid.y])
            rooms_extended.append(rooms_poly.buffer(0.3,join_style=2))
            areas.append(rooms_poly.area)
            if room_type == 'KITCHEN_DINING' or room_type == 'KITCHEN':
                kitchen = 1
            if room_eleva == 100:
                room_eleva = float(elevation[i])
                room_height = float(height[i])
        elif room_type == 'ENTRANCE_DOOR':
            front_door = rooms_poly
        elif room_type == 'DOOR':
            doors_pt.append(room_corners)
        elif room_type == 'WINDOW':
            windows.append(room_corners)
            
    return layout_house,rooms_extended,house_type_list,house_type_names,house_centers,areas,front_door,doors_pt,windows


def parse_distance_distribution(room_img,boundary_img,contest_img,id):

    img = np.array(room_img)[:,:,0]
    im_bound = np.array(boundary_img)[:,:,-1]
    im_bound[np.where(im_bound == 127)[0],np.where(im_bound == 127)[1]] = 255
    indx_out = np.where(im_bound==0)

    mask = np.ones((128,128))
    geo = img.copy()

    # get boundary polygon
    _, thresh = cv2.threshold(im_bound, 127, 255, 0)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    _, pt = draw_approx_hull_polygon(im_bound, contours, [255])

    poly_bound = Polygon(np.squeeze(pt[0])).buffer(0.1)
    poly_bound_pt = np.array(poly_bound.exterior.coords[:-1])#.buffer(2)
    # boundary mask
    # cv2.fillPoly(mask, [np.array(poly_bound.buffer(2).exterior.coords[:-1])[:,np.newaxis,:].astype(np.int32)], color=255)
    cv2.fillPoly(mask, [poly_bound_pt[:,np.newaxis,:].astype(np.int32)], color=0)

    index_room = np.where(img == 255)

    # Room-Boundary Distance #

    phi = np.where(img, 0, -1) + 0.5
    speed = np.ones_like(phi)
    phi[index_room[0],index_room[1]] = 0.5
    phi = np.ma.MaskedArray(phi, mask)

    site0 = None
    site1 = None
    site2 = None
    site3 = None
    if -0.5 in np.unique(phi) and 0.5 in np.unique(phi):

        sd1 = 255 - skfmm.travel_time(phi, speed, dx=1)*3
        sd1[np.where(sd1<0)] = 0
        sd1[indx_out[0],indx_out[1]] = 0
        index_fd = np.where(im_bound == 255)

        if id == 0:
            site0 = np.zeros((128,128))
            site0[index_fd[0],index_fd[1]] = 255
            site1 = np.ones((128,128))*127
            site1[indx_out[0],indx_out[1]] = 0

        sd1[index_room[0],index_room[1]] = 255
        
        # Room-FrontDoor Distance #

        img[index_room[0],index_room[1]] = 0

        phi = np.where(img, 0, -1) + 0.5
        phi[index_fd[0],index_fd[1]] = 0.5
        # mask[index_room[0],index_room[1]] = 255
        phi  = np.ma.MaskedArray(phi, mask)

        sd2 = 255-skfmm.travel_time(phi, speed, dx=1)*3
        sd2[np.where(sd2<0)] = 0
        sd2[indx_out[0],indx_out[1]] = 0

        if id == 0:
            site2 = sd2.copy()

        sd2[index_room[0],index_room[1]] = 255

        # Room-Contest Distance #

        # cv2.fillPoly(contest_img, [poly_bound_pt[:,np.newaxis,:].astype(np.int32)], color=0)

        _, thresh2 = cv2.threshold(contest_img.astype(np.uint8), 127, 255, 0)
        contours2, _ = cv2.findContours(thresh2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        _, pt2 = draw_approx_hull_polygon(contest_img, contours2, [255])

        poly_bound2 = Polygon(np.squeeze(pt2[0]))
        if explain_validity(poly_bound2) != 'Valid Geometry':
            poly_bound2 = make_valid(poly_bound2).geoms[0]

        poly_bound2 = poly_bound2.difference(poly_bound)
        init_bound = poly_bound.difference(poly_bound.buffer(-1))
        itersec = init_bound.difference(poly_bound2.buffer(2.5))
        if itersec.geom_type == 'MultiPolygon':
            itersec = find_maxgeo(itersec)
        img = img.astype(np.int32)
        if itersec.area > 1:

            cv2.fillPoly(img, [np.array(itersec.exterior.coords[:-1])[:,np.newaxis,:].astype(np.int32)], color=255)
            
            phi = np.where(img, 0, -1) + 0.5
            phi  = np.ma.MaskedArray(phi, mask)

            if -0.5 in np.unique(phi):
                sd3 = 255-skfmm.travel_time(phi, speed, dx=1)*3
                sd3[np.where(sd3<0)] = 0
                sd3[indx_out[0],indx_out[1]] = 0

                if id == 0:
                    site3 = sd3.copy()
                sd3[index_room[0],index_room[1]] = 255
                
            else:
                sd3 = np.zeros_like(sd2)
                indx_in = np.where(im_bound==255)
                sd3[indx_in[0],indx_in[1]] = 127
                if id == 0:
                    site3 = sd3.copy()
                sd3[index_room[0],index_room[1]] = 255

        else:

            sd3 = np.zeros_like(sd2)
            indx_in = np.where(im_bound==255)
            sd3[indx_in[0],indx_in[1]] = 127
            if id == 0:
                site3 = sd3.copy()
            sd3[index_room[0],index_room[1]] = 255

        return 1, geo, sd1, sd2, sd3, site0, site1, site2, site3
    
    else:
        return 0, 0, 0, 0, 0, 0, 0, 0, 0

class Swiss_Dewelling_Ana():

    def __init__(self,house_room_types,house_type_index):

        # self.type_distribution = np.zeros((14))
        # self.bound_domain = []
        # self.area = []
        # self.roomnum = []
        self.house_type_index = house_type_index
        self.house_room_types = house_room_types
        self.corner_distri = np.zeros((30))
        self.convexity = np.ones((9,200000))*1000
        self.areas = np.zeros((9,200000))
        self.indx = np.zeros(9).astype(np.int32)
        self.games = np.zeros((9))
        self.game_scores = np.zeros((9))
        self.convexity_apart_id = np.zeros((9,200000))
        self.convexity_room_id = np.zeros((9,200000))
        
    def transfer_polygons(self,tmp,apart_id):

        corners_all,tpyes_all,tpyes_house,area,convex,ids\
            = bound_type_analy(tmp.index,tmp['geometry'],tmp['entity_subtype'],self.house_room_types,self.house_type_index)

        # for m,n in enumerate(tpyes_all):
        #     self.convexity[n,self.indx[n]] = convex[m]
        #     self.areas[n,self.indx[n]] = area[m]
        #     self.convexity_apart_id[n,self.indx[n]] = apart_id
        #     self.convexity_room_id[n,self.indx[n]] = ids[m]
        #     self.indx[n] = self.indx[n] + 1
        #     if m < len(tpyes_all) - 1:
        #         for k,f in enumerate(tpyes_all[m+1:]):
        #             if n != f:
        #                 if convex[m] > convex[k] + 0.001:
        #                     self.game_scores[n] += 3
        #                     self.games[n] += 1
        #                     self.games[f] += 1
        #                 elif convex[m] + 0.001 < convex[k]:
        #                     self.game_scores[f] += 3
        #                     self.games[n] += 1
        #                     self.games[f] += 1
        #                 else:
        #                     self.game_scores[n] += 1
        #                     self.game_scores[f] += 1
        #                     self.games[n] += 1
        #                     self.games[f] += 1

        # self.type_distribution += tpyes_house
        self.corner_distri += corners_all
        # boundary_domain = [0,0]
        # if tpyes_all != []:
        #     self.roomnum.append(len(tpyes_all))
        #     self.area.extend(area)
        #     floorplan_all_polygon = MultiPolygon(corners_all)

        #     boundary = unary_union(floorplan_all_polygon.buffer(0.1,join_style=2))
        #     while boundary.geom_type == 'MultiPolygon':
        #         boundary = boundary.buffer(0.1,join_style=2)
        #     boundary_domainxy = boundary.bounds
        #     boundary_domain[0] = boundary_domainxy[2] - boundary_domainxy[0]
        #     boundary_domain[1] = boundary_domainxy[3] - boundary_domainxy[1]
        # self.bound_domain.append(boundary_domain)

class Swiss_Dewelling_Frontdoor():

    def __init__(self,house_room_types,house_type_index,loc_dimension,area_dimension):

        self.house_room_types = house_room_types
        self.house_type_index = house_type_index
        self.C_Dimen = loc_dimension
        self.S_Dimen = area_dimension

        self.count = 0
    
    def reset(self):

        self.front_door = None

    def transfer_polygons(self,tmp,ind,contest):

        # real-world data
        corners_house,extended_house,tpyes_house,types_names,house_centers,house_areas,front_door,doorsPt,windowsPt\
            = parse_swiss_dewelling_polygon(tmp.index,tmp['geometry'],tmp['entity_subtype'],self.house_room_types,self.house_type_index)

        if tpyes_house != [] and len(tpyes_house) < 15:

            floorplan_house_polygon = MultiPolygon(corners_house)
            boundary = unary_union(floorplan_house_polygon.buffer(0.05,join_style=2))

            while boundary.geom_type == 'MultiPolygon':
                boundary = boundary.buffer(0.1,join_style=2)
            if list(boundary.interiors) != []:
                for inte in list(boundary.interiors):
                    boundary = unary_union(MultiPolygon([boundary,Polygon(inte).buffer(0.1,join_style=2)]))
            
            self.boundary_domainxy = boundary.bounds # (minx, miny, maxx, maxy)
            boundx = self.boundary_domainxy[2] - self.boundary_domainxy[0]
            boundy = self.boundary_domainxy[3] - self.boundary_domainxy[1]
            self.boundary = boundary

            if boundx <= 20 and boundy <= 20:

                if front_door == None:
                    front_door_corners = [[0,0],[0,1],[1,1],[0,0]]
                    front_door = Polygon(front_door_corners)
                else:
                    front_door_corners = list(front_door.exterior.coords)
                
                frondoor_center = front_door.centroid
                self.front_door = np.array([int(25*(frondoor_center.x - self.boundary_domainxy[0])/boundx),
                                            int(25*(frondoor_center.y - self.boundary_domainxy[1])/boundy)])


                return 1, self.front_door
            
            else:

                return 0, 0

class Swiss_Dewelling_Window():

    def __init__(self,house_room_types,house_type_index,loc_dimension,area_dimension):

        self.house_room_types = house_room_types
        self.house_type_index = house_type_index
        self.C_Dimen = loc_dimension
        self.S_Dimen = area_dimension
        self.bound_img = np.zeros((128,128,4))
        self.type = np.zeros((14))
        self.location = np.zeros((14,2)) # one-hot with 32 steps in range boundary box
        self.adjacency = np.zeros((14,14))
        self.areas = np.zeros((14)) # one-hot with 40 steps in range 40
        self.loc_img = []
        self.regions = [] # save as img

        self.count = 0
    
    def reset(self):
        self.bound_img = np.zeros((128,128,4))
        self.type = np.zeros((14))
        self.location = np.zeros((14,2)) # one-hot with 32 steps in range boundary box
        self.adjacency = np.zeros((14,14))
        self.areas = np.zeros((14)) # one-hot with 40 steps in range 40
        self.loc_img = []
        self.regions = []
        self.front_door = None

    def transfer_polygons(self,tmp,ind,contest):

        # real-world data
        corners_house,extended_house,tpyes_house,types_names,house_centers,house_areas,front_door,doorsPt,windows\
            = parse_swiss_dewelling_polygon(tmp.index,tmp['geometry'],tmp['entity_subtype'],self.house_room_types,self.house_type_index)

        if tpyes_house != [] and len(tpyes_house) < 15:

            floorplan_house_polygon = MultiPolygon(corners_house)
            boundary = unary_union(floorplan_house_polygon.buffer(0.05,join_style=2))

            while boundary.geom_type == 'MultiPolygon':
                boundary = boundary.buffer(0.1,join_style=2)
            if list(boundary.interiors) != []:
                for inte in list(boundary.interiors):
                    boundary = unary_union(MultiPolygon([boundary,Polygon(inte).buffer(0.1,join_style=2)]))
            
            self.boundary_domainxy = boundary.bounds # (minx, miny, maxx, maxy)
            boundx = self.boundary_domainxy[2] - self.boundary_domainxy[0]
            boundy = self.boundary_domainxy[3] - self.boundary_domainxy[1]
            self.boundary = boundary

            if boundx <= 20 and boundy <= 20:
                self.corners_house = corners_house
                self.house_centers = house_centers

                ada_list = get_adjacency_graph(MultiPolygon(extended_house))
                boundary_corners = list(boundary.minimum_rotated_rectangle.exterior.coords)
                bound_all_corners = list(boundary.exterior.coords)
                boundary_pt = np.array(boundary_corners)[:-1]
                index_miny = np.where(boundary_pt[:,1] == np.min(boundary_pt[:,1]))[0][0]
                vector = boundary_pt[index_miny - 1] - boundary_pt[index_miny]
                normalized_vector = vector/np.linalg.norm(vector)
                self.vec = normalized_vector

                if front_door == None:
                    front_door_corners = [[0,0],[0,1],[1,1],[0,0]]
                    front_door = Polygon(front_door_corners)
                else:
                    front_door_corners = list(front_door.exterior.coords)
                
                frondoor_center = front_door.centroid
                new_frontdoor = Polygon(get_boundbox(frondoor_center,normalized_vector,0.75))
                contest_cut = contest.difference(boundary)
                contest_cut = contest_cut.difference(new_frontdoor)
                boundary_cut = boundary.difference(new_frontdoor)
                if contest_cut.geom_type == 'MultiPolygon':
                    contest_cut = contest_cut.geoms[0]
                if boundary_cut.geom_type == 'MultiPolygon':
                    boundary_cut = boundary_cut.geoms[0]   

                boudnary_center = [boundary.centroid.x*6.4,boundary.centroid.y*6.4]
                move_x =  64 - boudnary_center[0]
                move_y =  64 - boudnary_center[1]
                self.front_door = np.array([int(frondoor_center.x*6.4 + move_x),int(frondoor_center.y*6.4 + move_y)])
                boundary_cut_coords = scale_to_img(6.4,move_x,move_y,boundary_cut)
                contest_cut_coords = scale_to_img(6.4,move_x,move_y,contest_cut)
                frontdoor_coords = scale_to_img(6.4,move_x,move_y,new_frontdoor)

                boundary_cut_coords[np.where(boundary_cut_coords>127)] = 127
                boundary_cut_coords[np.where(boundary_cut_coords<0)] = 0
                contest_cut_coords[np.where(contest_cut_coords>127)] = 127
                contest_cut_coords[np.where(contest_cut_coords<0)] = 0

                temp_boundAlpha = np.zeros((128,128))
                temp_boundrgb = np.zeros((128,128))

                temp_boundAlpha = cv2.fillPoly(temp_boundAlpha, contest_cut_coords.astype(np.int32), color=255)
                temp_boundAlpha = cv2.fillPoly(temp_boundAlpha, boundary_cut_coords.astype(np.int32), color=255)
                temp_boundrgb = cv2.fillPoly(temp_boundrgb, boundary_cut_coords.astype(np.int32), color=127)

                temp_boundAlpha = cv2.fillPoly(temp_boundAlpha, frontdoor_coords.astype(np.int32), color=255)
                temp_boundrgb = cv2.fillPoly(temp_boundrgb, frontdoor_coords.astype(np.int32), color=255)

                self.bound_img[:,:,3] = temp_boundAlpha
                for m in range(3):
                    self.bound_img[:,:,m] = temp_boundrgb
                file_img = 'parsed/boundary/%d.png' % (ind) #'parsed/boundary/%d_%s.jpg' % (ind, id_name)
                # file_json = 'parsed/graph/%d.json' % (ind) #'parsed/graph/%d_%s.json' % (ind, id_name)

                # real-world data to json
                # floorplan_to_Json(file_json,floorplan_house_polygon,types_names,house_centers,
                #     tpyes_house,ada_list,house_areas,bound_all_corners,front_door_corners,windowsPt,doorsPt)
                # cv2.imwrite(file_img, self.bound_img)

                self.reorder(move_x,move_y,tpyes_house,house_centers,boundx,boundy,
                    self.boundary_domainxy[0],self.boundary_domainxy[1],house_areas,ada_list,corners_house)
                
                loc_onehot, area_onehot = self.one_hot()

                all_windows = MultiPolygon(windows)
                all_doors = MultiPolygon(doorsPt)
                # original_img = cv2.imread('GT/boundary_layout512_graph_site/%d.jpg' % (int(ind)))
                original_img = cv2.imread('GT/boundary_distan_512_site/%d.jpg' % (int(ind)))

                # bound = ((original_img[:,:,0]==127)&(original_img[:,:,1]==127)&(original_img[:,:,2]==127))
                # bound_mask = bound*np.ones((512,512))
                # bound_pixels = np.where(bound_mask==1)
                boudnary_centerl = [boundary.centroid.x*25.6,boundary.centroid.y*25.6]
                move_xx =  256 - boudnary_centerl[0]
                move_yy =  256 - boudnary_centerl[1]
                for f in all_windows.geoms:
                    windows_scaled = scale_to_img(25.6,move_xx,move_yy,f)
                    original_img = cv2.fillPoly(original_img, windows_scaled.astype(np.int32), color=[0,0,255])
                for d in all_doors.geoms:
                    doors_scaled = scale_to_img(25.6,move_xx,move_yy,d)
                    original_img = cv2.fillPoly(original_img, doors_scaled.astype(np.int32), color=[255,0,0])
                # for i in range(3):
                #     original_img[bound_pixels[0],bound_pixels[1],i] = 127
                cv2.imwrite("GT/boundary_distan_512_window/%d.jpg" % (int(ind)),original_img)

                return self.Tokenization(loc_onehot, area_onehot, move_x, move_y, frontdoor_coords, ind)
            
            else:

                return 0, 0, 0, 0, 0

    def reorder(self,Mx,My,T,C,boundx,boundy,bondxmin,bondymin,S,A,R):

        for k in range(len(T)):
            self.adjacency[k][k] = 1

        # Living Room First (Rplan/iPLAN used) T type C location S size A adjacency R region
        if 1 in T: # Living Room existing in layout
            ind_living = int(np.where(np.array(T) == 1)[0][0])
            self.type[0] = 1

            self.regions.append(scale_to_img(6.4,Mx,My,R[ind_living]))
            self.loc_img.append(scale_to_img(6.4,Mx,My,Polygon(get_boundbox(Point(C[ind_living]),self.vec,0.5))))
            self.areas[0] = S[ind_living]
            self.location[0] = location_normalize(C[ind_living],boundx,boundy,bondxmin,bondymin)
            ind = 1

            if ind_living != 0:
                A[np.where(A == ind_living)] = 100
                A[np.where(A < ind_living)] += 1
                A[np.where(A == 100)] = 0

            for n in A:
                self.adjacency[n[0]][n[1]] = 1
                self.adjacency[n[1]][n[0]] = 1

            # del T[ind_living]
            for i,j in enumerate(T):
                if j == 1:
                    continue
                else:
                    self.type[ind] = j
                    self.areas[ind] = S[i]
                    self.location[ind] = location_normalize(C[i],boundx,boundy,bondxmin,bondymin)
                    self.loc_img.append(scale_to_img(6.4,Mx,My,Polygon(get_boundbox(Point(C[i]),self.vec,0.5))))
                    self.regions.append(scale_to_img(6.4,Mx,My,R[i]))
                    ind += 1
        
        else: # no living room in layout

            for n in A:
                self.adjacency[n[0]][n[1]] = 1
                self.adjacency[n[1]][n[0]] = 1

            for i,j in enumerate(T):

                self.type[i] = j
                self.areas[i] = S[i]
                self.location[i] = location_normalize(C[i],boundx,boundy,bondxmin,bondymin)
                self.loc_img.append(scale_to_img(6.4,Mx,My,Polygon(get_boundbox(Point(C[i]),self.vec,0.5))))
                self.regions.append(scale_to_img(6.4,Mx,My,R[i]))

    def one_hot(self):

        loc_onehot = location_onehot(self.location,self.C_Dimen)
        area_onehot = size_onehot(self.areas,self.S_Dimen)

        return loc_onehot,area_onehot

    def Tokenization(self, L_onehot, S_onehot, Mx, My, frontdoor_coords, ind):

        type_token = np.insert(self.type,0,10,axis = 0) # start
        type_token = np.insert(type_token,15,0,axis = 0) # final

        loc_token = np.insert(L_onehot,0,np.array([self.C_Dimen-1]*2),axis = 0) # start
        loc_token = np.insert(loc_token,15,0,axis = 0) # final

        ada_token = np.insert(self.adjacency,0,np.ones((14)),axis = 0) # start
        ada_token = np.insert(ada_token,15,np.zeros((14)),axis = 0) # final

        area_token = np.insert(S_onehot,0,self.S_Dimen-1,axis = 0) # start
        area_token = np.insert(area_token,15,0,axis = 0) # final

        end_id = np.where(type_token==0)[0][0] # end
        type_token[end_id] = 9 
        loc_token[end_id] = np.array([self.C_Dimen-2]*2)
        ada_token[end_id] = np.array([0.5]*14)
        area_token[end_id] = self.S_Dimen-2

        img_data = np.ones((128, 128, 4),dtype=np.int32)
        outter_boundary = self.boundary.buffer(0.4,join_style=2)
        boundary_scaled_coords = scale_to_img(6.4, Mx, My, self.boundary)
        outter_boundary_scaled_coords = scale_to_img(6.4, Mx, My, outter_boundary)

        temp_boundAlpha = np.zeros((128,128))
        temp_boundrgb = np.zeros((128,128))

        temp_boundAlpha = cv2.fillPoly(temp_boundAlpha, outter_boundary_scaled_coords.astype(np.int32), color=127)
        temp_boundAlpha = cv2.fillPoly(temp_boundAlpha, frontdoor_coords.astype(np.int32), color=255)
        img_data[:,:,3] = temp_boundAlpha
        cv2.imwrite("parsed/location/0/%d.png" % (ind), img_data)
        cv2.imwrite("parsed/region/0/%d.png" % (ind), img_data)
        cv2.imwrite("parsed/location_all/%d.png" % (self.count), img_data)
        cv2.imwrite("parsed/region_all/%d.png" % (self.count), img_data)
        temp_boundAlpha = cv2.fillPoly(temp_boundAlpha, boundary_scaled_coords.astype(np.int32), color=0)
        temp_boundAlpha = cv2.fillPoly(temp_boundAlpha, frontdoor_coords.astype(np.int32), color=255)

        self.count += 1
        img_data[:,:,0:3] = 0
        img_data[:,:,3] = temp_boundAlpha
        temp_boundAlpha_main = temp_boundAlpha.copy()

        for m,n in enumerate(self.loc_img):

            temp_room = np.zeros((128,128))
            temp_boundAlpha = temp_boundAlpha_main.copy()

            temp_boundrgb[:,:] = 0
            temp_boundrgb = cv2.fillPoly(temp_boundrgb, n.astype(np.int32), color=255)

            for k in range(3):

                img_data[:,:,k] = temp_boundrgb

            temp_boundAlpha = cv2.fillPoly(temp_boundAlpha, n.astype(np.int32), color=255)
            img_data[:,:,3] = temp_boundAlpha

            cv2.imwrite("parsed/location/%d/%d.png" % (m+1,ind), img_data)
            cv2.imwrite("parsed/location_all/%d.png" % (self.count), img_data)

            temp_boundrgb = cv2.fillPoly(temp_boundrgb, self.regions[m].astype(np.int32), color=255)
            temp_room = cv2.fillPoly(temp_room, self.regions[m].astype(np.int32), color=255)

            # _, thresh2 = cv2.threshold(temp_room, 120, 255, 0)
            # contours2, _ = cv2.findContours(thresh2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            # _,pt2 = draw_approx_hull_polygon(temp_room, contours2, [255])

            for k in range(3):

                img_data[:,:,k] = temp_boundrgb

            temp_boundAlpha = cv2.fillPoly(temp_boundAlpha, self.regions[m].astype(np.int32), color=255)
            img_data[:,:,3] = temp_boundAlpha
            cv2.imwrite("parsed/region/%d/%d.png" % (m+1,ind), img_data)
            cv2.imwrite("parsed/region_all/%d.png" % (self.count), img_data)

            self.count += 1

        return 1, type_token, loc_token, ada_token, area_token

class Swiss_Dewelling_DataProcess():

    def __init__(self,house_room_types,house_type_index,loc_dimension,area_dimension):

        self.house_room_types = house_room_types
        self.house_type_index = house_type_index
        self.C_Dimen = loc_dimension
        self.S_Dimen = area_dimension
        self.bound_img = np.zeros((128,128,4))
        self.type = np.zeros((14))
        self.location = np.zeros((14,2)) # one-hot with 32 steps in range boundary box
        self.adjacency = np.zeros((14,14))
        self.areas = np.zeros((14)) # one-hot with 40 steps in range 40
        self.loc_img = []
        self.regions = [] # save as img

        self.count = 0
    
    def reset(self):
        self.bound_img = np.zeros((128,128,4))
        self.type = np.zeros((14))
        self.location = np.zeros((14,2)) # one-hot with 32 steps in range boundary box
        self.adjacency = np.zeros((14,14))
        self.areas = np.zeros((14)) # one-hot with 40 steps in range 40
        self.loc_img = []
        self.regions = []
        self.front_door = None

    def transfer_polygons(self,tmp,ind,contest):

        # real-world data
        corners_house,extended_house,tpyes_house,types_names,house_centers,house_areas,front_door,doorsPt,windowsPt\
            = parse_swiss_dewelling_polygon(tmp.index,tmp['geometry'],tmp['entity_subtype'],self.house_room_types,self.house_type_index)

        if tpyes_house != [] and len(tpyes_house) < 15:

            floorplan_house_polygon = MultiPolygon(corners_house)
            boundary = unary_union(floorplan_house_polygon.buffer(0.05,join_style=2))

            while boundary.geom_type == 'MultiPolygon':
                boundary = boundary.buffer(0.1,join_style=2)
            if list(boundary.interiors) != []:
                for inte in list(boundary.interiors):
                    boundary = unary_union(MultiPolygon([boundary,Polygon(inte).buffer(0.1,join_style=2)]))
            
            self.boundary_domainxy = boundary.bounds # (minx, miny, maxx, maxy)
            boundx = self.boundary_domainxy[2] - self.boundary_domainxy[0]
            boundy = self.boundary_domainxy[3] - self.boundary_domainxy[1]
            self.boundary = boundary

            if boundx <= 20 and boundy <= 20:
                self.corners_house = corners_house
                self.house_centers = house_centers

                ada_list = get_adjacency_graph(MultiPolygon(extended_house))
                boundary_corners = list(boundary.minimum_rotated_rectangle.exterior.coords)
                bound_all_corners = list(boundary.exterior.coords)
                boundary_pt = np.array(boundary_corners)[:-1]
                index_miny = np.where(boundary_pt[:,1] == np.min(boundary_pt[:,1]))[0][0]
                vector = boundary_pt[index_miny - 1] - boundary_pt[index_miny]
                normalized_vector = vector/np.linalg.norm(vector)
                self.vec = normalized_vector

                if front_door == None:
                    front_door_corners = [[0,0],[0,1],[1,1],[0,0]]
                    front_door = Polygon(front_door_corners)
                else:
                    front_door_corners = list(front_door.exterior.coords)
                
                frondoor_center = front_door.centroid
                new_frontdoor = Polygon(get_boundbox(frondoor_center,normalized_vector,0.75))
                contest_cut = contest.difference(boundary)
                contest_cut = contest_cut.difference(new_frontdoor)
                boundary_cut = boundary.difference(new_frontdoor)
                if contest_cut.geom_type == 'MultiPolygon':
                    contest_cut = contest_cut.geoms[0]
                if boundary_cut.geom_type == 'MultiPolygon':
                    boundary_cut = boundary_cut.geoms[0]   

                boudnary_center = [boundary.centroid.x*6.4,boundary.centroid.y*6.4]
                move_x =  64 - boudnary_center[0]
                move_y =  64 - boudnary_center[1]
                self.front_door = np.array([int(frondoor_center.x*6.4 + move_x),int(frondoor_center.y*6.4 + move_y)])
                boundary_cut_coords = scale_to_img(6.4,move_x,move_y,boundary_cut)
                contest_cut_coords = scale_to_img(6.4,move_x,move_y,contest_cut)
                frontdoor_coords = scale_to_img(6.4,move_x,move_y,new_frontdoor)

                boundary_cut_coords[np.where(boundary_cut_coords>127)] = 127
                boundary_cut_coords[np.where(boundary_cut_coords<0)] = 0
                contest_cut_coords[np.where(contest_cut_coords>127)] = 127
                contest_cut_coords[np.where(contest_cut_coords<0)] = 0

                temp_boundAlpha = np.zeros((128,128))
                temp_boundrgb = np.zeros((128,128))

                temp_boundAlpha = cv2.fillPoly(temp_boundAlpha, contest_cut_coords.astype(np.int32), color=255)
                temp_boundAlpha = cv2.fillPoly(temp_boundAlpha, boundary_cut_coords.astype(np.int32), color=255)
                temp_boundrgb = cv2.fillPoly(temp_boundrgb, boundary_cut_coords.astype(np.int32), color=127)

                temp_boundAlpha = cv2.fillPoly(temp_boundAlpha, frontdoor_coords.astype(np.int32), color=255)
                temp_boundrgb = cv2.fillPoly(temp_boundrgb, frontdoor_coords.astype(np.int32), color=255)

                self.bound_img[:,:,3] = temp_boundAlpha
                for m in range(3):
                    self.bound_img[:,:,m] = temp_boundrgb
                file_img = 'parsed/boundary/%d.png' % (ind) #'parsed/boundary/%d_%s.jpg' % (ind, id_name)
                file_json = 'parsed/graph/%d.json' % (ind) #'parsed/graph/%d_%s.json' % (ind, id_name)

                # real-world data to json
                floorplan_to_Json(file_json,floorplan_house_polygon,types_names,house_centers,
                    tpyes_house,ada_list,house_areas,bound_all_corners,front_door_corners,windowsPt,doorsPt)
                cv2.imwrite(file_img, self.bound_img)

                self.reorder(move_x,move_y,tpyes_house,house_centers,boundx,boundy,
                    self.boundary_domainxy[0],self.boundary_domainxy[1],house_areas,ada_list,corners_house)
                
                loc_onehot, area_onehot = self.one_hot()

                return self.Tokenization(loc_onehot, area_onehot, move_x, move_y, frontdoor_coords, ind)
            
            else:

                return 0, 0, 0, 0, 0

    def reorder(self,Mx,My,T,C,boundx,boundy,bondxmin,bondymin,S,A,R):

        for k in range(len(T)):
            self.adjacency[k][k] = 1

        # Living Room First (Rplan/iPLAN used) T type C location S size A adjacency R region
        if 1 in T: # Living Room existing in layout
            ind_living = int(np.where(np.array(T) == 1)[0][0])
            self.type[0] = 1

            self.regions.append(scale_to_img(6.4,Mx,My,R[ind_living]))
            self.loc_img.append(scale_to_img(6.4,Mx,My,Polygon(get_boundbox(Point(C[ind_living]),self.vec,0.5))))
            self.areas[0] = S[ind_living]
            self.location[0] = location_normalize(C[ind_living],boundx,boundy,bondxmin,bondymin)
            ind = 1

            if ind_living != 0:
                A[np.where(A == ind_living)] = 100
                A[np.where(A < ind_living)] += 1
                A[np.where(A == 100)] = 0

            for n in A:
                self.adjacency[n[0]][n[1]] = 1
                self.adjacency[n[1]][n[0]] = 1

            # del T[ind_living]
            for i,j in enumerate(T):
                if j == 1:
                    continue
                else:
                    self.type[ind] = j
                    self.areas[ind] = S[i]
                    self.location[ind] = location_normalize(C[i],boundx,boundy,bondxmin,bondymin)
                    self.loc_img.append(scale_to_img(6.4,Mx,My,Polygon(get_boundbox(Point(C[i]),self.vec,0.5))))
                    self.regions.append(scale_to_img(6.4,Mx,My,R[i]))
                    ind += 1
        
        else: # no living room in layout

            for n in A:
                self.adjacency[n[0]][n[1]] = 1
                self.adjacency[n[1]][n[0]] = 1

            for i,j in enumerate(T):

                self.type[i] = j
                self.areas[i] = S[i]
                self.location[i] = location_normalize(C[i],boundx,boundy,bondxmin,bondymin)
                self.loc_img.append(scale_to_img(6.4,Mx,My,Polygon(get_boundbox(Point(C[i]),self.vec,0.5))))
                self.regions.append(scale_to_img(6.4,Mx,My,R[i]))

    def one_hot(self):

        loc_onehot = location_onehot(self.location,self.C_Dimen)
        area_onehot = size_onehot(self.areas,self.S_Dimen)

        return loc_onehot,area_onehot

    def Tokenization(self, L_onehot, S_onehot, Mx, My, frontdoor_coords, ind):

        type_token = np.insert(self.type,0,10,axis = 0) # start
        type_token = np.insert(type_token,15,0,axis = 0) # final

        loc_token = np.insert(L_onehot,0,np.array([self.C_Dimen-1]*2),axis = 0) # start
        loc_token = np.insert(loc_token,15,0,axis = 0) # final

        ada_token = np.insert(self.adjacency,0,np.ones((14)),axis = 0) # start
        ada_token = np.insert(ada_token,15,np.zeros((14)),axis = 0) # final

        area_token = np.insert(S_onehot,0,self.S_Dimen-1,axis = 0) # start
        area_token = np.insert(area_token,15,0,axis = 0) # final

        end_id = np.where(type_token==0)[0][0] # end
        type_token[end_id] = 9 
        loc_token[end_id] = np.array([self.C_Dimen-2]*2)
        ada_token[end_id] = np.array([0.5]*14)
        area_token[end_id] = self.S_Dimen-2

        img_data = np.ones((128, 128, 4),dtype=np.int32)
        outter_boundary = self.boundary.buffer(0.4,join_style=2)
        boundary_scaled_coords = scale_to_img(6.4, Mx, My, self.boundary)
        outter_boundary_scaled_coords = scale_to_img(6.4, Mx, My, outter_boundary)

        temp_boundAlpha = np.zeros((128,128))
        temp_boundrgb = np.zeros((128,128))

        temp_boundAlpha = cv2.fillPoly(temp_boundAlpha, outter_boundary_scaled_coords.astype(np.int32), color=127)
        temp_boundAlpha = cv2.fillPoly(temp_boundAlpha, frontdoor_coords.astype(np.int32), color=255)
        img_data[:,:,3] = temp_boundAlpha
        cv2.imwrite("parsed/location/0/%d.png" % (ind), img_data)
        cv2.imwrite("parsed/region/0/%d.png" % (ind), img_data)
        cv2.imwrite("parsed/location_all/%d.png" % (self.count), img_data)
        cv2.imwrite("parsed/region_all/%d.png" % (self.count), img_data)
        temp_boundAlpha = cv2.fillPoly(temp_boundAlpha, boundary_scaled_coords.astype(np.int32), color=0)
        temp_boundAlpha = cv2.fillPoly(temp_boundAlpha, frontdoor_coords.astype(np.int32), color=255)

        self.count += 1
        img_data[:,:,0:3] = 0
        img_data[:,:,3] = temp_boundAlpha
        temp_boundAlpha_main = temp_boundAlpha.copy()

        for m,n in enumerate(self.loc_img):
            temp_boundAlpha = temp_boundAlpha_main.copy()

            temp_boundrgb[:,:] = 0
            temp_boundrgb = cv2.fillPoly(temp_boundrgb, n.astype(np.int32), color=255)

            for k in range(3):
                img_data[:,:,k] = temp_boundrgb
            temp_boundAlpha = cv2.fillPoly(temp_boundAlpha, n.astype(np.int32), color=255)
            img_data[:,:,3] = temp_boundAlpha
            cv2.imwrite("parsed/location/%d/%d.png" % (m+1,ind), img_data)
            cv2.imwrite("parsed/location_all/%d.png" % (self.count), img_data)

            temp_boundrgb = cv2.fillPoly(temp_boundrgb, self.regions[m].astype(np.int32), color=255)
            for k in range(3):
                img_data[:,:,k] = temp_boundrgb
            temp_boundAlpha = cv2.fillPoly(temp_boundAlpha, self.regions[m].astype(np.int32), color=255)
            img_data[:,:,3] = temp_boundAlpha
            cv2.imwrite("parsed/region/%d/%d.png" % (m+1,ind), img_data)
            cv2.imwrite("parsed/region_all/%d.png" % (self.count), img_data)

            self.count += 1

        return 1, type_token, loc_token, ada_token, area_token
    



class Swiss_Dewelling_DataProcess_Floor():

    def __init__(self,house_room_types,house_type_index,loc_dimension,area_dimension):

        self.house_room_types = house_room_types
        self.house_type_index = house_type_index
        self.C_Dimen = loc_dimension
        self.S_Dimen = area_dimension
        self.bound_img = np.zeros((128,128,4))
        self.type = np.zeros((14))
        self.location = np.zeros((14,2)) # one-hot with 32 steps in range boundary box
        self.adjacency = np.zeros((14,14))
        self.areas = np.zeros((14)) # one-hot with 40 steps in range 40
        self.loc_img = []
        self.regions = [] # save as img

        self.count = 0
    
    def reset(self):
        self.bound_img = np.zeros((128,128,4))
        self.type = np.zeros((14))
        self.location = np.zeros((14,2)) # one-hot with 32 steps in range boundary box
        self.adjacency = np.zeros((14,14))
        self.areas = np.zeros((14)) # one-hot with 40 steps in range 40
        self.loc_img = []
        self.regions = []
        self.front_door = None

    def transfer_polygons(self,tmp,ind,contest):

        # real-world data
        corners_house,extended_house,tpyes_house,types_names,house_centers,house_areas,front_door,doorsPt,windowsPt\
            = parse_swiss_dewelling_polygon(tmp.index,tmp['geometry'],tmp['entity_subtype'],self.house_room_types,self.house_type_index)

        if tpyes_house != [] and len(tpyes_house) < 15:

            floorplan_house_polygon = MultiPolygon(corners_house)
            boundary = unary_union(floorplan_house_polygon.buffer(0.05,join_style=2))

            while boundary.geom_type == 'MultiPolygon':
                boundary = boundary.buffer(0.1,join_style=2)
            if list(boundary.interiors) != []:
                for inte in list(boundary.interiors):
                    boundary = unary_union(MultiPolygon([boundary,Polygon(inte).buffer(0.1,join_style=2)]))
            
            self.boundary_domainxy = boundary.bounds # (minx, miny, maxx, maxy)
            boundx = self.boundary_domainxy[2] - self.boundary_domainxy[0]
            boundy = self.boundary_domainxy[3] - self.boundary_domainxy[1]
            self.boundary = boundary

            if boundx <= 20 and boundy <= 20:
                self.corners_house = corners_house
                self.house_centers = house_centers

                ada_list = get_adjacency_graph(MultiPolygon(extended_house))
                boundary_corners = list(boundary.minimum_rotated_rectangle.exterior.coords)
                bound_all_corners = list(boundary.exterior.coords)
                boundary_pt = np.array(boundary_corners)[:-1]
                index_miny = np.where(boundary_pt[:,1] == np.min(boundary_pt[:,1]))[0][0]
                vector = boundary_pt[index_miny - 1] - boundary_pt[index_miny]
                normalized_vector = vector/np.linalg.norm(vector)
                self.vec = normalized_vector

                if front_door == None:
                    front_door_corners = [[0,0],[0,1],[1,1],[0,0]]
                    front_door = Polygon(front_door_corners)
                else:
                    front_door_corners = list(front_door.exterior.coords)
                
                frondoor_center = front_door.centroid
                new_frontdoor = Polygon(get_boundbox(frondoor_center,normalized_vector,0.75))
                contest_cut = contest.difference(boundary)
                contest_cut = contest_cut.difference(new_frontdoor)
                boundary_cut = boundary.difference(new_frontdoor)
                if contest_cut.geom_type == 'MultiPolygon':
                    contest_cut = contest_cut.geoms[0]
                if boundary_cut.geom_type == 'MultiPolygon':
                    boundary_cut = boundary_cut.geoms[0]   

                boudnary_center = [boundary.centroid.x*6.4,boundary.centroid.y*6.4]
                move_x =  64 - boudnary_center[0]
                move_y =  64 - boudnary_center[1]
                self.front_door = np.array([int(frondoor_center.x*6.4 + move_x),int(frondoor_center.y*6.4 + move_y)])
                boundary_cut_coords = scale_to_img(6.4,move_x,move_y,boundary_cut)
                contest_cut_coords = scale_to_img(6.4,move_x,move_y,contest_cut)
                frontdoor_coords = scale_to_img(6.4,move_x,move_y,new_frontdoor)

                boundary_cut_coords[np.where(boundary_cut_coords>127)] = 127
                boundary_cut_coords[np.where(boundary_cut_coords<0)] = 0
                contest_cut_coords[np.where(contest_cut_coords>127)] = 127
                contest_cut_coords[np.where(contest_cut_coords<0)] = 0

                temp_boundAlpha = np.zeros((128,128))
                temp_boundrgb = np.zeros((128,128))

                temp_boundAlpha = cv2.fillPoly(temp_boundAlpha, contest_cut_coords.astype(np.int32), color=255)
                temp_boundAlpha = cv2.fillPoly(temp_boundAlpha, boundary_cut_coords.astype(np.int32), color=255)
                temp_boundrgb = cv2.fillPoly(temp_boundrgb, boundary_cut_coords.astype(np.int32), color=127)

                temp_boundAlpha = cv2.fillPoly(temp_boundAlpha, frontdoor_coords.astype(np.int32), color=255)
                temp_boundrgb = cv2.fillPoly(temp_boundrgb, frontdoor_coords.astype(np.int32), color=255)

                self.bound_img[:,:,3] = temp_boundAlpha
                for m in range(3):
                    self.bound_img[:,:,m] = temp_boundrgb
                file_img = 'parsed/boundary/%d.png' % (ind) #'parsed/boundary/%d_%s.jpg' % (ind, id_name)
                file_json = 'parsed/graph/%d.json' % (ind) #'parsed/graph/%d_%s.json' % (ind, id_name)

                # real-world data to json
                floorplan_to_Json(file_json,floorplan_house_polygon,types_names,house_centers,
                    tpyes_house,ada_list,house_areas,bound_all_corners,front_door_corners,windowsPt,doorsPt)
                cv2.imwrite(file_img, self.bound_img)

                self.reorder(move_x,move_y,tpyes_house,house_centers,boundx,boundy,
                    self.boundary_domainxy[0],self.boundary_domainxy[1],house_areas,ada_list,corners_house)
                
                loc_onehot, area_onehot = self.one_hot()

                return self.Tokenization(loc_onehot, area_onehot, move_x, move_y, frontdoor_coords, ind)
            
            else:

                return 0, 0, 0, 0, 0

    def reorder(self,Mx,My,T,C,boundx,boundy,bondxmin,bondymin,S,A,R):

        for k in range(len(T)):
            self.adjacency[k][k] = 1

        # Living Room First (Rplan/iPLAN used) T type C location S size A adjacency R region
        if 1 in T: # Living Room existing in layout
            ind_living = int(np.where(np.array(T) == 1)[0][0])
            self.type[0] = 1

            self.regions.append(scale_to_img(6.4,Mx,My,R[ind_living]))
            self.loc_img.append(scale_to_img(6.4,Mx,My,Polygon(get_boundbox(Point(C[ind_living]),self.vec,0.5))))
            self.areas[0] = S[ind_living]
            self.location[0] = location_normalize(C[ind_living],boundx,boundy,bondxmin,bondymin)
            ind = 1

            if ind_living != 0:
                A[np.where(A == ind_living)] = 100
                A[np.where(A < ind_living)] += 1
                A[np.where(A == 100)] = 0

            for n in A:
                self.adjacency[n[0]][n[1]] = 1
                self.adjacency[n[1]][n[0]] = 1

            # del T[ind_living]
            for i,j in enumerate(T):
                if j == 1:
                    continue
                else:
                    self.type[ind] = j
                    self.areas[ind] = S[i]
                    self.location[ind] = location_normalize(C[i],boundx,boundy,bondxmin,bondymin)
                    self.loc_img.append(scale_to_img(6.4,Mx,My,Polygon(get_boundbox(Point(C[i]),self.vec,0.5))))
                    self.regions.append(scale_to_img(6.4,Mx,My,R[i]))
                    ind += 1
        
        else: # no living room in layout

            for n in A:
                self.adjacency[n[0]][n[1]] = 1
                self.adjacency[n[1]][n[0]] = 1

            for i,j in enumerate(T):

                self.type[i] = j
                self.areas[i] = S[i]
                self.location[i] = location_normalize(C[i],boundx,boundy,bondxmin,bondymin)
                self.loc_img.append(scale_to_img(6.4,Mx,My,Polygon(get_boundbox(Point(C[i]),self.vec,0.5))))
                self.regions.append(scale_to_img(6.4,Mx,My,R[i]))

    def one_hot(self):

        loc_onehot = location_onehot(self.location,self.C_Dimen)
        area_onehot = size_onehot(self.areas,self.S_Dimen)

        return loc_onehot,area_onehot

    def Tokenization(self, L_onehot, S_onehot, Mx, My, frontdoor_coords, ind):

        type_token = np.insert(self.type,0,10,axis = 0) # start
        type_token = np.insert(type_token,15,0,axis = 0) # final

        loc_token = np.insert(L_onehot,0,np.array([self.C_Dimen-1]*2),axis = 0) # start
        loc_token = np.insert(loc_token,15,0,axis = 0) # final

        ada_token = np.insert(self.adjacency,0,np.ones((14)),axis = 0) # start
        ada_token = np.insert(ada_token,15,np.zeros((14)),axis = 0) # final

        area_token = np.insert(S_onehot,0,self.S_Dimen-1,axis = 0) # start
        area_token = np.insert(area_token,15,0,axis = 0) # final

        end_id = np.where(type_token==0)[0][0] # end
        type_token[end_id] = 9 
        loc_token[end_id] = np.array([self.C_Dimen-2]*2)
        ada_token[end_id] = np.array([0.5]*14)
        area_token[end_id] = self.S_Dimen-2

        img_data = np.ones((128, 128, 4),dtype=np.int32)
        outter_boundary = self.boundary.buffer(0.4,join_style=2)
        boundary_scaled_coords = scale_to_img(6.4, Mx, My, self.boundary)
        outter_boundary_scaled_coords = scale_to_img(6.4, Mx, My, outter_boundary)

        temp_boundAlpha = np.zeros((128,128))
        temp_boundrgb = np.zeros((128,128))

        temp_boundAlpha = cv2.fillPoly(temp_boundAlpha, outter_boundary_scaled_coords.astype(np.int32), color=127)
        temp_boundAlpha = cv2.fillPoly(temp_boundAlpha, frontdoor_coords.astype(np.int32), color=255)
        img_data[:,:,3] = temp_boundAlpha
        cv2.imwrite("parsed/location/0/%d.png" % (ind), img_data)
        cv2.imwrite("parsed/region/0/%d.png" % (ind), img_data)
        cv2.imwrite("parsed/location_all/%d.png" % (self.count), img_data)
        cv2.imwrite("parsed/region_all/%d.png" % (self.count), img_data)
        temp_boundAlpha = cv2.fillPoly(temp_boundAlpha, boundary_scaled_coords.astype(np.int32), color=0)
        temp_boundAlpha = cv2.fillPoly(temp_boundAlpha, frontdoor_coords.astype(np.int32), color=255)

        self.count += 1
        img_data[:,:,0:3] = 0
        img_data[:,:,3] = temp_boundAlpha
        temp_boundAlpha_main = temp_boundAlpha.copy()

        for m,n in enumerate(self.loc_img):
            temp_boundAlpha = temp_boundAlpha_main.copy()

            temp_boundrgb[:,:] = 0
            temp_boundrgb = cv2.fillPoly(temp_boundrgb, n.astype(np.int32), color=255)

            for k in range(3):
                img_data[:,:,k] = temp_boundrgb
            temp_boundAlpha = cv2.fillPoly(temp_boundAlpha, n.astype(np.int32), color=255)
            img_data[:,:,3] = temp_boundAlpha
            cv2.imwrite("parsed/location/%d/%d.png" % (m+1,ind), img_data)
            cv2.imwrite("parsed/location_all/%d.png" % (self.count), img_data)

            temp_boundrgb = cv2.fillPoly(temp_boundrgb, self.regions[m].astype(np.int32), color=255)
            for k in range(3):
                img_data[:,:,k] = temp_boundrgb
            temp_boundAlpha = cv2.fillPoly(temp_boundAlpha, self.regions[m].astype(np.int32), color=255)
            img_data[:,:,3] = temp_boundAlpha
            cv2.imwrite("parsed/region/%d/%d.png" % (m+1,ind), img_data)
            cv2.imwrite("parsed/region_all/%d.png" % (self.count), img_data)

            self.count += 1

        return 1, type_token, loc_token, ada_token, area_token

class Swiss_Dewelling_DataProcess3D():

    def __init__(self,house_room_types,house_type_index):

        self.house_room_types = house_room_types
        self.house_type_index = house_type_index
        self.T_list = [[255,255,255],[255,255,0],[0,255,255],[127,0,255],[255,0,255],[127,127,255],[255,0,127],[127,255,127],[255,127,127]]
        self.bound_img = np.zeros((128,128,4))
        self.type = np.zeros((12,13,14))
        self.location = np.zeros((12,13,14,2)) # one-hot with 32 steps in range boundary box
        self.adjacency = np.zeros((12,13,14,14))
        self.areas = np.zeros((12,13,14)) # one-hot with 40 steps in range 40
        self.loc_img = []
        self.regions = [] # save as img
    
    def reset(self):
        self.bound_img = np.zeros((128,128,4))
        self.type = np.zeros((12,13,14))
        self.location = np.zeros((12,13,14,2)) # one-hot with 32 steps in range boundary box
        self.adjacency = np.zeros((12,13,14,14))
        self.areas = np.zeros((12,13,14)) # one-hot with 40 steps in range 40
        self.loc_img = []
        self.regions = []
        self.front_door = None

    def transfer_polygons(self,tmp,ind,floor_id,apart_id):

        # real-world data
        corners_house,extended_house,tpyes_house,types_names,house_centers,house_areas,front_door,doorsPt,windowsPt\
            = parse_swiss_dewelling_polygon3D(tmp.index,tmp['geometry'],tmp['entity_subtype'],tmp['elevation'],tmp['height'],self.house_room_types,self.house_type_index)

        if tpyes_house != [] and len(tpyes_house) < 15:

            floorplan_house_polygon = MultiPolygon(corners_house)
            boundary = unary_union(floorplan_house_polygon.buffer(0.05,join_style=2))

            while boundary.geom_type == 'MultiPolygon':
                boundary = boundary.buffer(0.1,join_style=2)
            if list(boundary.interiors) != []:
                for inte in list(boundary.interiors):
                    boundary = unary_union(MultiPolygon([boundary,Polygon(inte).buffer(0.1,join_style=2)]))
            
            self.boundary_domainxy = boundary.bounds # (minx, miny, maxx, maxy)
            boundx = self.boundary_domainxy[2] - self.boundary_domainxy[0]
            boundy = self.boundary_domainxy[3] - self.boundary_domainxy[1]
            self.boundary = boundary

            if boundx <= 20 and boundy <= 20:
                self.corners_house = corners_house
                self.house_centers = house_centers

                ada_list = get_adjacency_graph(MultiPolygon(extended_house))
                boundary_corners = list(boundary.minimum_rotated_rectangle.exterior.coords)
                bound_all_corners = list(boundary.exterior.coords)
                boundary_pt = np.array(boundary_corners)[:-1]
                index_miny = np.where(boundary_pt[:,1] == np.min(boundary_pt[:,1]))[0][0]
                vector = boundary_pt[index_miny - 1] - boundary_pt[index_miny]
                normalized_vector = vector/np.linalg.norm(vector)
                self.vec = normalized_vector

                if front_door == None:
                    front_door_corners = [[0,0],[0,1],[1,1],[0,0]]
                    front_door = Polygon(front_door_corners)
                else:
                    front_door_corners = list(front_door.exterior.coords)
                
                frondoor_center = front_door.centroid
                new_frontdoor = Polygon(get_boundbox(frondoor_center,normalized_vector,0.75))
                boundary_cut = boundary.difference(new_frontdoor)
                if boundary_cut.geom_type == 'MultiPolygon':
                    boundary_cut = boundary_cut.geoms[0]   

                boudnary_center = [boundary.centroid.x*6.4,boundary.centroid.y*6.4]
                move_x =  64 - boudnary_center[0]
                move_y =  64 - boudnary_center[1]
                self.front_door = np.array([int(frondoor_center.x*6.4 + move_x),int(frondoor_center.y*6.4 + move_y)])
                frontdoor_coords = scale_to_img(6.4,move_x,move_y,new_frontdoor)

                file_json = "GT/building3D/%d/%d/%d.json" % (floor_id,apart_id,ind) #'parsed/graph/%d_%s.json' % (ind, id_name)

                # real-world data to json
                floorplan_to_Json(file_json,floorplan_house_polygon,types_names,house_centers,
                    tpyes_house,ada_list,house_areas,bound_all_corners,front_door_corners,windowsPt,doorsPt)

                self.reorder(move_x,move_y,tpyes_house,house_centers,boundx,boundy,
                    self.boundary_domainxy[0],self.boundary_domainxy[1],house_areas,ada_list,corners_house)
                
                loc_onehot, area_onehot = self.one_hot()

                return self.Tokenization(loc_onehot, area_onehot, move_x, move_y, frontdoor_coords, ind,floor_id,apart_id)
            
            else:

                return 0

    def reorder(self,Mx,My,T,C,boundx,boundy,bondxmin,bondymin,S,A,R):

        for k in range(len(T)):
            self.adjacency[k][k] = 1

        # Living Room First (Rplan/iPLAN used) T type C location S size A adjacency R region
        if 1 in T: # Living Room existing in layout
            ind_living = int(np.where(np.array(T) == 1)[0][0])
            self.type[0] = 1

            self.regions.append(scale_to_img(6.4,Mx,My,R[ind_living]))
            self.loc_img.append(scale_to_img(6.4,Mx,My,Polygon(get_boundbox(Point(C[ind_living]),self.vec,0.5))))
            self.areas[0] = S[ind_living]
            self.location[0] = location_normalize(C[ind_living],boundx,boundy,bondxmin,bondymin)
            ind = 1

            if ind_living != 0:
                A[np.where(A == ind_living)] = 100
                A[np.where(A < ind_living)] += 1
                A[np.where(A == 100)] = 0

            for n in A:
                self.adjacency[n[0]][n[1]] = 1
                self.adjacency[n[1]][n[0]] = 1

            # del T[ind_living]
            for i,j in enumerate(T):
                if j == 1:
                    continue
                else:
                    self.type[ind] = j
                    self.areas[ind] = S[i]
                    self.location[ind] = location_normalize(C[i],boundx,boundy,bondxmin,bondymin)
                    self.loc_img.append(scale_to_img(6.4,Mx,My,Polygon(get_boundbox(Point(C[i]),self.vec,0.5))))
                    self.regions.append(scale_to_img(6.4,Mx,My,R[i]))
                    ind += 1
        
        else: # no living room in layout

            for n in A:
                self.adjacency[n[0]][n[1]] = 1
                self.adjacency[n[1]][n[0]] = 1

            for i,j in enumerate(T):

                self.type[i] = j
                self.areas[i] = S[i]
                self.location[i] = location_normalize(C[i],boundx,boundy,bondxmin,bondymin)
                self.loc_img.append(scale_to_img(6.4,Mx,My,Polygon(get_boundbox(Point(C[i]),self.vec,0.5))))
                self.regions.append(scale_to_img(6.4,Mx,My,R[i]))

    def one_hot(self):

        loc_onehot = location_onehot(self.location,self.C_Dimen)
        area_onehot = size_onehot(self.areas,self.S_Dimen)

        return loc_onehot,area_onehot

    def Tokenization(self, L_onehot, S_onehot, Mx, My, frontdoor_coords, ind,floor_id,apart_id):

        img_data = np.zeros((128, 128, 4),dtype=np.int32)
        outter_boundary = self.boundary.buffer(0.4,join_style=2)
        boundary_scaled_coords = scale_to_img(6.4, Mx, My, self.boundary)
        outter_boundary_scaled_coords = scale_to_img(6.4, Mx, My, outter_boundary)

        temp_boundAlpha = np.zeros((128,128))
        temp_boundrgb0 = np.zeros((128,128))
        temp_boundrgb1 = np.zeros((128,128))
        temp_boundrgb2 = np.zeros((128,128))

        temp_boundAlpha = cv2.fillPoly(temp_boundAlpha, outter_boundary_scaled_coords.astype(np.int32), color=127)
        temp_boundAlpha = cv2.fillPoly(temp_boundAlpha, frontdoor_coords.astype(np.int32), color=255)
        temp_boundAlpha = cv2.fillPoly(temp_boundAlpha, boundary_scaled_coords.astype(np.int32), color=255)
        temp_boundAlpha = cv2.fillPoly(temp_boundAlpha, frontdoor_coords.astype(np.int32), color=255)

        img_data[:,:,3] = temp_boundAlpha
        # temp_boundAlpha_main = temp_boundAlpha.copy()

        # for m,n in enumerate(self.regions):
  
        #     temp_boundrgb0 = cv2.fillPoly(temp_boundrgb0,  n.astype(np.int32), color=self.T_list[self.type[m]][0])
        #     temp_boundrgb1 = cv2.fillPoly(temp_boundrgb1,  n.astype(np.int32), color=self.T_list[self.type[m]][1])
        #     temp_boundrgb2 = cv2.fillPoly(temp_boundrgb2,  n.astype(np.int32), color=self.T_list[self.type[m]][2])
        
        # img_data[:,:,0] = temp_boundrgb0
        # img_data[:,:,1] = temp_boundrgb1
        # img_data[:,:,2] = temp_boundrgb2

        # cv2.imwrite("GT/building3D/%d/%d/%d.png" % (floor_id,apart_id,ind), img_data)

        return 1