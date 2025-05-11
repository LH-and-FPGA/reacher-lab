import unittest
import msgpack
import numpy as np

# 假序列化串口，用于捕获和注入数据
class FakeSerial:
    def __init__(self):
        self.written = b''
        self.to_read = b''
        self.timeout = 0
    def write(self, data):
        self.written += data
    def read(self, n):
        if not self.to_read:
            return b''
        chunk = self.to_read[:n]
        self.to_read = self.to_read[n:]
        return chunk

# 在创建 Interface 前，先 monkey-patch serial.Serial
from pupper_hardware_interface.interface import Interface
import serial

def make_interface(fake_serial, start_byte=0x00):
    serial.Serial = lambda *args, **kwargs: fake_serial
    iface = Interface(port='COM_TEST', start_byte=start_byte)
    # 同步 reader 起始字节
    iface.reader.start_byte = start_byte
    iface.reader.start_byte2 = start_byte
    return iface

class TestInterface(unittest.TestCase):
    def setUp(self):
        self.fake = FakeSerial()
        self.iface = make_interface(self.fake, start_byte=0x00)

    def assert_msgpack(self, buf, key, expected):
        # 帧头前两个字节后为 payload
        payload = buf[2:]
        data = msgpack.unpackb(payload)
        self.assertIn(key, data)
        self.assertEqual(data[key], expected)

    def test_set_joint_space_parameters(self):
        self.iface.set_joint_space_parameters(1.1, 2.2, 3.3)
        buf = self.fake.written
        self.assertEqual(buf[0], 0x00)
        self.assertEqual(buf[1], len(buf)-2)
        unpacked = msgpack.unpackb(buf[2:])
        self.assertAlmostEqual(unpacked['kp'], 1.1, places=5)
        self.assertAlmostEqual(unpacked['kd'], 2.2, places=5)
        self.assertAlmostEqual(unpacked['max_current'], 3.3, places=5)

    def test_set_cartesian_parameters(self):
        self.fake.written = b''
        self.iface.set_cartesian_parameters([4,5,6], [7,8,9], 0.5)
        unpacked = msgpack.unpackb(self.fake.written[2:])
        self.assertEqual(unpacked['cart_kp'], [4,5,6])
        self.assertEqual(unpacked['cart_kd'], [7,8,9])
        self.assertAlmostEqual(unpacked['max_current'], 0.5, places=5)

    def test_activate_deactivate(self):
        self.fake.written = b''
        self.iface.activate()
        unpacked = msgpack.unpackb(self.fake.written[2:])
        self.assertEqual(unpacked['activations'], [1]*12)

        self.fake.written = b''
        self.iface.deactivate()
        unpacked = msgpack.unpackb(self.fake.written[2:])
        self.assertTrue(unpacked['idle'])
        self.assertEqual(unpacked['activations'], [0]*12)

    def test_set_activations(self):
        pattern = [0,1]*6
        self.fake.written = b''
        self.iface.set_activations(pattern)
        unpacked = msgpack.unpackb(self.fake.written[2:])
        self.assertEqual(unpacked['activations'], pattern)

    def test_zero_home(self):
        self.fake.written = b''
        self.iface.zero_motors()
        self.assertTrue(msgpack.unpackb(self.fake.written[2:])['zero'])

        self.fake.written = b''
        self.iface.home_motors()
        self.assertTrue(msgpack.unpackb(self.fake.written[2:])['home'])

    def test_set_actuator_positions(self):
        mat = np.arange(12).reshape((3,4))
        self.fake.written = b''
        self.iface.set_actuator_postions(mat)
        unpacked = msgpack.unpackb(self.fake.written[2:])
        self.assertEqual(unpacked['pos'], mat.flatten('F').tolist())

    def test_set_cartesian_positions(self):
        mat = np.arange(12).reshape((3,4)) + 0.5
        self.fake.written = b''
        self.iface.set_cartesian_positions(mat)
        unpacked = msgpack.unpackb(self.fake.written[2:])
        self.assertEqual(unpacked['cart_pos'], mat.flatten('F').tolist())

    def test_read_incoming_data(self):
        # 构造一个完整的 robot state
        state = {
            'yaw': 1.2, 'pitch': 2.3, 'roll': 3.4,
            'yaw_rate': 0.1, 'pitch_rate': 0.2, 'roll_rate': 0.3,
            'pos': list(range(12)),
            'vel': [i*0.1 for i in range(12)],
            'cur': [i*0.2 for i in range(12)],
            'pref': [0]*12, 'vref': [0]*12, 'cref': [0]*12, 'lcur': [0]*12,
            'mode': 3
        }
        payload = msgpack.packb(state)
        packet = bytes([0x00, len(payload)]) + payload
        self.fake.to_read = packet

        result = self.iface.read_incoming_data()
        rs = self.iface.robot_state
        self.assertEqual(rs.yaw, state['yaw'])
        self.assertEqual(rs.mode, 'position_control')
        self.assertEqual(rs.position, state['pos'])

if __name__ == '__main__':
    unittest.main()
