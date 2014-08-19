#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Version: 1.0
# Requires python-usbhid (https://pypi.python.org/pypi/hidapi/0.7.99-4)

# vsbutil: Service utility for the Very Serious Button
# © 2014 Greg Courville <Greg_Courville@GregLabs.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>


import sys
import itertools
import argparse
import struct
import time
from collections import OrderedDict
import platform
if (platform.system() == "Linux"):
	import hidraw as hid
else:
	import hid


KEYCODES = {
	"A":       0x04,
	"B":       0x05,
	"C":       0x06,
	"D":       0x07,
	"E":       0x08,
	"F":       0x09,
	"G":       0x0A,
	"H":       0x0B,
	"I":       0x0C,
	"J":       0x0D,
	"K":       0x0E,
	"L":       0x0F,
	"M":       0x10,
	"N":       0x11,
	"O":       0x12,
	"P":       0x13,
	"Q":       0x14,
	"R":       0x15,
	"S":       0x16,
	"T":       0x17,
	"U":       0x18,
	"V":       0x19,
	"W":       0x1A,
	"X":       0x1B,
	"Y":       0x1C,
	"Z":       0x1D,
	"1":       0x1E,
	"2":       0x1F,
	"3":       0x20,
	"4":       0x21,
	"5":       0x22,
	"6":       0x23,
	"7":       0x24,
	"8":       0x25,
	"9":       0x26,
	"0":       0x27,
	"ENTER":   0x28,
	"ESC":     0x29,
	"BKSP":    0x2A,
	"TAB":     0x2B,
	"SPACE":   0x2C,
	"MINUS":   0x2D,
	"EQUALS":  0x2E,
	"LBRACE":  0x2F,
	"RBRACE":  0x30,
	"BSLASH":  0x31,
	"EUR1":    0x32,
	"SCOLON":  0x33,
	"QUOTE":   0x34,
	"TILDE":   0x35,
	"COMMA":   0x36,
	"PERIOD":  0x37,
	"SLASH":   0x38,
	"CAPSLK":  0x39,
	"F1":      0x3A,
	"F2":      0x3B,
	"F3":      0x3C,
	"F4":      0x3D,
	"F5":      0x3E,
	"F6":      0x3F,
	"F7":      0x40,
	"F8":      0x41,
	"F9":      0x42,
	"F10":     0x43,
	"F11":     0x44,
	"F12":     0x45,
	"PRTSC":   0x46,
	"SCROLK":  0x47,
	"PAUSE":   0x48,
	"INSERT":  0x49,
	"HOME":    0x4A,
	"PGUP":    0x4B,
	"DELETE":  0x4C,
	"END":     0x4D,
	"PGDN":    0x4E,
	"RIGHT":   0x4F,
	"LEFT":    0x50,
	"DOWN":    0x51,
	"UP":      0x52,
	"NUMLK":   0x53,
	"KPSLASH": 0x54,
	"KPAST":   0x55,
	"KPMINUS": 0x56,
	"KPPLUS":  0x57,
	"KPENTER": 0x58,
	"KP1":     0x59,
	"KP2":     0x5A,
	"KP3":     0x5B,
	"KP4":     0x5C,
	"KP5":     0x5D,
	"KP6":     0x5E,
	"KP7":     0x5F,
	"KP8":     0x60,
	"KP9":     0x61,
	"KP0":     0x62,
	"KPPERIOD":0x63,
	"EUR2":    0x64,
	"APP":     0x65,
	"POWER":   0x66,
	"KPEQUALS":0x67,
	"F13":     0x68,
	"F14":     0x69,
	"F15":     0x6A,
	"F16":     0x6B,
	"F17":     0x6C,
	"F18":     0x6D,
	"F19":     0x6E,
	"F20":     0x6F,
	"F21":     0x70,
	"F22":     0x71,
	"F23":     0x72,
	"F24":     0x73,
	"HELP":    0x75,
	"MENU":    0x76,
	"UNDO":    0x7A,
	"CUT":     0x7B,
	"COPY":    0x7C,
	"PASTE":   0x7D,
	"FIND":    0x7E,
	"MUTE":    0x7F,
	"VOLUP":   0x80,
	"VOLDN":   0x81,
	"SYSRQ":   0x9A,
	"LCTRL":   0xE0,
	"LSHIFT":  0xE1,
	"LALT":    0xE2,
	"LGUI":    0xE3,
	"RCTRL":   0xE4,
	"RSHIFT":  0xE5,
	"RALT":    0xE6,
	"RGUI":    0xE7,
	}

