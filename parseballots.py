#!/usr/bin/env python3

import sys, getopt, json, csv

class ParseMain(object):
	def __init__(self):
		pass
	def main(self, argv):
		try:
			self.optlist, self.args = getopt.getopt(argv, "h", ["help"])
		except getopt.GetoptError as err:
			print(err)
			self.usage()
			self.exit(2)
		for o, a in self.optlist:
			if o in ["-h", "--help"]:
				self.usage()
				sys.exit()
		if len(self.args) != 2:
			self.usage()
			sys.exit(3)

		with open(self.args[0]) as csvfile:
			with open(self.args[1], 'w') as jsonfile:
				json.dump(self.convertCSV(self.readCSV(csvfile)), jsonfile)

	def usage(self):
		print("parseballots.py <csv export> <ballots.json>")

	def convertCSV(self, csvdata):
		ballots = {}
		for r in csvdata:
			if len(r)<2: continue
			if r[0]=="Timestamp" or r[1]=="test@matthew.ath.cx": continue
			ranks = [[],[],[],[],[],[],[],[],[],[],[],[]]
			for (label, pos) in [('a', 3), ('b', 4), ('c', 5), ('d', 6), ('e', 7), ('f', 8), ('g', 9), ('h', 10), ('i', 11), ('j', 12), ('k', 13)]:
				rank = int(r[pos].replace("Rank ", "") if r[pos] else 11)
				ranks[rank-1].append(label)
			ballots[str(ranks)] = (ranks, ballots.get(str(ranks), (ranks, 0))[1]+1)
		return [
			{"count":c, "ballot":b} for (k, (b, c)) in ballots.items()
		]


	def readCSV(self, csvfile):
		return [row for row in csv.reader(csvfile)]


if __name__ == "__main__":
	ParseMain().main(sys.argv[1:])
