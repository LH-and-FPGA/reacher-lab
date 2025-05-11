# test_send.py

import time
from pupper_hardware_interface import interface

def main():
    # 根据实际端口改成你的串口号
    port = 'COM3'      # Linux 下通常是 /dev/ttyUSBx，Windows 下可能是 'COM3'
    baudrate = 500000

    # 初始化 Interface：连接串口并设置初始参数
    iface = interface.Interface(port=port, baudrate=baudrate)

    try:
        while True:
            # 这里以发送一个 joint-space 参数更新为例
            # 你也可以改成 send_dict 或者其他命令
            kp = 14.0
            kd = 2.0
            max_current = 2.0
            iface.set_joint_space_parameters(kp, kd, max_current)

            print(f"[{time.strftime('%H:%M:%S')}] Sent kp={kp}, kd={kd}, max_current={max_current}")

            # 等待 5 秒
            time.sleep(2)

    except KeyboardInterrupt:
        print("测试结束，退出。")

if __name__ == '__main__':
    main()
