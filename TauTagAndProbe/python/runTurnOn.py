#!/usr/bin/env python3

import ROOT
import argparse
import sys
import re
import numpy as np
from array import array

import math
import os
from tdrstyle import *

from Plothelper import CreateBins,CreateHistograms,CreateMCHistograms,CreateL1Histograms
parser = argparse.ArgumentParser(description='Create turnon curves.')
parser.add_argument('--input_data', required=True, type=str, nargs='+', help="run2022 data")

parser.add_argument('--channel', required=True, type=str, help="ditau,mutau,etau,VBFditau_hi,VBFditau_lo,ditaujet,single_tau")
parser.add_argument('--selection', required=False, type=str,default="DeepTau", help="Tau selection")

parser.add_argument('--output', required=True, type=str, help="output file")
parser.add_argument('--vars', required=True,nargs='+', type=str, help="variable to draw")
parser.add_argument('--L1', required=False,  action='store_true', help="require L1 efficiency")
parser.add_argument('--HLT', required=False,  action='store_true', help="require HLT only efficiency")

args = parser.parse_args()

print(args.vars)

sys.path.insert(0, 'Common/python')
from AnalysisTypes import *
from AnalysisTools import *
import RootPlotting
import TriggerConfig
ROOT.gROOT.SetBatch(True)
ROOT.TH1.SetDefaultSumw2()
RootPlotting.ApplyDefaultGlobalStyle()

trigger_pattern = {"ditau":"HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS35_L2NN_eta2p1_CrossL1_v","mutau":"HLT_IsoMu20_eta2p1_LooseDeepTauPFTauHPS27_eta2p1_CrossL1_v","ditaujet":"HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS30_L2NN_eta2p1_CrossL1_v","VBFditau_hi":"HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS45_L2NN_eta2p1_CrossL1_v","VBFditau_lo":"HLT_IsoMu24_eta2p1_MediumDeepTauPFTauHPS20_eta2p1_SingleL1_v","single_tau":"HLT_IsoMu24_eta2p1_LooseDeepTauPFTauHPS180_eta2p1_v"}


selection_id = ParseEnum(TauSelection, "DeepTau")



n_input = len(args.input_data)


eras = ['B','C','D']
output_file = ROOT.TFile(args.output + '.root', 'RECREATE')

trigger_dict = dict()
hlt_paths = dict()


hist_L3_passed = dict()
hist_L3_total = dict()
eff_L3 = dict()

hist_L1_passed = dict()
hist_L1_total = dict()
eff_L1 = dict()

ROOT.gStyle.SetOptStat(0); ROOT.gStyle.SetTextFont(42)
c = ROOT.TCanvas("c", "", 800, 700)
c.SetGridx();c.SetGridy()
setTDRStyle()
label = ROOT.TLatex(); label.SetNDC(True)
ylabel = ROOT.TLatex(); ylabel.SetNDC(True)
label = ROOT.TLatex(); label.SetNDC(True)

