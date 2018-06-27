#encoding: utf-8

def ConvertToInt(s):
	if s is None:
		return 0
	while True:
		try:
			return int(float(s))
		except:
			pass
		unit = 1
		idx = s.find(u"千")
		if idx >= 0:
			unit *= 1000
			s = s[0:idx]
		idx = s.find(u"万")
		if idx >= 0:
			unit *= 10000
			s = s[0:idx]
		idx = s.find(u"亿")
		if idx >= 0:
			unit *= 100000000
			s = s[0:idx]
		try:
			return int(float(s) * unit)
		except:
			pass
		return 0

if __name__ == '__main__':
	print ConvertToInt("12")
	print ConvertToInt("1.2")
	print ConvertToInt(u"1.2万")
	print ConvertToInt(u"2万")
	print ConvertToInt(u"万")
