# main.py -- put your code here!
from machine import Pin, UART, reset
import time
import json
from math import sqrt, acos
from config_storage import save_string, fb_txt

def sub_cb(topic, msg):
	print((topic, msg))
	if topic == b'notification' and msg == b'received':
		print('ESP received hello message')

def connect_and_subscribe():
	global client_id, mqtt_server, topic_sub, mqtt_user, mqtt_pass
	client = MQTTClient(client_id, mqtt_server)
	client.set_callback(sub_cb)
	client.connect()
	client.subscribe(topic_sub)
	print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
	return client

def restart_and_reconnect():
	print('Failed to connect to MQTT broker. Reconnecting...')
	time.sleep(10)
	reset()

try:
	client = connect_and_subscribe()
except OSError as e:
	restart_and_reconnect()

def bit_length(n):
	"""Return the number of bits required to represent an integer in binary."""
	if not isinstance(n, int):
		raise TypeError("bit_length() argument must be an integer")
	if n == 0:
		return 0
	if n < 0:
		n = -n  # Handle negative numbers
	length = 0
	while n:
		length += 1
		n >>= 1  # Shift right by 1 bit
	return length

def read_exact(n, timeout_ms=50):
	buf = b''
	start = time.ticks_ms()

	while len(buf) < n:
		if uart.any():
			buf += uart.read(n - len(buf))
		if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
			return None
	return buf

def check_crc(data):
	msg = (
		reverse_byte(data[0]) << 24 |
		reverse_byte(data[1]) << 16 |
		reverse_byte(data[2]) << 8  |
		reverse_byte(data[3])
	)
	expected = reverse_byte(crc8(msg))
	return expected == data[4]

# ------------------ CONFIG ------------------
UART_ID = 1
BAUD = 9600
TX_PIN = 0
RX_PIN = 5

SYN_PIN = 3
SCS_PIN = 1

POLY = 0x107  # 0x07 + implicit x^8

# ------------------ HARDWARE ------------------
uart = UART(UART_ID, baudrate=BAUD, tx=0, rx=5)

syn = Pin(3, Pin.OUT, value=1)
scs = Pin(1, Pin.OUT, value=1)
led_green = Pin(10, Pin.OUT)
led_red = Pin(7, Pin.OUT, value=0)
led_blue = Pin(6, Pin.OUT, value=0)
rst_btn = Pin(8, Pin.IN)

# ------------------ FAST BIT REVERSE ------------------+
# Precomputed lookup table for 8-bit reversal
def reverse_byte(b):
	b = (b & 0xF0) >> 4 | (b & 0x0F) << 4
	b = (b & 0xCC) >> 2 | (b & 0x33) << 2
	b = (b & 0xAA) >> 1 | (b & 0x55) << 1
	return b

# ------------------ CRC ------------------
def crc8(message, poly=POLY):
	"""Compute CRC-8 (STPM style)."""
	message <<= 8
	while bit_length(message) >= 9:
		shift = bit_length(message) - 9
		message ^= (poly << shift)
	return message & 0xFF

# ------------------ STPM CONTROL ------------------
def stpm_reset():
	scs.off(); time.sleep_us(40)
	scs.on()
	for _ in range(3):
		syn.off(); time.sleep_us(40)
		syn.on();  time.sleep_us(40)
		

def pulse_syn():
	syn.off()
	time.sleep_us(20)
	syn.on()
	time.sleep_us(20)
	scs.off()
	time.sleep_us(20)
	scs.on()

# ------------------ FRAME BUILD ------------------
def build_frame(b1, b2, b3, b4):
	msg = (
		reverse_byte(b1) << 24 |
		reverse_byte(b2) << 16 |
		reverse_byte(b3) << 8  |
		reverse_byte(b4)
	)
	crc = reverse_byte(crc8(msg))
	return bytes([b1, b2, b3, b4, crc])

# ------------------ COMMAND ------------------
FREQ_REG = 0x05 # Set default line frequency to 60 Hz
READ_REG = 0x48 # Current and voltage measurements
frame_init = build_frame(READ_REG, FREQ_REG, 0x00, 0x08)
frame_vcrms = build_frame(READ_REG, 0xFF, 0xFF, 0xFF)
UART_REG = 0x28 # UART status register
frame_uart = build_frame(UART_REG, 0xFF, 0x00, 0x00)
CT_REG = 0x19 # Change Shunt to CT (modify current gain)
frame_gain = build_frame(0xFF, CT_REG, 0x27, 0x03)
PERI_REG = 0x2E # Period register
frame_peri = build_frame(PERI_REG, 0xFF, 0xFF, 0xFF)
PHASE_REG = 0x4E # Phase measurement register
frame_phase = build_frame(PHASE_REG, 0xFF, 0xFF, 0xFF)
ACT_REG = 0x5C # Active power register
frame_act = build_frame(ACT_REG, 0xFF, 0xFF, 0xFF)
REA_REG = 0x60 # Reactive power register
frame_rea = build_frame(REA_REG, 0xFF, 0xFF, 0xFF)

# ------------------ MAIN ------------------
for _ in range(10):
	time.sleep(1)
	led_blue.toggle()
stpm_reset()

vref = 1.18
R1 = 820000
R2 = 1000
calv = 0.875
Av = 2
cali = 0.875
Ai = 16
ks = 0.0025
kint = 1

f = 60
FClk = 125000

lsb_v = (vref*(1+R1/R2))/(calv*Av*pow(2,15))
lsb_i = vref/(cali*Ai*ks*kint*pow(2,17))
lsb_per = 0.000008 # 8 us
lsb_ph = f*360/FClk
lsb_pow = (pow(vref,2)*(1+R1/R2))/(kint*Av*Ai*ks*calv*cali*pow(2,28))

time.sleep(1)