for var in args.vars:
    # use multiplotter for multiple graphs
    mg = ROOT.TMultiGraph("mg", "")
    # legend
    leg = ROOT.TLegend(0.582707, 0.247312, 0.883459, 0.397849)
    leg.SetTextSize(0.025)
    leg.SetTextSize(0.025)
    leg.SetShadowColor(0)
    leg.SetBorderSize(0)
    graphs = {}
    icolor = [1,4,2,8]
    ic = 0
    imaker = 9
    ileg = 0
    for input_era in args.input_data:
        keyname = input_era+'_'+var
        trigger_dict[keyname] = TriggerConfig.LoadTriggerDictionary(input_era)
        hlt_paths[keyname] = TriggerConfig.GetMatchedTriggers(trigger_dict[keyname][0],trigger_pattern[args.channel])
        hist_L1_passed[keyname], hist_L1_total[keyname], eff_L1[keyname] = CreateL1Histograms(input_era, selection_id, hlt_paths[keyname],args.vars,output_file,args.channel)
        hist_L3_passed[keyname], hist_L3_total[keyname], eff_L3[keyname] = CreateHistograms(input_era, selection_id, hlt_paths[keyname],args.vars,output_file,args.channel)
        if args.L1 == True and args.HLT == False:
            graphs[keyname] =  ROOT.TGraphAsymmErrors(hist_L1_passed[keyname][var].GetPtr(),hist_L1_total[keyname][var].GetPtr(), "n")
        elif args.L1 == False and args.HLT == True:
            graphs[keyname] =  ROOT.TGraphAsymmErrors(hist_L3_passed[keyname][var].GetPtr(),hist_L1_passed[keyname][var].GetPtr(), "n")
        else:
            graphs[keyname] =  ROOT.TGraphAsymmErrors(hist_L3_passed[keyname][var].GetPtr(),hist_L3_total[keyname][var].GetPtr(), "n")
        graphs[keyname].SetLineColor(icolor[ic])
        graphs[keyname].SetMarkerStyle(imaker)
        graphs[keyname].SetLineWidth(3)
        graphs[keyname].SetMarkerSize(1.5)
        ic = ic + 1
        #imaker = imaker + 1
    
        legname = ["Run 2022","Run 2023B","Run 2023C","Run 2023D"]
        leg.AddEntry(graphs[keyname],legname[ileg])
        print('Drawing {}'.format(legname[ileg]))
        mg.Add(graphs[keyname])
        ileg = ileg+1

        
    mg.GetYaxis().SetRangeUser(0,1)
    mg.GetYaxis().SetNdivisions(5)
    mg.GetXaxis().SetLabelSize(0.04)
    mg.GetYaxis().SetLabelSize(0.04)
    #mg.GetYaxis().SetTitle("L1 + HLT Efficiency")
    if args.channel == "single_tau" and var == "tau_pt":
        mg.GetXaxis().SetRangeUser(50,500)
    mg.Draw("AP")

    if args.L1 == True and args.HLT == False:
        ylabel.SetTextAngle(90);ylabel.SetTextSize(0.0414815);ylabel.DrawLatex(0.035,0.422222, "L1 Efficiency")
    elif args.L1 == False and args.HLT == True:
        ylabel.SetTextAngle(90);ylabel.SetTextSize(0.0414815);ylabel.DrawLatex(0.035,0.422222, "HLT Efficiency")
    else:
        ylabel.SetTextAngle(90);ylabel.SetTextSize(0.0414815);ylabel.DrawLatex(0.035,0.422222, "L1 + HLT Efficiency")
    if args.channel == "VBFditau_lo" and args.L1 == False:
        ylabel.SetTextAngle(90);ylabel.SetTextSize(0.0414815);ylabel.DrawLatex(0.035,0.422222, "HLT Efficiency")
    if(var == "tau_pt"):
        label.SetTextSize(0.0414815);label.DrawLatex(0.67,0.0192593, "Offline p_{T}^{#tau} [GeV]")
        label.SetTextSize(0.040); label.DrawLatex(0.100, 0.920, "#bf{CMS} #it{Preliminary}")
        
    elif(var== "npu" or var == "npv"):
        label.SetTextSize(0.0414815);label.DrawLatex(0.197995,0.0122888, "number of offline reconstructed primary vertices")
        label.SetTextSize(0.040); label.DrawLatex(0.100, 0.920, "#bf{CMS} #it{Preliminary}")
    else:
        label.SetTextSize(0.0414815);label.DrawLatex(0.67,0.0192593, "Offline #eta^{#tau}")
        label.SetTextSize(0.040); label.DrawLatex(0.100, 0.920, "#bf{CMS} #it{Preliminary}")
        #label.SetTextSize(0.030); label.DrawLatex(0.63, 0.912593, "34.3 fb^{-1} (13.6 TeV, 2022)")
        
    if args.channel == 'ditau':
        label.DrawLatex(0.358396,0.434074, "#bf{Double-#tau_{h} trigger performance}")
    elif args.channel == 'mutau':
        label.DrawLatex(0.358396,0.434074, "#bf{#mu#tau_{h} trigger performance}")
    elif args.channel == 'etau':
        label.DrawLatex(0.358396,0.434074, "#bf{e#tau_{h} trigger performance}")
    elif args.channel == 'single_tau':
        label.DrawLatex(0.358396,0.434074, "#bf{Single-#tau_{h} trigger performance}")
    elif args.channel == "VBFditau_hi" or args.channel == "VBFditau_lo":
        label.DrawLatex(0.358396,0.434074, "#bf{VBF di-#tau_{h} trigger performance}")
    else:
        label.DrawLatex(0.358396,0.434074, "#bf{di-#tau_{h} +jets trigger performance}")
    if var == "tau_eta":
        #print("Medium tauID, #tau_ > {} GeV".format(eta_th[args.channel]))
        label.DrawLatex(0.305764,0.183704, "Offline tauID applied at Medium WP")
    elif var == "npv":
        label.DrawLatex(0.305764,0.183704,"Offline tauID applied at Medium WP" )
    else:
        label.DrawLatex(0.305764,0.183704, "Offline tauID applied at Medium WP")
    leg.Draw()
    if args.L1 == True and args.HLT == False:
        pname = args.output+'_'+args.channel+'_'+var+'_L1'
    elif args.L1 == False and args.HLT == True:
        pname = args.output+'_'+args.channel+'_'+var+'_HLT'
    else:
        pname = args.output+'_'+args.channel+'_'+var
    plot_pdf_name = pname+'.pdf'
    plot_png_name = pname+'.png'
    cfg_name = pname+'.C'
    c.SaveAs('./newDP/{}'.format(plot_pdf_name))
    c.SaveAs('./newDP/{}'.format(plot_png_name))
    c.SaveAs('./newDP/{}'.format(cfg_name))
    
    print('TurnOn is created')


