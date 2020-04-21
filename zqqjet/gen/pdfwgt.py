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
import coffea.processor as processor
from nanoindex.nanogen.index import index
from pprint import pprint

process = False
plot = True

datasets = ["WJetsToQQ", "WJetsToQQ_pdfwgt"]
subdatasets = {
	"WJetsToQQ": ["WJetsToQQ_HT800toInf", "WJetsToQQ_HT600to800", "WJetsToQQ_HT400to600"],
	"WJetsToQQ_pdfwgt": ["WJetsToQQ_pdfwgt_HT800toInf", "WJetsToQQ_pdfwgt_HT600to800", "WJetsToQQ_pdfwgt_HT400to600"],
}

def delta_phi(phi1, phi2):
    return (phi1 - phi2 + math.pi) % (2*math.pi) - math.pi

def delta_r(eta1, eta2, phi1, phi2):
    return ((eta1 - eta2)**2 + delta_phi(phi1, phi2)**2)**0.5

def where(predicate, iftrue, iffalse):
    predicate = predicate.astype(np.bool)   # just to make sure they're 0/1
    return predicate*iftrue + (1 - predicate)*iffalse


if process:
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
	output = processor.dict_accumulator()
	output["h_zpt"] = hist.Hist("Events", dataset_axis, hist.Bin("pt", r"Z p_{T} [GeV]", 100, 0., 1000.))
	output["h_genjetAK8_mass"] = hist.Hist("Events", dataset_axis, hist.Bin("m", r"GenJetAK8 mass [GeV]", 100, 50., 150.))

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
				output["h_zpt"].fill(dataset=dataset, pt=branches["GenPart_pt"][selection].flatten(), weight=normalizations[subdataset])

				# Gen Z boson eta and phi. Assume there's exactly 1 per event.
				event_Z_eta = branches["GenPart_eta"][selection]
				event_Z_eta = where(event_Z_eta.count() >= 1, event_Z_eta[0], 1.e20)
				event_Z_phi = branches["GenPart_phi"][selection]
				event_Z_phi = where(event_Z_phi.count() >= 1, event_Z_eta[0], 1.e20)

				# Match gen jets to Z
				genjetAK8_match = delta_r(branches["GenJetAK8_eta"], event_Z_eta, branches["GenJetAK8_phi"], event_Z_phi) < 0.8
				output["h_genjetAK8_mass"].fill(dataset=dataset, m=branches["GenJetAK8_mass"][genjetAK8_match].flatten())

	util.save(output, "output.coffea")

if plot:
	print("Importing matplotlib")
	import matplotlib.pyplot as plt
	print("Loading histograms")
	stuff = util.load("output.coffea")

	print("Rebinning")
	stuff["h_zpt"] = stuff["h_zpt"].rebin("pt", 5)

	print("Making subplots")
	fig1, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))

	print("Plotting top")
	hist.plot1d(stuff["h_zpt"], overlay="dataset", ax=ax1)
	print("Styling top")
	ax1.set_xlim(0., 1000.)
	ax1.set_ylim(0.1, 100000.)
	ax1.set_yscale("log")

	print("Integrating for ratio")
	h_zpt_pdfwgtT = stuff["h_zpt"].integrate("dataset", ("WJetsToQQ_pdfwgt"))
	h_zpt_pdfwgtF = stuff["h_zpt"].integrate("dataset", ("WJetsToQQ"))

	print("Plotting bottom")
	hist.plotratio(h_zpt_pdfwgtT, h_zpt_pdfwgtF, ax=ax2, unc="poisson-ratio", error_opts={'color': 'blue', 'marker': '.'}, guide_opts={'xmin': 0., 'xmax': 1000.})
	ax2.set_xlim(0., 1000.)
	plt.tight_layout()
	print("Saving")
	fig1.savefig("pdfwgt_Vpt.png")


	fig2, ax = plt.subplots()
	hist.plot1d(stuff["h_genjetAK8_mass"], overlay="dataset", ax=ax)
	fig2.savefig("pdfwgt_genjetAK8mass.png")

