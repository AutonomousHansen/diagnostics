#! /usr/bin/python
# Copyright (c) 2009, Willow Garage, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Willow Garage, Inc. nor the names of its
#       contributors may be used to endorse or promote products derived from
#       this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# This script brings up an effort controller runs a 500x life test on the 
# head tilt joint, pan joint and laser tilt joint.  
#
# Author: Kevin Watts

##@package impact_test
#
# @mainpage
# @htmlinclude manifest.xml
#
# @section usage Usage
# @verbatim $ run_test.launch @endverbatim
#
# @par Description
# @verbatim
# This program runs a impact life test on the head tilt, pan and laser tilt. 500 cycles, with effort safety removed.
# @endverbatim
 


CONTROLLER_NAMES = ["head_tilt_effort", "head_pan_effort", "laser_tilt_effort"]
JOINT_NAMES = ["head_tilt_joint", "head_pan_joint", "laser_tilt_mount_joint"]

import sys

import rostools
#<<<<<<< .mine
rostools.update_path('impact_test') # Rename to path head_impact_test
#=======
#rostools.load_manifest('impact_test') # Rename to head_impact_test
#>>>>>>> .r10290
import rospy
from std_msgs.msg import *
from mechanism_control import mechanism
from robot_srvs.srv import SpawnController, KillController
from time import sleep

## Create XML code for controller on the fly
def xml_for(controller, joint):
    return  '''\
<controller name=\"%s\" type=\"JointEffortControllerNode\">\
<joint name=\"%s\" />\
</controller>''' % (controller, joint) 

def main():
    rospy.init_node('impact_head_test', anonymous=True)
    for i in range(0,3): 
        joint = JOINT_NAMES[i]
        controller = CONTROLLER_NAMES[i]
        print xml_for(controller,joint)

        rospy.wait_for_service('spawn_controller')
        spawn_controller = rospy.ServiceProxy('spawn_controller', SpawnController)
        kill_controller = rospy.ServiceProxy('kill_controller', KillController)
    
        resp = spawn_controller(xml_for(controller, joint))
        if len(resp.ok) < 1 or not ord(resp.ok[0]):
            print "Failed to spawn effort controller"
        else:
            print "Spawned controller %s successfully" % controller

            pub = rospy.Publisher("/%s/set_command" % controller, Float64)

            try:
                for i in range(0,3):
                    if rospy.is_shutdown():
                        break
                    # Back and forth
                    sleep(1.5)
                    effort = -1000; # Min effort
                    pub.publish(Float64(effort))
                    sleep(1.5)
                    effort = 1000; # Max effort
                    pub.publish(Float64(effort))
            finally:
                kill_controller(controller)
                sleep(5)

    
if __name__ == '__main__':
    main()