# Send READ_REG to STPM
uart.write(frame_init)

time.sleep_ms(500)

while True:
	if not rst_btn.value():
		save_string(fb_txt, "None")
		reset()
	try:
		client.check_msg()
		if (time.time() - last_message) > message_interval:
			# msg = b'Hello #%d' % counter
			#client.publish(topic_pub, msg)
			last_message = time.time()
			counter += 1
			led_green.toggle()
			pulse_syn()
			time.sleep_us(100)
			uart.read()  # flush garbage

			# Reading VC_RMS by sending next reg in line
			uart.write(frame_peri)

			# Wait until full response arrives
			time.sleep_ms(40)
			data = read_exact(5)
			if not data:
				print("Timeout")
				stpm_reset()
				# reset()
				led_red.on()
				continue
			if not check_crc(data):
				print("CRC FAIL")
				continue

			if data:
				# FIXED: correct byte assembly
				led_red.off()
				msg = (
					(data[3] << 24) |
					(data[2] << 16) |
					(data[1] << 8)  |
					data[0]
				)

				print("---------Voltage and Current Registers---------")
				# print("message:", bin(msg))

				volt_reg = msg & 0x7FFF
				curr_reg = msg >> 15

				# print("Voltage Register:", volt_reg)
				# print("Current Register:", curr_reg)
				# print()

				voltage = volt_reg * lsb_v
				current = curr_reg * lsb_i

				print("Voltage RMS (V):", voltage)
				print("Current RMS (A):", current)
				# print()


			time.sleep_us(50)
			uart.read()  # flush garbage
			# Reading Period by sending next reg in line
			uart.write(frame_phase)

			# Wait until full response arrives
			time.sleep_ms(40)
			data = read_exact(5)
			if not data:
				print("Timeout")
				continue
			if not check_crc(data):
				print("CRC FAIL")
				continue
			if data:
				# FIXED: correct byte assembly
				msg = (
					(data[3] << 24) |
					(data[2] << 16) |
					(data[1] << 8)  |
					data[0]
				)

				print("---------Period Register---------")
				# print("message:", bin(msg))

				period_reg = msg & 0xFFF

				# print("Period Register:", period_reg)
				# print()

				period = period_reg * lsb_per
				if period:
					frequency = 1/period
				else:
					frequency = 0

				print("Period (s):", period)
				print("Frequency (Hz):", frequency)
				# print()


			time.sleep_us(50)
			uart.read()  # flush garbage
			# Reading Phase by sending next reg in line
			uart.write(frame_act)

			# Wait until full response arrives
			time.sleep_ms(40)
			data = read_exact(5)
			if not data:
				print("Timeout")
				continue
			if not check_crc(data):
				print("CRC FAIL")
				continue
			if data:
				# FIXED: correct byte assembly
				msg = (
					(data[3] << 24) |
					(data[2] << 16) |
					(data[1] << 8)  |
					data[0]
				)

				print("---------Phase Register---------")
				# print("message:", bin(msg))

				phase_reg = (msg >> 16) & 0xFFF

				# print("Phase Register:", phase_reg)
				# print()

				phase = phase_reg * lsb_ph
				# if phase > 180:
				# 	phase -= 360
				phase -= 180

				print("Phase (deg):", phase)
				# print()

			
			time.sleep_us(50)
			uart.read()  # flush garbage
			# Reading Active by sending next reg in line
			uart.write(frame_rea)

			# Wait until full response arrives
			time.sleep_ms(20)
			data = read_exact(5)
			if not data:
				print("Timeout")
				continue
			if not check_crc(data):
				print("CRC FAIL")
				continue
			if data:
				# FIXED: correct byte assembly
				msg = (
					(data[3] << 24) |
					(data[2] << 16) |
					(data[1] << 8)  |
					data[0]
				)

				print("---------Active Power Register---------")
				# print("message:", bin(msg))

				active_reg = msg & 0xFFFFFFF
				active_sign = msg & 0x10000000

				# print("Active Register:", active_reg)
				# print()
				if active_sign:
					active_reg = active_reg - 0xFFFFFFF

				Active = active_reg * lsb_pow * -1

				print("Active Power (W):", Active)
				# print()

			
			time.sleep_us(50)
			uart.read()  # flush garbage
			# Reading Reactive by sending next reg in line
			uart.write(frame_vcrms)

			# Wait until full response arrives
			time.sleep_ms(20)
			data = read_exact(5)
			if not data:
				print("Timeout")
				continue
			if not check_crc(data):
				print("CRC FAIL")
				continue
			if data:
				# FIXED: correct byte assembly
				msg = (
					(data[3] << 24) |
					(data[2] << 16) |
					(data[1] << 8)  |
					data[0]
				)

				print("---------Reactive Power Register---------")
				# print("message:", bin(msg))

				reactive_reg = msg & 0xFFFFFFF
				reactive_sign = msg & 0x10000000

				# print("Reactive Register:", reactive_reg)
				# print()
				if reactive_sign:
					reactive_reg = reactive_reg - 0xFFFFFFF
						
				Reactive = reactive_reg * lsb_pow
				

				print("Reactive Power (VA):", Reactive)
				print()

			Apparent = sqrt(pow(Active,2)+pow(Reactive,2))
			PowerFactor = Active/Apparent
			Phase_angle = acos(PowerFactor)
			UNIX_OFFSET = 946684800
			json_msg = json.dumps({"esp_id":"ESP_002", "voltage":voltage, "current":current, "p_active":Active, "p_reactive":Reactive, "p_apparent":Apparent, "power_factor":PowerFactor, "phase":phase, "frequency":frequency, "date":time.time()+UNIX_OFFSET})

			client.publish(topic_pub, json_msg)

	except OSError as e:
		restart_and_reconnect()