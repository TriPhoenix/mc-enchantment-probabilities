mc-enchantment-probabilities
============================

Python2-based calculator for enchantment probabilities in Minecraft, the popular Swedish block-based sandbox game.

Overview
--------

This tool is intended to calculate enchantment probabilities for the various types of items in Minecraft. It takes the item type, the item's material and a designated enchantment level and gives you a table of possible enchantments. As the enchantment system changed rather drastically from Minecraft 1.2 and prior to Minecraft 1.3.1 and later, it allows you to choose between different enchantment models.

This release is under GPLv3.

Usage
-----
<pre>
Usage: enchantingprobs.py MODEL MATERIAL ITEMTYPE LEVEL

MODEL      either 12 (for Minecraft 1.2 and prior) or 13 (for Minecraft 1.3.1 and later)
MATERIAL   the item's material, can be one of: leather, chain, iron, gold, diamond, wood, stone
ITEMTYPE   the item type, can be one of: bow, armour, boots, helmet, sword, tool
LEVEL      the enchanting level available
</pre>

Example
-------
This example calculates the probabilities for a diamond tool (pickaxe, shovel, axe) in Minecraft 1.3 while using a level 30 enchantment.

<pre>
$ python2 enchantingprobs.py 13 diamond tool 30
------------
Probabilities detailed:
------------
23.70% Efficiency IV, Unbreaking III
16.60% Efficiency IV
10.46% Efficiency IV, Fortune III, Unbreaking III
 8.89% Unbreaking III
 7.49% Efficiency IV, Silk Touch I, Unbreaking III
 6.10% Efficiency IV, Fortune III
 4.52% Efficiency IV, Fortune II, Unbreaking III
 4.50% Efficiency IV, Silk Touch I
 2.89% Efficiency IV, Fortune II
 2.29% Fortune III, Unbreaking III
 2.12% Fortune III
 1.78% Silk Touch I
 1.78% Silk Touch I, Unbreaking III
 1.44% Fortune II
 1.27% Efficiency III, Unbreaking III
 1.26% Fortune II, Unbreaking III
 1.17% Efficiency III
 0.68% Efficiency III, Fortune II, Unbreaking III
 0.48% Efficiency III, Fortune II
 0.34% Efficiency III, Silk Touch I, Unbreaking III
 0.24% Efficiency III, Silk Touch I
 0.00% Efficiency V
 0.00% Efficiency V, Fortune III, Unbreaking III
 0.00% Efficiency V, Silk Touch I, Unbreaking III
 0.00% Efficiency V, Silk Touch I
 0.00% Efficiency V, Unbreaking III
 0.00% Efficiency V, Fortune III
------------
Probabilities per enchantment:
------------
76.27% Efficiency IV
62.67% Unbreaking III
20.97% Fortune III
16.12% Silk Touch I
11.27% Fortune II
 4.18% Efficiency III
 0.00% Efficiency V
------------
Probabilities per enchantment class:
------------
80.45% Efficiency
62.67% Unbreaking
32.25% Fortune
16.12% Silk Touch
------------
Number of enchantments
------------
1: 32.00%
2: 44.51%
3: 23.49%
</pre>

Thanks
------

Thanks go to

* <a href="http://mojang.com">Mojang</a> for creating a great game
* The <a href="http://www.minecraftwiki.net/wiki/Enchantment_Mechanics">Minecraft Wiki page on Enchantment Mechanics</a> to give a good overview and guideline
* The <a href="http://mcp.ocean-labs.de/index.php/MCP_Releases">Minecraft Code Pack</a> team to allow insights that would not have been easily obtainable otherwise
 