MODKEYS = {
	"CTRL":    0x01,
	"LCTRL":   0x01,
	"SHIFT":   0x02,
	"LSHIFT":  0x02,
	"ALT":     0x04,
	"LALT":    0x04,
	"GUI":     0x08,
	"LGUI":    0x08,
	"RCTRL":   0x10,
	"RSHIFT":  0x20,
	"RALT":    0x40,
	"RGUI":    0x80,
	}


class VerySeriousButtonNotFound(IOError):
	pass

class VerySeriousButton(object):
	READ_INTERVAL = 0.02
	READ_TRIES = int(1. / READ_INTERVAL)
	USB_VID = 0x16D0
	USB_PID = 0x09D2
	MODE_INACTIVE = 0
	MODE_GAMEPAD = 1
	MODE_SINGLEKEY = 2
	MODE_KEYSEQ = 3
	REPORTID_VSB = 3
	VSB_MODE_NONE = 0
	VSB_MODE_JOYSTICK = 1
	VSB_MODE_SINGLEKEY = 2
	VSB_MODE_KEYSEQ = 3
	VSB_CMD_NONE = 0
	VSB_CMD_GETDEVINFO = 1
	VSB_CMD_GETCFG = 2
	VSB_CMD_SETCFG = 3
	VSB_CMD_SAVECFG = 4
	VSB_CMD_LOADCFG = 5
	VSB_CMD_WIPECFG = 6
	VSB_CMD_READPAGE = 7
	VSB_CMD_WRITEPAGE = 8
	VSB_CMD_GETSERIAL = 0x11
	VSB_CMD_FUCKYOU = 0xF0
	VSB_CMD_EEPREAD = 0xF1
	VSB_CMD_EEPWRITE = 0xF2
	VSB_CMD_RESET = 0xF3
	VSB_CMD_DFU = 0xF4
	VSB_RESP_NULL = 0
	VSB_RESP_OK = 1
	VSB_RESP_ERR = 0x10
	VSB_RESP_BADCMD = 0x11
	VSB_RESP_BADCS = 0x12
	VSB_RESP_BADMEM = 0x14
	VSB_RESP_BADIDX = 0x18
	VSB_RESP_BUSY = 0x80
	@classmethod
	def mode_string_for_value(cls, x):
		return {
			cls.VSB_MODE_NONE: "none",
			cls.VSB_MODE_JOYSTICK: "joystick",
			cls.VSB_MODE_SINGLEKEY: "single key",
			cls.VSB_MODE_KEYSEQ: "key sequence",
			}[x]
	@classmethod
	def list_connected(cls):
		btns = hid.enumerate(cls.USB_VID, cls.USB_PID)
		return [
			(btn["serial_number"],btn["release_number"],btn["path"]) for btn in btns
			 #if btn["manufacturer_string"] == cls.USB_MFR
			 #and btn["product_string"] == cls.USB_PROD
			]
	def __init__(self, serial=None):
		btns = dict(((ser,(path,rls)) for (ser,rls,path) in self.list_connected()))
		if not btns:
			raise VerySeriousButtonNotFound("No VerySeriousButtons connected")
		if not serial:
			path, rls = btns.values()[0]
		else:
			if serial not in btns:
				raise VerySeriousButtonNotFound("Couldn't find VerySeriousButton with serial number '%s'" % (serial,))
			path, rls = btns[serial]
		self.release_number = rls
		self.serial_number = serial
		self.hid_dev = hid.device()
		self.hid_dev.open_path(path)
		self.hid_dev.set_nonblocking(False)
		info = self.get_device_info()
		self.keyseq_page_size = info["keyseq_pagesize"]
		self.keyseq_nkeys = info["keyseq_nkeys"]
		self.num_keyseq_pages = info["keyseq_npages"]
		self.singlekey_nkeys = info["singlekey_nkeys"]
	def write_command(self, cmd_id, data=""):
		buf = struct.pack("BBB", self.REPORTID_VSB, cmd_id, 0) + bytearray(data)
		self.hid_dev.send_feature_report(list(bytearray(buf)))
	def read_response(self):
		data = None
		for foo in range(self.READ_TRIES):
			data = self.hid_dev.get_feature_report(self.REPORTID_VSB, 32)
			if data[0] != self.REPORTID_VSB:
				raise IOError("Received incorrect report ID (expecting %d, got %d)" % (self.REPORTID_VSB,data[0]))
			if (len(data) > 2) and (data[2] != self.VSB_RESP_BUSY):
				break
			data = None
			time.sleep(self.READ_INTERVAL)
		if data is None:
			raise IOError("Device didn't respond!")
		return data[1], data[2], bytearray(data[3:])
	def get_device_info(self):
		bytes = self.do_query(self.VSB_CMD_GETDEVINFO)
		return OrderedDict(
			singlekey_nkeys=bytes[0],
			keyseq_nkeys=bytes[1],
			keyseq_pagesize=bytes[2],
			keyseq_npages=bytes[3],
			)
	def get_config(self):
		bytes = self.do_query(self.VSB_CMD_GETCFG)
		return {
			"mode": bytes[0],
			"mods": bytes[1],
			"keycodes": list(bytes[2:2+self.singlekey_nkeys]),
			"keyseq_len": bytes[8]
			}
	def set_config(self, cfg):
		valid_modes = (
			self.MODE_GAMEPAD,
			self.MODE_SINGLEKEY,
			self.MODE_KEYSEQ
			)
		mode = int(cfg["mode"])
		if not mode in valid_modes:
			raise ValueError("Invalid mode value: " + repr(cfg["mode"]))
		keycodes = list(bytearray(cfg["keycodes"]))
		mods = int(cfg["mods"])
		if len(keycodes) > self.singlekey_nkeys:
			raise ValueError("Keycodes array too long")
		if len(keycodes) < self.singlekey_nkeys:
			keycodes += [0]*(self.singlekey_nkeys-len(keycodes))
		keyseq_len = int(cfg["keyseq_len"])
		if (keyseq_len < 0) or (keyseq_len > self.num_keyseq_pages):
			raise ValueError("Invalid keyseq length: " + repr(cfg["keyseq_len"]))
		cfg_bytes = [mode, mods] + keycodes + [keyseq_len]
		self.do_query(self.VSB_CMD_SETCFG, data=bytearray(cfg_bytes))
	def read_raw_keyseq_page(self, i):
		data = self.do_query(self.VSB_CMD_READPAGE, data=[int(i),])
		if data[0] != i:
			raise IOError("Requested keyseq page %d, got page %d" % (i,data[0]))
		return data[1:1+self.keyseq_page_size]
	def read_raw_keyseq(self):
		ks_len = self.get_config()["keyseq_len"]
		bytes = []
		for i in range(ks_len):
			bytes += self.read_raw_keyseq_page(i)
		return bytearray(bytes)
	def write_raw_keyseq_page(self, i, data):
		bytes = list(bytearray(data))
		wr_pg = int(i)
		if (wr_pg < 0) or (wr_pg >= self.num_keyseq_pages):
			raise ValueError("Keyseq page number out of range: " + repr(i))
		if len(bytes) > self.keyseq_page_size:
			raise ValueError("Keyseq page data is too long")
		if len(bytes) < self.keyseq_page_size:
			bytes += [0]*(self.keyseq_page_size - len(bytes))
		self.do_query(self.VSB_CMD_WRITEPAGE, [wr_pg] + bytes)
	def write_keyseq(self, keyseq):
		if len(keyseq) > self.num_keyseq_pages:
			raise ValueError("Key sequence too long (length %d, maximum %d)" % (len(keyseq), self.num_keyseq_pages))
		i = 0
		for mod, keycodes in keyseq:
			if len(keycodes) > self.keyseq_nkeys:
				raise ValueError("Too many keys in key group %d (got %d, max %d)" % (i, len(keycodes), self.keyseq_nkeys))
			self.write_raw_keyseq_page(i, [mod] + list(keycodes))
			i += 1
		self.update_config(keyseq_len=i)
	def write_raw_keyseq(self, data):
		bytes = list(bytearray(data))
		i = 0
		while True:
			start = i * self.keyseq_page_size
			end = start + self.keyseq_page_size
			if not bytes[start:end]:
				break
			self.write_raw_keyseq_page(i, bytes[start:end])
			i += 1
		self.update_config(keyseq_len=i)
	def update_config(self, **kwargs):
		config = self.get_config()
		for key in kwargs:
			if key not in config:
				raise KeyError("%s is not a valid config parameter name" % (repr(key),))
			config[key] = kwargs[key]
		self.set_config(config)
	def do_query(self, cmd_id, data=""):
		self.write_command(cmd_id, data)
		rcmd, rresp, rdata = self.read_response()
		if rcmd != cmd_id:
			raise IOError("Command ID returned by the device (0x%X) doesn't match the command ID sent (0x%X)" % (rcmd, cmd_id))
		if rresp == self.VSB_RESP_NULL:
			raise IOError("Got a null response code")
		elif rresp == self.VSB_RESP_BADCMD:
			raise IOError("Device reported 0x%X is a bad command ID" % (rcmd,))
		elif rresp == self.VSB_RESP_BADCS:
			raise IOError("Device reported stored configuration is corrupt")
		elif rresp == self.VSB_RESP_BADIDX:
			raise IOError("Device reported %d is a bad keyseq page number" % (rdata[0],))
		elif rresp == self.VSB_RESP_ERR:
			raise IOError("Device reported a general error")
		elif rresp != self.VSB_RESP_OK:
			raise IOError("Device returned unrecognized response code 0x%X" % (rresp,))
		return rdata
	def get_fuckyou(self):
		data = self.do_query(self.VSB_CMD_FUCKYOU)
		return data.split("\x00",1)[0]
	def reset(self):
		self.do_query(self.VSB_CMD_RESET)
		self.close()
	def reset_to_bootloader(self):
		self.do_query(self.VSB_CMD_DFU)
		self.close()
	def set_mode(self, mode):
		self.update_config(mode=mode)
	def init_stored_config(self):
		self.do_query(self.VSB_CMD_WIPECFG)
	def store_current_config(self):
		self.do_query(self.VSB_CMD_SAVECFG)
	def load_stored_config(self):
		self.do_query(self.VSB_CMD_LOADCFG)
	def read_eeprom_byte(self, addr):
		data = self.do_query(self.VSB_CMD_EEPREAD, data=struct.pack(">H", addr))
		raddr = struct.unpack(">H", str(data[0:2]))[0]
		if raddr != addr:
			raise IOError("Device replied with EEPROM read address 0x%X (expected 0x%X)" % (raddr, addr))
		return data[2]
	def read_eeprom_bytes(self, addr, n):
		bytes = []
		for i in range(n):
			bytes.append(self.read_eeprom_byte(addr+i))
		return bytearray(bytes)
	def write_eeprom_byte(self, addr, v):
		data = self.do_query(self.VSB_CMD_EEPWRITE, data=struct.pack(">HB", addr, v))
		raddr = struct.unpack(">H", str(data[0:2]))[0]
		if raddr != addr:
			raise IOError("Device replied with EEPROM write address 0x%X (expected 0x%X)" % (raddr, addr)) #This is really unnecessary
	def write_eeprom_bytes(self, addr, vs):
		for i, v in enumerate(vs):
			self.write_eeprom_byte(addr+i, v)
	def get_serialnum(self):
		data = self.do_query(self.VSB_CMD_GETSERIAL)
		l = data[0]
		return str(data[1:1+l])
	def close(self):
		if self.hid_dev is not None:
			self.hid_dev.close()
		self.hid_dev = None

