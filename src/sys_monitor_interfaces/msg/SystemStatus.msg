# One snapshot of the local machine state.
# The time the record was taken is carried in header.stamp.

std_msgs/Header header

# Host name of the machine that produced this record.
string hostname

# CPU usage in percent (0.0 - 100.0).
float32 cpu_percent

# Memory usage in percent (0.0 - 100.0).
float32 memory_percent

# Total physical memory in bytes.
uint64 memory_total_bytes

# Available physical memory in bytes.
uint64 memory_available_bytes

# Cumulative bytes received on all network interfaces since boot.
uint64 net_bytes_recv

# Cumulative bytes sent on all network interfaces since boot.
uint64 net_bytes_sent
