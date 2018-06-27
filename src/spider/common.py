#!/usr/local/bin/python
#encoding: utf-8
import time, sys

def LogOut(cont):
	tmStr = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
	sys.stdout.write("%s %s\n" % (tmStr, cont.encode("utf-8")))
	sys.stdout.flush()

def LogErr(cont):
	global LogFid
	tmStr = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
	sys.stderr.write("%s %s\n" % (tmStr, cont))
	sys.stderr.flush()
