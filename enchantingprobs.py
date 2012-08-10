#!/usr/bin/env python2

"""
Copyright (c) 2012 Dennis Bliefernicht

mc-enchantment-probabilities is free software: you can redistribute 
it and/or modify it under the terms of the GNU General Public License 
as published by the Free Software Foundation, either version 3 of the 
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from fractions import Fraction
from functools import reduce
import sys
import math
import sqlite3

# generic constants across all versions

ROMANS = [ "", "I", "II", "III", "IV", "V" ]

TYPE_ARMOUR = 1
TYPE_FEET = 2
TYPE_HEAD = 4
TYPE_WEAPON = 8
TYPE_TOOL = 16
TYPE_BOW = 32
TYPE_NAMES = { TYPE_ARMOUR: "armour", TYPE_FEET: "boots", TYPE_HEAD: "helmet", TYPE_WEAPON: "sword", TYPE_TOOL: "tool", TYPE_BOW: "bow" }

MATERIAL_CLOTH = 0
MATERIAL_CHAIN = 1
MATERIAL_IRON = 2
MATERIAL_GOLD = 3
MATERIAL_DIAMOND = 4
MATERIAL_WOOD = 5
MATERIAL_STONE = 6
MATERIAL_NAMES = [ "leather", "chain", "iron", "gold", "diamond", "wood", "stone" ]

def load_model():
	"""
	contains the model specifications for different versions of minecraft
	must be called before any calculations are being performed
	- the global variable MODEL contains the model version number
	"""
	global MODEL, MAX_LEVEL, XP_PER_MOB, TOOL_ENCHANTABILITY, WEAPON_ENCHANTABILITY, ARMOUR_ENCHANTABILITY, BOW_ENCHANTABILITY, ENCHANTABILITY, ENCHANTABILITY_RANGE, ENCH, xp_for_level
	
	if MODEL == 12:
		MAX_LEVEL = 50
		XP_PER_MOB = 5
		
		def xp_for_level(lvl):
			if lvl <= 1:
				return 7
			else:
				if lvl % 2 == 0:
					return xp_for_level(lvl - 1) + (lvl / 2) * 7 + 3
				else:
					return xp_for_level(lvl - 1) + ((lvl+1) / 2) * 7
	
		TOOL_ENCHANTABILITY = [ -1, -1, 14, 22, 10, 15, 5 ]
		WEAPON_ENCHANTABILITY = TOOL_ENCHANTABILITY
		ARMOUR_ENCHANTABILITY = [ 15, 12, 9, 25, 10, -1, -1 ]
		BOW_ENCHANTABILITY = [ -1, -1, -1, -1, -1, 1, -1]
		ENCHANTABILITY = { TYPE_ARMOUR: ARMOUR_ENCHANTABILITY, 
						   TYPE_FEET: ARMOUR_ENCHANTABILITY,
						   TYPE_HEAD: ARMOUR_ENCHANTABILITY,
						   TYPE_WEAPON: WEAPON_ENCHANTABILITY,
						   TYPE_TOOL: TOOL_ENCHANTABILITY,
						   TYPE_BOW: BOW_ENCHANTABILITY,
						 }
		ENCHANTABILITY_RANGE=0.25
		
		# name, weight, maxlevel, minpoints, maxpoints, types, exclusion group, index
		ENCH = [ ["Protection",        10, 4, lambda x: 1+(x-1)*16,    lambda x: 21+(x-1)*16, TYPE_ARMOUR|TYPE_FEET|TYPE_HEAD, 1, 0], 
			 ["Fire Protection",        5, 4, lambda x: 10+(x-1)*8,    lambda x: 22+(x-1)*8,  TYPE_ARMOUR|TYPE_FEET|TYPE_HEAD, 1, 1], 
			 ["Feather Feet",           5, 4, lambda x: 5+(x-1)*6,     lambda x: 15+(x-1)*6,  TYPE_FEET,                       0, 2], 
			 ["Blast Protection",       2, 4, lambda x: 5+(x-1)*8,     lambda x: 17+(x-1)*8,  TYPE_ARMOUR|TYPE_FEET|TYPE_HEAD, 1, 3], 
			 ["Projectile Protection",  5, 4, lambda x: 3+(x-1)*6,     lambda x: 18+(x-1)*6,  TYPE_ARMOUR|TYPE_FEET|TYPE_HEAD, 1, 4], 
			 ["Respiration",            2, 3, lambda x: 10*x,          lambda x: 10*x+30,     TYPE_HEAD, 0, 5], 
			 ["Aqua Affinity",          2, 1, lambda x: 1,             lambda x: 41,          TYPE_HEAD, 0, 6], 
				 
			 ["Sharpness",             10, 5, lambda x: 1+(x-1)*16,    lambda x: 21+(x-1)*16, TYPE_WEAPON, 2, 7],
			 ["Smite",                  5, 5, lambda x: 5+(x-1)*8,     lambda x: 25+(x-1)*8,  TYPE_WEAPON, 2, 8],
			 ["Bane Of Arthropods",     5, 5, lambda x: 5+(x-1)*8,     lambda x: 25+(x-1)*8,  TYPE_WEAPON, 2, 9],
			 ["Knockback",              5, 2, lambda x: 5+(x-1)*20,    lambda x: 55+(x-1)*20, TYPE_WEAPON, 0, 10],
			 ["Fire Aspect",            2, 2, lambda x: 10+(x-1)*20,   lambda x: 60+(x-1)*20, TYPE_WEAPON, 0, 11],
			 ["Looting",                2, 3, lambda x: 20+(x-1)*12,   lambda x: 70+(x-1)*12, TYPE_WEAPON, 0, 12],
			 
			 ["Efficiency",            10, 5, lambda x: 1+(x-1)*15,    lambda x: 51+(x-1)*15, TYPE_TOOL, 0, 13],
			 ["Silk Touch",             1, 1, lambda x: 25,            lambda x: 75,          TYPE_TOOL, 3, 14],
			 ["Unbreaking",             5, 3, lambda x: 5+(x-1)*10,    lambda x: 55+(x-1)*10, TYPE_TOOL, 0, 15],
			 ["Fortune",                2, 3, lambda x: 20+(x-1)*12,   lambda x: 70+(x-1)*12, TYPE_TOOL, 3, 16],
			 
			 ["Power",                 10, 5, lambda x: 1+(x-1)*10,    lambda x: 16+(x-1)*10, TYPE_BOW, 0, 17],
			 ["Punch",                  2, 2, lambda x: 12+(x-1)*20,   lambda x: 37+(x-1)*20, TYPE_BOW, 0, 18],
			 ["Flame",                  2, 1, lambda x: 20,            lambda x: 50,          TYPE_BOW, 0, 19],
			 ["Infinity",               1, 1, lambda x: 20,            lambda x: 50,          TYPE_BOW, 0, 20],
			 ]
	elif MODEL == 13:
		MAX_LEVEL = 30
		XP_PER_MOB = 5
		
		def xp_for_level(lvl):
			if lvl <= 1:
				return 17
			elif lvl <= 16:
				return xp_for_level(lvl - 1) + 17
			else:
				return xp_for_level(lvl - 1) + 17 + (lvl - 16) * 3
	
		TOOL_ENCHANTABILITY = [ -1, -1, 7, 11, 5, 7, 2 ]
		WEAPON_ENCHANTABILITY = TOOL_ENCHANTABILITY
		ARMOUR_ENCHANTABILITY = [ 7, 6, 4, 12, 5, -1, -1 ]
		BOW_ENCHANTABILITY = [ -1, -1, -1, -1, -1, 0, -1]
		ENCHANTABILITY = { TYPE_ARMOUR: ARMOUR_ENCHANTABILITY, 
						   TYPE_FEET: ARMOUR_ENCHANTABILITY,
						   TYPE_HEAD: ARMOUR_ENCHANTABILITY,
						   TYPE_WEAPON: WEAPON_ENCHANTABILITY,
						   TYPE_TOOL: TOOL_ENCHANTABILITY,
						   TYPE_BOW: BOW_ENCHANTABILITY,
						 }
		ENCHANTABILITY_RANGE=0.15
		
		# name, weight, maxlevel, minpoints, maxpoints, types, exclusion group, index
		ENCH = [ ["Protection",        10, 4, lambda x: 1+(x-1)*11,    lambda x: 21+(x-1)*11, TYPE_ARMOUR|TYPE_FEET|TYPE_HEAD, 1, 0], 
			 ["Fire Protection",        5, 4, lambda x: 10+(x-1)*8,    lambda x: 22+(x-1)*8,  TYPE_ARMOUR|TYPE_FEET|TYPE_HEAD, 1, 1], 
			 ["Feather Feet",           5, 4, lambda x: 5+(x-1)*6,     lambda x: 15+(x-1)*6,  TYPE_FEET,                       0, 2], 
			 ["Blast Protection",       2, 4, lambda x: 5+(x-1)*8,     lambda x: 17+(x-1)*8,  TYPE_ARMOUR|TYPE_FEET|TYPE_HEAD, 1, 3], 
			 ["Projectile Protection",  5, 4, lambda x: 3+(x-1)*6,     lambda x: 18+(x-1)*6,  TYPE_ARMOUR|TYPE_FEET|TYPE_HEAD, 1, 4], 
			 ["Respiration",            2, 3, lambda x: 10*x,          lambda x: 10*x+30,     TYPE_HEAD, 0, 5], 
			 ["Aqua Affinity",          2, 1, lambda x: 1,             lambda x: 41,          TYPE_HEAD, 0, 6], 
			 
			 ["Sharpness",             10, 5, lambda x: 1+(x-1)*11,    lambda x: 21+(x-1)*11, TYPE_WEAPON, 2, 7],
			 ["Smite",                  5, 5, lambda x: 5+(x-1)*8,     lambda x: 25+(x-1)*8,  TYPE_WEAPON, 2, 8],
			 ["Bane Of Arthropods",     5, 5, lambda x: 5+(x-1)*8,     lambda x: 25+(x-1)*8,  TYPE_WEAPON, 2, 9],
			 ["Knockback",              5, 2, lambda x: 5+(x-1)*20,    lambda x: 55+(x-1)*20, TYPE_WEAPON, 0, 10],
			 ["Fire Aspect",            2, 2, lambda x: 10+(x-1)*20,   lambda x: 60+(x-1)*20, TYPE_WEAPON, 0, 11],
			 ["Looting",                2, 3, lambda x: 15+(x-1)*9,    lambda x: 65+(x-1)*9,  TYPE_WEAPON, 0, 12],
			 
			 ["Efficiency",            10, 5, lambda x: 1+(x-1)*10,    lambda x: 51+(x-1)*10, TYPE_TOOL, 0, 13],
			 ["Silk Touch",             1, 1, lambda x: 15,            lambda x: 65,          TYPE_TOOL, 3, 14],
			 ["Unbreaking",             5, 3, lambda x: 5+(x-1)*8,     lambda x: 55+(x-1)*8,  TYPE_TOOL, 0, 15],
			 ["Fortune",                2, 3, lambda x: 15+(x-1)*9,    lambda x: 65+(x-1)*9,  TYPE_TOOL, 3, 16],
			 
			 ["Power",                 10, 5, lambda x: 1+(x-1)*10,    lambda x: 16+(x-1)*10, TYPE_BOW, 0, 17],
			 ["Punch",                  2, 2, lambda x: 12+(x-1)*20,   lambda x: 37+(x-1)*20, TYPE_BOW, 0, 18],
			 ["Flame",                  2, 1, lambda x: 20,            lambda x: 50,          TYPE_BOW, 0, 19],
			 ["Infinity",               1, 1, lambda x: 20,            lambda x: 50,          TYPE_BOW, 0, 20],
			 ]
       

def name(e):
	""" returns an enchantment's name """
	return e[0]

