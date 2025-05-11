import time
import numpy as np
from pupper_hardware_interface.interface import Interface

def generate_test_state():
    # 生成测试数据：标量 + 12 轴数据 + mode
    return {
        "yaw": 1.23,
        "pitch": -0.45,
        "roll": 0.67,
        "yaw_rate": 0.01,
        "pitch_rate": -0.02,
        "roll_rate": 0.03,
        "pos": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        "vel": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2],
        "cur": [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6],
        "pref": [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3],
        # "vref": np.linspace(0.4, 4.5, 12).tolist(),
        # "cref": np.linspace(0.5, 5.6, 12).tolist(),
        # "lcur": np.linspace(0.6, 6.7, 12).tolist(),
        # mode 用数字或字符串均可，下位机期待字符串类型
        "mode": 3
    }

if __name__ == "__main__":
    # 根据实际串口修改 port
    iface = Interface(port="COM3", baudrate=500000)

    try:
        while True:
            test_dict = generate_test_state()
            print("Sending test state:", test_dict)
            iface.send_dict(test_dict)
            time.sleep(2.0)
    except KeyboardInterrupt:
        print("测试结束")
