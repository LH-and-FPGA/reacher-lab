import time
from pupper_hardware_interface.interface import Interface

# 串口配置，按实际情况修改
PORT      = 'COM3'
BAUDRATE  = 500000
START_BYTE= 0x00

# 初始化
iface = Interface(port=PORT, baudrate=BAUDRATE, start_byte=START_BYTE)

# 要发送给下位机的数据（示例）
payload = {
    'kp': 100.01,
    'kd': 8080.0,
    'max_current': 7.89,
    'idle': True
}

# 发送并等待
while True:
    iface.send_dict(payload)
    # iface.activate()  # 发送完毕后，关闭下位机
    iface.set_joint_space_parameters(12.0, 2.0, 3.0)

    print("已发送")

    time.sleep(2.0)  # 等待 2 秒

# 可选：发送之后再读一次下位机返回
resp = iface.read_incoming_data()
print("2秒后收到的数据：", resp)