def weight(e):
	""" returns an enchantment's weight for choosing enchantments """
	return e[1]
	
def maxlevel(e):
	""" returns an enchantment's maximum level """
	return e[2]
	
def minpoints(e, level):
	""" returns an enchantment's minimum modified enchantment level for a given enchantment level """
	return e[3](level)

def maxpoints(e, level):
	""" returns an enchantment's maximum modified enchantment level for a given enchantment level """
	return e[4](level)
	
def isokfor(e, type):
	""" checks if an enchantment can be applied to a given item type """
	return (e[5] & type) > 0
	
def excludes(e1, e2):
	""" checks if two enchantments cannot be applied together """
	return (e1 != e2) and (e1[6] == e2[6]) and (e1[6] != 0)
	
def eindex(e):
	""" returns an enchantment's index """
	return e[7]
	
def encode_enchantments(elist):
	""" encodes an enchantment list into a single number """
	value = 0
	sortelist = sorted(elist, key=lambda x: eindex(x[0]))
	
	for x in sortelist:
		value *= 1000
		value += eindex(x[0]) * 10 + x[1]
	return value
	
def decode_enchantments(value):
	""" decodes a single number into an enchantment list """
	result = []
	while value > 0:
		v = value % 1000
		result.append( (ENCH[v / 10], v % 10) )
		value /= 1000
	return result

