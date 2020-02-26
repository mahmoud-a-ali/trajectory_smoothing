import numpy as np
from sympy import diff, Symbol

from piecewise_function import PiecewiseFunction
from parameterize_path import parameterize_path
import  traj
from sympy import Matrix
def reverse_list( lst ):
    arr = np.array( lst )
    arr = np.rot90(arr).tolist()
    arr.reverse()
    return arr

def form_seg_jt_2_jt_seg(lst):
    #n_segs  = len( lst )
    #n_jts   = len( lst[0] )
    #n_phs   = len( lst[0][0] ) 
    arr = np.array(lst)
    arr = np.rot90(arr)
    lst = np.reshape(arr,   ( len( lst[0] ), len(lst), len(lst[0][0]) )   ).tolist()
    lst.reverse()   
    return lst    
    
def project_limits_onto_s(limits, function):
    #print "function: {}".format( function )    
    #print "limits: {}".format( limits )    
    slope = np.abs(np.array(diff(function)).astype(np.float64).flatten())
    #print "slope: {}".format( slope )    
    limit_factor = limits / slope
    #return min(limit_factor)
    return limit_factor.tolist()


def trajectory_for_path(path, v_start, v_end, max_velocities, max_accelerations, max_jerks):       
    path_function = parameterize_path(path)
    t = Symbol('t')
    s = path_function.independent_variable    

    n_segs = len(path_function.functions)
    n_wpts = n_segs +1
    n_jts  = len(v_start)
    
    
############################ FW VEL ######################   
    s_fw_vel = []  
    for seg in range(n_segs):
        fsegment = path_function.functions[seg]
        s0 = path_function.boundaries[seg]
        s1 = path_function.boundaries[seg + 1]
        
        # Project joint limits onto this segment's direction to get limits on s
        v_max = project_limits_onto_s(max_velocities, fsegment)
        a_max = project_limits_onto_s(max_accelerations, fsegment)
        j_max = project_limits_onto_s(max_jerks, fsegment)

        if seg == 0:
            s_v_start = project_limits_onto_s(v_start, fsegment)
            s_fw_vel.append( s_v_start)
            
        s_nxt_vel = []
        for jt in range(n_jts):
            tj, ta, tv, s_v_nxt = traj.max_reachable_vel( s1-s0, s_fw_vel[seg][jt], 30.0, v_max[jt], a_max[jt], j_max[jt])
            s_nxt_vel.append( s_v_nxt )   
        s_fw_vel.append( s_nxt_vel )
    print "\n>>> s_fw_vel: \n {} \n\n".format( s_fw_vel)
 
   
   
   
   
############################ BK VEL ######################   
    s_bk_vel = []
    for seg in range(n_segs):
        fsegment = path_function.functions[n_segs - seg -1 ]
        s0 = path_function.boundaries[n_segs - seg - 1]
        s1 = path_function.boundaries[n_segs - seg ]
        
        # Project joint limits onto this segment's direction to get limits on s
        v_max = project_limits_onto_s(max_velocities, fsegment)
        a_max = project_limits_onto_s(max_accelerations, fsegment)
        j_max = project_limits_onto_s(max_jerks, fsegment)
    
        if seg == 0:
            s_v_end = project_limits_onto_s(v_end, fsegment)
            s_bk_vel.append( s_v_end)

        s_nxt_vel = []
        for jt in range(n_jts):
            tj, ta, tv, s_v_nxt = traj.max_reachable_vel( s1-s0, s_bk_vel[seg][jt], 30.0, v_max[jt], a_max[jt], j_max[jt])
            s_nxt_vel.append( s_v_nxt )   
        s_bk_vel.append( s_nxt_vel )
 
    s_bk_vel.reverse()
    print "\n>>> s_bk_vel: \n {}".format( s_bk_vel)
    



   