def parse_hex(x):
	return int(x.strip().split("0x",1)[-1],base=16)

def handle_cmdline_args(argv):
	ap = argparse.ArgumentParser(prog=argv[0], description="VerySeriousButton service tool")
	ap.add_argument("--serial", default=None, help="serial number of VSB unit to connect to")
	subparser = ap.add_subparsers(dest="cmd")
	subparser.add_parser("getserial", help="get VSB serial number")
	subparser.add_parser("getdevinfo", help="get VSB device info")
	subparser.add_parser("getconfig", help="get VSB device configuration")
	subparser.add_parser("wipeconfig", help="initialize stored configuration to factory defaults")
	subparser.add_parser("saveconfig", help="store current configuration to EEPROM")
	subparser.add_parser("loadconfig", help="read stored configuration from EEPROM")
	subparser.add_parser("getfuckyou", help="retrieve a fuckyou")
	setjoy = subparser.add_parser("setjoy", help="set VSB to gamepad mode")
	setkey = subparser.add_parser("setkey", help="set VSB to single keyboard key mode")
	setkey.add_argument("keygroup", metavar="KEYS", help="plus-separated group of key names, e.g. 'LALT+LSHIFT+F'")
	setkeys = subparser.add_parser("setkeys", help="set VSB to keyboard sequence mode")
	setkeys.add_argument("keygroups", metavar="KEYS", nargs="+", help="plus-separated group(s) of key names")
	eepread = subparser.add_parser("eepread", help="read byte(s) from EEPROM")
	eepread.add_argument("addr", metavar="ADDR", type=parse_hex, help="start address in hex")
	eepread.add_argument("nbytes", metavar="NBYTES", type=int, nargs="?", default=1, help="number of bytes to read")
	eepwrite = subparser.add_parser("eepwrite", help="write byte(s) to EEPROM")
	eepwrite.add_argument("addr", metavar="ADDR", type=int)
	eepwrite.add_argument("values", nargs="+", metavar="VALUE", type=parse_hex, help="byte value(s) to write, in hex")
	subparser.add_parser("reset", help="make VSB initiate a hardware reset")
	subparser.add_parser("dfu", help="make VSB jump into USB DFU bootloader")
	return ap.parse_args(argv[1:])

