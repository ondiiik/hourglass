# Default brightness
BRIGHTNESS = 1

# Delay in seconds after which clock will be displayed
CLOCK_TIME = 8

# Time zone in hours against GMT
TIME_ZONE_HOURS = 2

# Time bright time range in hours
CLOCK_BRIGHT_TIME = 7, 20

# NTP server to be used for time synchronization
NTP_SERVER = '0.cz.pool.ntp.org'

# All possible SSID and passwords shall be listed here
WIFI = (b'MySSID', b'MyPassword'),

# Time in seconds after which the display will be dimmed to reduce consumption
DIMM_TIME = 30

# Time in seconds when display will switch to screen saver mode
SAVER_TIME = 120

# Compensation of measured accelerations
ACC_COMPENSATE = -10, 29, 69

# Transform accelerometer vector to real position
# inside clock. Absolute value of nuber says
# positions of X (1), Y(2), Z(3) and signess says
# if value is positive or negative.
ACC_TRANSFORM = 2, -1, -3

# Follows HW configuration
PIN_SDA = 5
PIN_SCL = 4
SPI_ID = 1