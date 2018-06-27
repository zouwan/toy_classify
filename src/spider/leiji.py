import sys

for i in xrange(1, len(sys.argv)):
	print sys.argv[i]
	dic = {}
	for line in open(sys.argv[i]).readlines():
		line = line.strip("\n")
		cols = line.split("\t")
		val = 0
		try:
			val = int(dic[cols[0]])
		except:
			pass
		dic[cols[0]] = val + int(cols[1])

	filename = "r_" + sys.argv[i]
	renamefid = open(filename, "w")
	for key in dic:
		renamefid.write("%s\t%d\r\n" % (key, dic[key]))
	renamefid.close()
