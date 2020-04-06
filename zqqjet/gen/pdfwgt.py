import os
import sys
import math
import pickle
import json
import time
import numexpr
import array
import uproot
import awkward
import numpy as np
from coffea import hist
from coffea import lookup_tools
from coffea import util
from coffea.analysis_objects import JaggedCandidateArray
from nanoindex.nanogen.index import index
from pprint import pprint

datasets = ["WJetsToQQ", "WJetsToQQ_pdfwgt"]
subdatasets = {
	"WJetsToQQ": ["WJetsToQQ_HT800toInf", "WJetsToQQ_HT600to800", "WJetsToQQ_HT400to600"],
	"WJetsToQQ_pdfwgt": ["WJetsToQQ_pdfwgt_HT800toInf", "WJetsToQQ_pdfwgt_HT600to800", "WJetsToQQ_pdfwgt_HT400to600"],
}

xses = {
	"WJetsToQQ_pdfwgt_HT800toInf": 32.98649999999999,
	"WJetsToQQ_pdfwgt_HT600to800": 67.08899999999998,
	"WJetsToQQ_HT800toInf": 28.652499999999996,
	"WJetsToQQ_HT600to800": 59.333499999999994,
	"WJetsToQQ_pdfwgt_HT400to600": 311.825,
	"WJetsToQQ_HT400to600": 279.79,
}
normalizations = {}
nevents = {}
for dataset in datasets:
	for subdataset in subdatasets[dataset]:
		nevents[subdataset] = 0
		files = index[subdataset]
		for file in files:
			#print(file)
			tree = uproot.open(file)["Events"]
			nevents[subdataset] += len(tree)
		normalizations[subdataset] = 137. * xses[subdataset] / nevents[subdataset]
pprint(normalizations)


dataset_axis = hist.Cat("dataset", "Primary dataset")
h_zpt = hist.Hist("Events", dataset_axis, hist.Bin("pt", r"Z p_{T} [GeV]", 100, 0., 1000.))
for dataset in datasets:
	for subdataset in subdatasets[dataset]:
		files = index[subdataset]
		for file in files:
			print(file)
			tree = uproot.open(file)["Events"]
			#print(tree.keys())
			branches = tree.arrays(namedecode='utf-8')
			#print(branches["GenPart_pt"])
			#print(branches["GenPart_pdgId"])
			#print(branches["GenPart_status"])
			#print(branches["GenPart_pt"][abs(branches["GenPart_pdgId"]) == 24])
			#print(branches["GenPart_status"][abs(branches["GenPart_pdgId"]) == 24])
			selection = (abs(branches["GenPart_pdgId"]) == 24) & (branches["GenPart_status"] == 62)
			#print(branches["GenPart_pt"][selection])
			h_zpt.fill(dataset=dataset, pt=branches["GenPart_pt"][selection].flatten(), weight=normalizations[subdataset])
util.save(h_zpt, "output.coffea")