def prob_baselevel(baselevel, destlevel, enchantability):
	"""
	given the enchanting level (baselevel) and the item's enchantability
	this funciton calculates the probability, that a given modified
	enchanting level (destlevel) can be reached
	"""
	n = enchantability / 2 + 1
	x = destlevel - baselevel - 1
	if x < 0 or x > 2 * (n-1):
		return 0
	if x < n:
		return Fraction(x + 1) / (n*n)
	else:
		return Fraction(2*n - 1 - x) / (n*n)

def prob_factor_below(x):
	""" 
	calculates the probability of a value being below a given value in a pyramidical
	distribution between 1-ENCHANTABILITY_RANGE and 1+ENCHANTABILITY_RANGE 
	"""
	if x < (1-ENCHANTABILITY_RANGE):
		return Fraction(0)
	elif x > (1+ENCHANTABILITY_RANGE):
		return Fraction(1)
	elif x <= 1:
		return 8 * (x - Fraction(1-ENCHANTABILITY_RANGE)) * (x - Fraction(1-ENCHANTABILITY_RANGE))
	else:
		return 1 - 8 * (Fraction(1+ENCHANTABILITY_RANGE) - x) * (Fraction(1+ENCHANTABILITY_RANGE) - x)
		
def prob_factor_between(minfactor, maxfactor):
	"""
	calculates the probability of a value being in a given range in a pyramidical
	distribution between 1-ENCHANTABILITY_RANGE and 1+ENCHANTABILITY_RANGE 
	"""
	minf = max(minfactor, 1-ENCHANTABILITY_RANGE)
	maxf = min(maxfactor, 1+ENCHANTABILITY_RANGE)
	return prob_factor_below(maxf) - prob_factor_below(minf)

