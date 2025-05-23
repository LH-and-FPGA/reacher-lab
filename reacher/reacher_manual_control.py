from reacher import reacher_kinematics
from reacher import reacher_robot_utils
from reacher import reacher_sim_utils
import pybullet as p
import time
import numpy as np
from absl import app
from absl import flags
from pupper_hardware_interface import interface
from sys import platform

flags.DEFINE_bool("run_on_robot", False,
                  "Whether to run on robot or in simulation.")
flags.DEFINE_bool("ik", False, "Whether to control arms through cartesian coordinates(IK) or joint angles")
FLAGS = flags.FLAGS

KP = 20.0  # Amps/rad
KD = 1.50  # Amps/(rad/s)
MAX_CURRENT = 3.0  # Amps

UPDATE_DT = 0.01  # seconds

HIP_OFFSET = 0.0335  # meters
L1 = 0.08  # meters
L2 = 0.11  # meters


def main(argv):
  run_on_robot = FLAGS.run_on_robot
  reacher = reacher_sim_utils.load_reacher()
  sphere_id = reacher_sim_utils.create_debug_sphere()

  joint_ids = reacher_sim_utils.get_joint_ids(reacher)
  param_ids = reacher_sim_utils.get_param_ids(reacher)
  reacher_sim_utils.zero_damping(reacher)

  p.setPhysicsEngineParameter(numSolverIterations=10)

  if run_on_robot:
    # serial_port = reacher_robot_utils.get_serial_port()
    serial_port = 'COM3'
    hardware_interface = interface.Interface(serial_port)
    time.sleep(0.25)
    hardware_interface.set_joint_space_parameters(kp=KP,
                                                  kd=KD,
                                                  max_current=MAX_CURRENT)

  p.setRealTimeSimulation(1)
  counter = 0
  last_command = time.time()
  enable = True
  joint_angles = np.zeros(6)

  # Use this function to disable/enable certain motors. The first six elements
  # determine activation of the motors attached to the front of the PCB, which
  # are not used in this lab. The last six elements correspond to the activations
  # of the motors attached to the back of the PCB, which you are using.
  # The 7th element will correspond to the motor with ID=1, 8th element ID=2, etc
  # hardware_interface.send_dict({"activations": [0, 0, 0, 0, 0, 0, x, x, x, x, x, x]})

  while (1):
    if run_on_robot:
      hardware_interface.read_incoming_data()

    if time.time() - last_command > UPDATE_DT:
      last_command = time.time()
      counter += 1

      slider_angles = np.zeros_like(joint_angles)
      for i in range(len(param_ids)):
        c = param_ids[i]
        targetPos = p.readUserDebugParameter(c)
        slider_angles[i] = targetPos

      # If IK is enabled, update joint angles based off of goal XYZ position
      if FLAGS.ik:
          xyz = []
          for i in range(len(param_ids), len(param_ids) + 3):
            xyz.append(p.readUserDebugParameter(i))
          xyz = np.asarray(xyz)
          ret = reacher_kinematics.calculate_inverse_kinematics(xyz, joint_angles[:3])
          if ret is None:
            enable = False
          else:
            # Wraps angles between -pi, pi
            joint_angles[:3] = np.arctan2(np.sin(ret), np.cos(ret))
            joint_angles[3:] = slider_angles[3:]
            enable = True
      else:
        joint_angles = slider_angles

      for i in range(len(joint_ids)):
        p.setJointMotorControl2(reacher,
                                joint_ids[i],
                                p.POSITION_CONTROL,
                                joint_angles[i],
                                force=2.)

      if run_on_robot and enable:
        full_actions = np.zeros([3, 4])
        # TODO: Update order & signs for your own robot/motor configuration like below
        # left_angles = [-joint_angles[1], -joint_angles[0], joint_angles[2]]
        # right_angles = [-joint_angles[5], joint_angles[4], -joint_angles[3]]
        left_angles = joint_angles[:3]
        left_angles[2] = -left_angles[2]
        right_angles = joint_angles[3:]
        # full_actions[:, 3] = left_angles
        full_actions[:, 0] = left_angles
        # full_actions[:, 2] = right_angles
        full_actions[:, 1] = right_angles
        # 对于joint angles, 0是底下的，1是中间的，2是上面的
        # 对于full actions来说第0列是left_leg的，第一行是底下的，第二行是中间的，第三行是上面的

        hardware_interface.set_actuator_postions(full_actions)
        # Actuator positions are stored in array: hardware_interface.robot_state.position,
        # Actuator velocities are stored in array: hardware_interface.robot_state.velocity

      end_effector_pos = reacher_kinematics.calculate_forward_kinematics_robot(joint_angles[:3])
      p.resetBasePositionAndOrientation(sphere_id,
                                        posObj=end_effector_pos,
                                        ornObj=[0, 0, 0, 1])

      if counter % 20 == 0:
        print("Joint angles:", joint_angles, "Position:", end_effector_pos)

app.run(main)
