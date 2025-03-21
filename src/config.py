RED_RATIO: float = 1/3
DEFAULT_LISTENING_PORT: int = 9999
DEFAULT_LISTENING_IP: str = '0.0.0.0'
BROADCAST_IP: str = '10.0.1.255'
KEEPALIVE_INTERVAL: int = 5
IP_PREFIX: str = "10.0.1."

# After how many nanoseconds is leader considered dead
LEADER_DEAD_AFTER: int = int(2e+10)
# After how many nanoseconds is slave node considered dead
NODE_DEAD_AFTER: int = int(2e+10)

# How fast is monitor sending color requests
MONITOR_COLOR_POLL_RATE:int = 3