#!/usr/bin/python3
# Copyright (c) 2023 Matthew Johnson
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import sys, getopt, json, pprint, copy
from schulze_stv import SchulzeSTV
from condorcet import CondorcetHelper


class VoteMain(object):
	def __init__(self):
		self.calculator=None
	def main(self, argv):
		try:
			self.optlist, self.args = getopt.getopt(argv, "h", ["help"])
		except getopt.GetoptError as err:
			print(err)
			self.usage()
			sys.exit(2)
		for o, a in self.optlist:
			if o in ["-h", "--help"]:
				self.usage()
				sys.exit()
		if len(self.args) != 1:
			self.usage()
			sys.exit(3)
		with open(self.args[0]) as f:
			self.config = json.load(f)
		with open(self.config["votefile"]) as f:
			self.ballots = json.load(f)
		self.pairWise()
		self.removeLosersToNoneOfTheAbove()
		if len(self.config["candidates"])-len(self.losers) <= self.config["positions"]:
			self.winners=set(self.config["candidates"].keys())-set(self.losers)
		else:
			self.calculateSchulze()
		self.printResult()

	def usage(self):
		print("judgevote.py <config.json>")

	def removeLosersToNoneOfTheAbove(self):
		self.losers = set()
		for k in self.pairWiseResults:
			(a, b) = k
			(w, _) = self.pairWiseResults[k]
			if self.config['candidates'][w] == "None of the above":
				self.losers.add(a)
				self.losers.add(b)
		for x in self.losers:
			self.removeFromBallots(self.ballots, x)

	def removeFromBallots(self, ballots, x):
		for j in ballots:
			for i in j["ballot"]:
				if x in i:
					i.remove(x)
				if len(i) == 0:
					j["ballot"].remove([])

	def pairWise(self):
		self.pairWiseResults = {}
		for a in self.config["candidates"]:
			for b in self.config["candidates"]:
				if a < b:
					self.pairWiseResults[(a,b)] = self.pairWiseResult(a, b)

	def pairWiseResult(self, a, b):
		votesa=0
		votesb=0
		ballots = copy.deepcopy(self.ballots)
		CondorcetHelper().standardize_ballots(ballots, CondorcetHelper.BALLOT_NOTATION_GROUPING)
		for i in ballots:
			r = self.findResultInBallot(i["ballot"], a, b)
			if r > 0:
				votesa = votesa + i["count"]
			elif r < 0:
				votesb = votesb + i["count"]
		return (a if votesa>votesb else b, abs(votesa-votesb))

	def findResultInBallot(self, ballot, a, b):
		if a in ballot and not b in ballot:
			return 1
		elif b in ballot and not a in ballot:
			return -1
		elif not b in ballot and not a in ballot:
			return 0
		elif ballot[a] > ballot[b]:
			return 1
		elif ballot[b] > ballot[a]:
			return -1
		else:
			return 0

	def calculateSchulze(self):
		self.calculator = SchulzeSTV(ballots=self.ballots, tie_breaker=None, required_winners=self.config["positions"], ballot_notation=CondorcetHelper.BALLOT_NOTATION_GROUPING)
		self.calculator.calculate_results()
		self.winners = self.calculator.winners

	def printResult(self):
		print("Candidates:")
		for k in sorted(self.config['candidates'].keys()):
			print("   - %s: %s" % (k, self.config['candidates'][k]))
		print("Number of winners: %s" % self.config['positions'])
		if self.calculator: pprint.pprint(self.calculator.as_dict())
		print("Total number of votes cast: %s"%sum(item["count"] for item in self.ballots))
		print("Pairwise results:")
		for k in sorted(self.pairWiseResults.keys()):
			(a, b) = k
			(w, diff) = self.pairWiseResults[k]
			print("   - %s vs %s: %s (%s)" % (self.config['candidates'][a], self.config['candidates'][b], self.config['candidates'][w], diff))
		print("Removed due to losing to None of the Above:")
		for i in self.losers:
			print("   - "+self.config['candidates'][i])
		print("Winners (in no particular order):")
		for i in self.winners:
			print("   - "+self.config['candidates'][i])



if __name__ == "__main__":
	VoteMain().main(sys.argv[1:])
