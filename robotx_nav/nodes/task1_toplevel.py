#!/usr/bin/env python

""" task 1:
    -----------------
    Created by Ren Ye @ 2016-11-06
    Authors: Ren Ye, Reinaldo
    -----------------

    <put the descriptions from robotx.org pdf file>

    <put the algorithms in natural language, can use bullet points, best is to use markdown format>

    <if you have plan b, can put it here>

    ## example ##
    + Go to start point
    + Rotate in position to detect red_1 and green_1 buoys
    + Plot perpendicular waypoints wrt to position of red and green buoys
    + Move towards waypoints move_base_forward
    + meanwhile requesting positions of red_2 and green_2
    + 	shutdown move_base_forward, create new move_base_forward towards mid of red_2 and green_2

    <change log put here>
    ### @ 2016-11-06 ###
    + create template

    renye's approach:
    1. drive to gps waypoint
    2. slowly in place rotate # noneed
    3. detect red and green totems by any camera
    4. rotate to bow to red and green totems
    5. roi of red in bow/left and roi of green in bow/right, calculate center
    6. drive until roi vanishes from both bow cameras, detect totem from port and starboard
    7. see new roi from bow
    8. drive with 5 and 6


"""

import rospy
import numpy
from geometry_msgs.msg import Point
from move_base_util import MoveBaseUtil
from move_base_waypoint_geo import MoveToGeo
from move_base_waypoint import MoveTo
from move_base_forward import Forward
from roi_coordinate import RoiCoordinate

class Task1(object):
    bow_left_red_x = float("Inf")
    bow_right_red_x = float("Inf")
    port_red_x = float("Inf")
    starboard_red_x = float("Inf")
    transom_red_x = float("Inf")
    bow_left_green_x = float("Inf")
    bow_right_green_x = float("Inf")
    port_green_x = float("Inf")
    starboard_green_x = float("Inf")
    transom_green_x = float("Inf")
    red_x_list = list()
    red_y_list = list()
    green_x_list = list()
    green_y_list = list()

    def subscribe_coordinate(self, topic_name, colorname):
        rospy.Subscriber(topic_name, Point, self.roi_coordinate_callback, colorname, queue_size=10)

    def __init__(self):
        # 0. parameters
        self.tart_lat = rospy.get_param("~lat", 1.34)
        self.tart_lon = rospy.get_param("~lon", 103.56)
        self.tart_heading = rospy.get_param("~heading", 1.57)  # north

        # 1. drive to gps waypoint
        # move_to_geo = MoveToGeo("gps_waypoint", self.start_lat, self.start_lon, self.start_heading)

        # 2. roi detect color totem, assume already have in launch
        #    then listen to namespace/objectname/colorname/coordinates
        rospy.init_node("roi_coordinate")
        self.subscribe_coordinate("bow/left/totem/red")
        self.subscribe_coordinate("bow/right/totem/red")
        self.subscribe_coordinate("port/totem/red")
        self.subscribe_coordinate("starboard/totem/red")
        self.subscribe_coordinate("transom/totem/red")
        self.subscribe_coordinate("bow/left/totem/green")
        self.subscribe_coordinate("bow/right/totem/green")
        self.subscribe_coordinate("port/totem/green")
        self.subscribe_coordinate("starboard/totem/green")
        self.subscribe_coordinate("transom/totem/green")

        # 3. calculate the center point bewtween red and green totem
        # the simplest way: median for (x_red, y_red) and median for (x_green, y_green)
        # then take the centerpoint for constant heading
        # the hard way: collect red and green points and use svm to get the separation plane
        # use the plane for constant heading
        rate = rospy.Rate(10)
        duration = 10
        rate.sleep()
        start_time = rospy.get_time()
        current_time = start_time
        while current_time - start_time < duration:
            self.red_x_list.extend([self.bow_left_red_x, self.bow_right_red_x,
                                   self.port_red_x, self.starboard_red_x, self.transom_red_x])
            self.red_y_list.extend([self.bow_left_red_x, self.bow_right_red_x,
                                   self.port_red_x, self.starboard_red_x, self.transom_red_x])
            self.green_x_list.extend([self.bow_left_green_x, self.bow_right_green_x,
                                   self.port_green_x, self.starboard_green_x, self.transom_green_x])
            self.green_y_list.extend([self.bow_left_green_x, self.bow_right_green_x,
                                   self.port_green_x, self.starboard_green_x, self.transom_green_x])
            rospy.spinOnce()

        else:
            red_x_center, red_y_center = numpy.median(self.red_x_list), numpy.median(self.red_y_list)
            green_x_center, green_y_center = numpy.median(self.green_x_list), numpy.median(self.green_y_list)
            print red_x_center, red_y_center, green_x_center, green_y_center

        # 4. constant heading based on roi, all coordinates are map. not relative
        target = [(red_x_center + green_x_center) / 2.0, (red_y_center + green_y_center) / 2.0, 0]
        # constant_heading = Forward("constant_heading", target=target, waypoint_separation=5, is_relative=False)

    def roi_coordinate_callback(self, msg):
        if colorname == "red":
            self.red_x_list.extend(msg.x)
            self.red_y_list.extend(msg.y)
        elif colorname == "green":
            self.green_x_list.extend(msg.x)
            self.green_y_list.extend(msg.y)

    def bow_left_red_callback(self, msg):
        self.x = msg.x
        self.y = msg.y

    def bow_right_red_callback(self, msg):
        self.bow_right_red_x = msg.x
        self.bow_right_red_y = msg.y

    def port_red_callback(self, msg):
        self.port_red_x = msg.x
        self.port_red_y = msg.y

    def starboard_red_callback(self, msg):
        self.starboard_red_x = msg.x
        self.starboard_red_y = msg.y

    def transom_red_callback(self, msg):
        self.transom_red_x = msg.x
        self.transom_red_y = msg.y

    def bow_left_green_callback(self, msg):
        self.bow_left_green_x = msg.x
        self.bow_left_green_y = msg.y

    def bow_right_green_callback(self, msg):
        self.bow_right_green_x = msg.x
        self.bow_right_green_y = msg.y

    def port_green_callback(self, msg):
        self.port_green_x = msg.x
        self.port_green_y = msg.y

    def starboard_green_callback(self, msg):
        self.starboard_green_x = msg.x
        self.starboard_green_y = msg.y

    def transom_green_callback(self, msg):
        self.transom_green_x = msg.x
        self.transom_green_y = msg.y



if __name__ == '__main__':
    try:
        Task1()

    except rospy.ROSInterruptException:
        rospy.loginfo("Navigation test finished.")