def parse_keygroup(group_str):
	pcs = [x.strip().upper() for x in group_str.split("+")]
	mod = 0;
	keys = []
	mods_phase = True
	for n, pc in enumerate(pcs):
		if (pc not in MODKEYS) or (n == len(pcs)-1):
			mods_phase = False
		if mods_phase:
			mod |= MODKEYS[pc]
		else:
			keys.append(KEYCODES[pc])
	return mod, keys

def run(argv):
	opts = handle_cmdline_args(argv)
	vsb = VerySeriousButton(serial = opts.serial)
	try:
		if opts.cmd == "getserial":
			print vsb.get_serialnum()
		elif opts.cmd == "getdevinfo":
			info = vsb.get_device_info()
			for key in info:
				print "%16s = %s" % (key, info[key])
		elif opts.cmd == "getconfig":
			cfg = vsb.get_config()
			info = OrderedDict(
				mode = "%d (%s)" % (cfg["mode"], vsb.mode_string_for_value(cfg["mode"]),),
				keycodes = ", ".join("0x%02X" % (x,) for x in cfg["keycodes"] if x != 0),
				mods = "0x%02X" % (cfg["mods"],),
				keyseq_len = "%d" % (cfg["keyseq_len"],),
				)
			for key in info:
				print "%16s = %s" % (key, info[key])
		elif opts.cmd == "wipeconfig":
			vsb.init_stored_config()
			print "Stored configuration initialized to factory defaults."
		elif opts.cmd == "saveconfig":
			vsb.store_current_config()
			print "Current configuration stored."
		elif opts.cmd == "loadconfig":
			vsb.load_stored_config()
			print "Stored configuration loaded."
		elif opts.cmd == "getfuckyou":
			print vsb.get_fuckyou()
		elif opts.cmd == "setkey":
			mod, keys = parse_keygroup(opts.keygroup)
			vsb.update_config(
				mode = vsb.VSB_MODE_SINGLEKEY,
				keycodes = keys,
				mods = mod,
				)
			print "Configured for single-key mode."
		elif opts.cmd == "setjoy":
			vsb.update_config(
				mode = vsb.VSB_MODE_JOYSTICK,
				)
			print "Configured for gamepad mode."
		elif opts.cmd == "readkeyseq":
			print " ".join("%02X" % (b,) for b in vsb.read_raw_keyseq())
		elif opts.cmd == "setkeys":
			keygroups = [parse_keygroup(x) for x in opts.keygroups]
			vsb.write_keyseq(keygroups)
			vsb.update_config(mode=vsb.VSB_MODE_KEYSEQ)
			vsb.store_current_config()
			print "Configured for key sequence mode; key sequence stored; current configuration stored."
		elif opts.cmd == "eepread":
			print " ".join(("%02X" % (b,) for b in vsb.read_eeprom_bytes(opts.addr, opts.nbytes)))
		elif opts.cmd == "eepwrite":
			vsb.write_eeprom_bytes(opts.addr, opts.values)
			print "%d bytes written to EEPROM." % (len(opts.values),)
		elif opts.cmd == "reset":
			vsb.reset()
			print "Performing reset in 1 second."
		elif opts.cmd == "dfu":
			vsb.reset_to_bootloader()
			print "Jumping to bootloader in 1 second."
	finally:
		vsb.close()


if __name__ == "__main__":
	run(sys.argv)
