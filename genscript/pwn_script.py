from pwn import *
import time
import subprocess
from functools import reduce
import z3

def bytes2int(data, byteorder="little"):
	return int.from_bytes(data, byteorder="little")

def int2bytes(num: int, adjust=8) -> bytes:
	return num.to_bytes((num.bit_length() + 7) // 8, byteorder='little', signed=True if num < 0 else False).ljust(adjust, b"\x00")

def any2bytes(datum, adjust=8):
	if isinstance(datum, str):
		return datum.encode()
	elif isinstance(datum, int):
		return int2bytes(datum, adjust)
	elif isinstance(datum, bytes):
		return datum
	else:
		raise TypeError("any2bytes: datum provided is neither str, int or bytes object")

def send(r, data, newline=True, adjust=8):
	result=b""
	if isinstance(data, list):
		for datum in data:
			result += any2bytes(datum, adjust)
	else:
		result = any2bytes(data, adjust)
	if newline:
		r.sendline(result)
	else:
		r.send(result)
	time.sleep(0.05)

def print_red(str):
	print("\033[91m" + str + "\033[0m")

def genbin(binary_name):
	command = f"genbin ~/challenges/playroom/shellcodes/{binary_name}"
	try:
		return bytes.fromhex(subprocess.check_output(command, shell=True, universal_newlines=True))
	except (subprocess.CalledProcessError, ValueError) as e:
		print(f"An exception occurred: {e}")
	exit(-1)

def rop_chain(chain):	
	for i in range(len(chain)):
		chain[i] = p64(chain[i])
	return reduce(lambda x, y: x + y, chain)

#I/O functions

context.terminal = ['tmux', 'splitw', '-h']
#context.log_level = "warn"
logging.getLogger('pwnlib.elf').setLevel(logging.ERROR)

# breakpoints
b_main = 0xffff

magic_gadget=0x00
if args["MAGIC_GADGET"]:
	magic_gadget = int(args["MAGIC_GADGET"], 16)
if args["REMOTE"]:
	r = remote("url$1", port$2)
elif args["GDB"]:
	r = gdb.debug("./exe$3", f"""
		# b *{b_main}
		unset env
		set disable-randomization off
		set debuginfod enabled on
		c
		""")
else:
	r = process("./exe$3")

#LIBC = ELF("./path")
#LIBC.address = 0xbase
#LIBC.symbols["__symol_name"]

time.sleep(0.5)

r.interactive()