def rec_calc_probabilities(alreadyenchantments, enchantments, restmodlevel):
	"""
	recursive enchantment calculation function
	
	given a list of existing enchantments, a list of possible enchantments and
	the modified enchantment level this recursively calculates all possible
	enchantments and their probabilities
	"""
	global MODEL
	
	result = {}
	enchantmentsum = reduce(lambda x,y: x+y, map(weight, map(lambda x: x[0], enchantments)))
	if MODEL==12:
		newmodlevel = restmodlevel / 2
	elif MODEL==13:
		newmodlevel = restmodlevel
	probkeepgoing = Fraction((newmodlevel + 1), 50)
	
	for ench in enchantments:
		eprob = Fraction(weight(ench[0]), enchantmentsum)
		newenchantments = alreadyenchantments + [ench,]
		newpossenchantments = []
		for e2 in enchantments:
			if ench != e2 and (not excludes(e2[0], ench[0])):
				newpossenchantments.append(e2)
						
		if len(newpossenchantments) > 0:
			result[encode_enchantments(newenchantments)] = (1 - probkeepgoing) * eprob
			if MODEL==12:
				moreprobs = rec_calc_probabilities(newenchantments, newpossenchantments, newmodlevel)
			elif MODEL==13:
				moreprobs = rec_calc_probabilities(newenchantments, newpossenchantments, newmodlevel/2)
			for encoded, prob in moreprobs.items():
				if encoded not in result:
					result[encoded] = prob * eprob * probkeepgoing
				else:
					result[encoded] += prob * eprob * probkeepgoing
		else:
			result[encode_enchantments(newenchantments)] = eprob
					
	return result

