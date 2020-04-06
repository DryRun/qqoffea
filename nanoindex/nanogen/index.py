import os
import sys
import glob

nanogen_dir = os.path.dirname(os.path.abspath(__file__))
nanogen_filelists = {
	"WJetsToQQ_pdfwgt_HT800toInf": f"{nanogen_dir}/files_WJetsToQQ_pdfwgt_HT800toInf.dat",
	"WJetsToQQ_pdfwgt_HT600to800": f"{nanogen_dir}/files_WJetsToQQ_pdfwgt_HT600to800.dat",
	"WJetsToQQ_pdfwgt_HT400to600": f"{nanogen_dir}/files_WJetsToQQ_pdfwgt_HT400to600.dat",
	"WJetsToQQ_HT800toInf": f"{nanogen_dir}/files_WJetsToQQ_HT800toInf.dat",
	"WJetsToQQ_HT600to800": f"{nanogen_dir}/files_WJetsToQQ_HT600to800.dat",
	"WJetsToQQ_HT400to600": f"{nanogen_dir}/files_WJetsToQQ_HT400to600.dat",
}
index = {}
for sample, filelist_path in nanogen_filelists.items():
	index[sample] = []
	with open(filelist_path, 'r') as filelist:
		for line in filelist:
			index[sample].append(line.rstrip())

if __name__ == "__main__":
	from pprint import pprint
	pprint(index)