############################ estimated VEL ######################   
    ##check condition when v_start or v_end is not feasible: v_start > max_v_start calculated using the backward loop or Vs
    for jt in range(n_jts):
        if s_fw_vel[0][jt] > s_bk_vel[0][jt] or s_bk_vel[-1][jt] > s_fw_vel[-1][jt] :
            raise ValueError("combination of v_start({}) & v_end({}) for jt_{}is not feasible".format(s_fw_vel[0][jt], s_bk_vel[-1][jt], jt ) )                 
    # calcuate max_rechable_vels that grantee v_end at the end of the trajectory for this portion of traj
    s_estimated_vel = []
    for wpt in range(n_wpts):
        s_seg_vel= [ min(v) for v in zip( s_fw_vel[wpt], s_bk_vel[wpt])]
        s_estimated_vel.append( s_seg_vel  )
    print "\n>>> s_estimated_vel: \n {}".format( s_estimated_vel)
    
  
############################ parameterize using estimated VEL ######################      
    traj_pos_seg_jt = []
    traj_vel_seg_jt = []
    traj_acc_seg_jt = []
    traj_jrk_seg_jt = []
    traj_times_seg_jt = []     
    traj_times_seg_jt.append( [0.0 for seg in range(n_segs)]  )
    
    trajectory_boundaries= [0.0]
    for segment_i in range(len(path_function.functions)):
        fsegment = path_function.functions[segment_i]

        s0 = path_function.boundaries[segment_i]
        s1 = path_function.boundaries[segment_i + 1]

        # Project joint limits onto this segment's direction to get limits on s
        v_max = project_limits_onto_s(max_velocities, fsegment)
        a_max = project_limits_onto_s(max_accelerations, fsegment)
        j_max = project_limits_onto_s(max_jerks, fsegment)
        

        # Compute 7 segment profile for s as a function of time.
        this_segment_start_time = trajectory_boundaries[-1]
        

        s_pos_jt=[]
        for jt in range(n_jts):
            print "\n>> seg_{}: jt={}".format(segment_i, jt)
            print "pos_dif={}, v0={}, v1={}".format( s1-s0, s_estimated_vel[segment_i][jt], s_estimated_vel[segment_i+1][jt])
            s_pos, s_vel, s_acc, s_jrk  = traj.fit_traj_segment(0, s1-s0, s_estimated_vel[segment_i][jt], s_estimated_vel[segment_i+1][jt], 30.0, v_max[jt], a_max[jt], j_max[jt], t)
            s_pos_jt.append( s_pos )            
#            print "\n>>> s_pos: {}".format( s_pos )

#            print "\n>>> n_functions: {}".format( len(s_position.functions) )
#            print "\n>>> s_position: {}".format(s_position.functions)
#            print "\n>>> s_velocity: {}".format( s_velocity.functions)
#            print "\n>>> s_acceleration: {}".format(s_acceleration.functions)
#            print "\n>>> s_jerk: {}".format( s_jerk.functions)
  
        
        for function_i in range(len(s_pos_jt[0].functions)):
            pos_vs_t = []
            for jt in range(n_jts):
                position_vs_t = fsegment.subs(s, s_pos_jt[jt].functions[function_i])
#                print "\n>>> position_vs_t: {}".format( position_vs_t )
                pos_vs_t.append( position_vs_t[jt] )                
            pos_vs_t = Matrix(pos_vs_t)
#            print "\n>>> pos_vs_t: {}".format( pos_vs_t )
#                
            vel_vs_t = diff(pos_vs_t, t)
            acc_vs_t = diff(vel_vs_t, t)
            jrk_vs_t = diff(acc_vs_t, t)
            
           

      
                
            traj_pos_seg_jt.append( pos_vs_t ) 
            traj_vel_seg_jt.append( vel_vs_t ) 
            traj_acc_seg_jt.append( acc_vs_t ) 
            traj_jrk_seg_jt.append( jrk_vs_t ) 
            #### are not synch in time, which time you can choose 
            trajectory_boundaries.append(s_pos_jt[0].boundaries[function_i + 1] + this_segment_start_time ) 
            
    print "\n traj_jrk_seg_jt[jt]={}".format( traj_jrk_seg_jt[0]   )


    return (PiecewiseFunction(trajectory_boundaries, traj_pos_seg_jt, t),
            PiecewiseFunction(trajectory_boundaries, traj_vel_seg_jt, t),
            PiecewiseFunction(trajectory_boundaries, traj_acc_seg_jt, t),
            PiecewiseFunction(trajectory_boundaries, traj_jrk_seg_jt, t))