def calc(materialnamestr, itemtypestr, level, db=None):
	"""
	main calculation function
	
	given the command line parameters this calculates and prints the enchantment probabilities
	"""
	
	# First evaluate the parameters
	material = MATERIAL_NAMES.index(materialnamestr)
	itemtype = -1
	for type, typename in TYPE_NAMES.items():
		if typename == itemtypestr:
			itemtype = type
			break
	
	enchantability = ENCHANTABILITY[itemtype][material]
	if enchantability == -1:
		print("This item/material combination does not exist.")
		return
	
	# Calculate the probabilities of all modified enchanting levels
	minbaselevel = int(level + 1)
	maxbaselevel = int(level + 1 + 2 * (enchantability / 2))
	baselevels = {}
	for baselevel in range(minbaselevel,maxbaselevel+1):
		baselevels[baselevel] = prob_baselevel(level, baselevel, enchantability)
		
	# Now recalculate all modified enchanting level probabilities as they
	# are again modified by multiplying with a random number in the range of
	# 1-ENCHANTABILITY_RANGE...1+ENCHANTABILITY_RANGE
	minmodlevel = int(minbaselevel * (1-ENCHANTABILITY_RANGE))
	maxmodlevel = int(maxbaselevel * (1+ENCHANTABILITY_RANGE)) + 1
	modlevels = {}
	for modlevel in range(minmodlevel, maxmodlevel+1):
		r = 0
		for baselevel in range(minbaselevel, maxbaselevel+1):
			r += baselevels[baselevel] * prob_factor_between( (modlevel - Fraction(0.5)) / baselevel, (modlevel + Fraction(0.5)) / baselevel)
		modlevels[modlevel] = r
	
	# Keys: [ (ench-idx, level), (ench-idx, level), ... ]
	finalprobabilities = {}	
	
	# Calculate all enchantment probabilities by going over all possible modified enchantming levels
	for modlevel, modlevelprob in modlevels.items():
		possibleenchantments = []
		# Select the possible enchantments for this modified enchanting level
		for ench in ENCH:
			if not isokfor(ench, itemtype):
				continue
			for slevel in range(maxlevel(ench), 0, -1):
				if maxpoints(ench, slevel) >= modlevel and minpoints(ench, slevel) <= modlevel:
					possibleenchantments.append([ench, slevel])
					break

		if len(possibleenchantments) == 0:
			continue					
		
		# recursively calculate the probabilities and save them for later
		probs = rec_calc_probabilities([], possibleenchantments, modlevel)
		sum = 0
		for code, prob in probs.items():
			if code not in finalprobabilities:
				finalprobabilities[code] = modlevelprob * prob
			else:
				finalprobabilities[code] += modlevelprob * prob
			
	# Finally calculate the summarized probabilities
	# - enchantments per level / class
	# - number of enchantments in total
	probperenchantmentlevel = {}
	probperenchantment = {}
	probpernum = {}
	
	for code, prob in finalprobabilities.items():
		val = code
		while val > 0:
			v = val % 1000
			ench = decode_enchantments(v)[0][0]
			if eindex(ench) not in probperenchantment:
				probperenchantment[eindex(ench)] = prob
			else:
				probperenchantment[eindex(ench)] += prob
			if v not in probperenchantmentlevel:
				probperenchantmentlevel[v] = prob
			else:
				probperenchantmentlevel[v] += prob
			val /= 1000
	
		count = int(math.log10(code)) / 3 + 1
		if count not in probpernum:
			probpernum[count] = prob
		else:
			probpernum[count] += prob
	
	# Print the whole thing to the console
	print("------------")
	print("Probabilities detailed:")
	print("------------")
	for code, prob in sorted(finalprobabilities.items(), key = lambda x: 1 - x[1]):
		enchantments = decode_enchantments(code)
		enchstr = ""
		for ench in sorted(enchantments, key = lambda x: name(x[0])):
			if len(enchstr) > 0:
				enchstr += ", "	
			enchstr += name(ench[0]) + " " + ROMANS[ench[1]]
		print("%5.2f%% %s" % (prob * 100, enchstr))
		
	print("------------")
	print("Probabilities per enchantment:")
	print("------------")
	for code, prob in sorted(probperenchantmentlevel.items(), key = lambda x: 1 - x[1]):
		ench = decode_enchantments(code)[0]
		print("%5.2f%% %s %s" % (prob * 100, name(ench[0]), ROMANS[ench[1]]))
	
	print("------------")
	print("Probabilities per enchantment class:")
	print("------------")
	for index, prob in sorted(probperenchantment.items(), key = lambda x: 1- x[1]):
		print("%5.2f%% %s" % (prob * 100, name(ENCH[index])))

	print("------------")
	print("Number of enchantments")
	print("------------")
	for count, prob in sorted(probpernum.items(), key = lambda x: x[0]):
		print("%d: %5.2f%%" % (count, prob * 100))

def main():
	global MODEL
	
	if len(sys.argv) == 5:
		MODEL = int(sys.argv[1])
		load_model()
		calc(sys.argv[2], sys.argv[3], int(sys.argv[4]))
	else:
		print("Usage: %s MODEL MATERIAL ITEMTYPE LEVEL" % sys.argv[0])
		print()
		print("MODEL      either 12 (for Minecraft 1.2 and prior) or 13 (for Minecraft 1.3.1 and later)")
		print("MATERIAL   the item's material, can be one of: %s" % (", ".join(MATERIAL_NAMES)))
		print("ITEMTYPE   the item type, can be one of: %s" % (", ".join(TYPE_NAMES.values())))
		print("LEVEL      the enchanting level available")
				
if __name__ == "__main__":
	main()