#!/usr/bin/env python
"""
Simple example that parametrizes a 2d joint-space path.
"""
import actionlib
from control_msgs.msg import FollowJointTrajectoryAction, FollowJointTrajectoryGoal
from trajectory_msgs.msg import JointTrajectoryPoint
from matplotlib import pyplot as plt
import numpy as np
import rospy
from sensor_msgs.msg import JointState

import traj


def create_joint_trajectory_goal(piecewise_position_function, piecewise_velocity_function,
                                 piecewise_acceleration_function, joint_names, sample_period=0.008):
    print ">>>> create_joint_trajectory_goal"
    # Non-zero start times won't make sense to the controller
    assert piecewise_position_function.boundaries[0] == 0.0
    goal = FollowJointTrajectoryGoal()
    goal.trajectory.header.stamp = rospy.Time.now()
    goal.trajectory.header.frame_id = 'base_link'
    goal.trajectory.joint_names = joint_names

    for t in np.arange(0.0, piecewise_position_function.boundaries[-1], sample_period):
        point = JointTrajectoryPoint()
        point.time_from_start = rospy.Duration(t)
        point.positions = list(piecewise_position_function(t))
        point.velocities = list(piecewise_velocity_function(t))
        point.accelerations = list(piecewise_acceleration_function(t))
        goal.trajectory.points.append(point)
    print point.positions
    print point.velocities
    print point.accelerations
    
    return goal


def joint_state_callback(joint_state_msg):
    global initial_joint_states
    initial_joint_states = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]












initial_joint_states = None

# Joint limits for a fictional 6DoF arm.

max_velocities = np.deg2rad(np.array([
    3.0,
    6.0,
]))

max_accelerations = np.deg2rad(np.array([
    4.0,
    8.0,

]))

max_jerks = np.deg2rad(np.array([
    10.0,
    20.0,
 
]))



max_positions =[  30.0,    30.0,]
max_velocities =[  3.0,    3.0,]
max_accelerations = [  4.0,    4.0,]
max_jerks = [  6.0,    6.0,]










joint_names = ['joint_1', 'joint_2']

rospy.init_node('traj_demo')
plot_trajectory = rospy.get_param('~plot', True)



# Simple path
path = np.array([ (0.0, 0.7), (0.5, 1.0) ,   (0.8, 1.8)])
v_start= [.1, 0.2]
v_end = [ 0.2, 0.1]

path = np.array([ (0.0, 0.0), (1.0, 0.0) ,   (1.7, 0.0)]) 
v_start= [ 0.0, 0.1]
v_end  = [ 0.2, 0.0]
 
 
path = np.array([ (0.0, 0.0), (1.0, .50) ,   (1.5, 1.8), (1.9, 1.0)]) 

#path = np.array([ (0.0, 0.0), (1.0, 1.0) ,   (1.3, 1.3), (1.9, 1.9)]) 
#path = np.array([ (0.0, 0.0), (1.0, 1.50) ])# ,   (1.3, 1.3), (1.9, 1.9)]) 

v_start= [ 0.0, 0.0]
v_end  = [ 0.0, 0.0]
 
path = np.array([ (1.0, 1.0), (2.0, 2.0) , (3.5, 3.8) ] ) 
v_start= [ 0.0, 0.0]
v_end  = [ 0.2, 0.1]

n_jts = len( v_start)
 
 
#####################  v1: test n-dof : to find max reachable  #######################
rot_path = np.rot90(path).tolist()
rot_path.reverse()

estimated_vel = traj.find_max_estimated_vel_per_ndof_path(rot_path, v_start, v_end, max_positions[0], max_velocities[0], max_accelerations[0], max_jerks[0])
print "max_estimated_vel: {}".format( estimated_vel )

fig = plt.figure()
for jt in range(n_jts): 
    plt.plot( estimated_vel[jt],  label='max_ve_jt_{}'.format(jt))
    plt.plot( estimated_vel[jt], 'o')

plt.xlabel("waypoints")
plt.ylabel("velocity")
plt.legend()
plt.grid()
plt.show()

estimated_vel= np.rot90(estimated_vel).tolist()
estimated_vel.reverse()
print "estimated_vel_seg_jt: {}".format( estimated_vel )


(trajectory_position_function, trajectory_velocity_function, trajectory_acceleration_function,
 trajectory_jerk_function) = traj.trajectory_for_path_v1(path, estimated_vel, max_positions,  max_velocities, max_accelerations, max_jerks)


print "\n\n>>> trajectory_jerk_function: \n{}".format(trajectory_jerk_function[0].functions )

if plot_trajectory:
    for jt in range(n_jts): 
        plt.figure()
        traj.plot.plot_trajectory(plt, trajectory_position_function[jt], trajectory_velocity_function[jt],
                              trajectory_acceleration_function[jt], trajectory_jerk_function[jt])

    plt.show()    
    
    
    plt.figure()
    traj.plot.plot_2d_path(plt.gca(), trajectory_position_function, 100, label='trajectory points')
    # Plot the waypoints in the original path for comparison.
    plt.plot([q[0] for q in path], [q[1] for q in path], 'bx', label='original waypoints')

    plt.show()















