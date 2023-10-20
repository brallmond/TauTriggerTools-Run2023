import ROOT
import numpy as np
import sys
import re
import numpy as np
from array import array
import os 
import sys

path_prefix = '' if 'TauTriggerTools' in os.getcwd() else 'TauTriggerTools/'
sys.path.insert(0, path_prefix + 'Common/python')

ROOT.gInterpreter.Declare('#include "{}TauTagAndProbe/interface/PyInterface.h"'.format(path_prefix))
def CreateBins(var_name,singleTau=False):
    if var_name in [ 'tau_pt' ]:
        bins = np.arange(20, 40, step=4)
        #bins = np.append(bins, np.arange(40, 120, step=4))
        high_pt_bins = [ 40,50, 70, 150]
        if singleTau:
            high_pt_bins = [50,70,90,120,150,200,250,500]
        bins = np.append(bins,high_pt_bins)
        return bins,False,False
    elif var_name in [ 'jet_pt']:
        bins = np.arange(20, 70, step=4)
        #bins = np.append(bins, np.arange(40, 120, step=4))
        high_pt_bins = [ 70,80,100,120, 150]
        bins = np.append(bins,high_pt_bins)
        return bins,False,False
    elif var_name in [ 'tau_eta', 'tau_gen_vis_eta' ]:
        return np.linspace(-2.3, 2.3, 7), False, False
    elif var_name in [ 'npu', 'npv' ]:
        return np.linspace(0, 80, 6), False, False
    raise RuntimeError("Can't find binning for \"{}\"".format(var_name))

def CreateHistograms(input_file, selection_id, hlt_paths, vars, output_file,ch):
    df = ROOT.RDataFrame('events',input_file)
    eta_th = {"ditau":45,"mutau":30,"etau":30,"single_tau":180,"ditaujet":45,"VBFditau_lo":30,"VBFditau_hi":47}
    if ch == "VBFditau_lo":
        df = df.Filter('(tau_sel & {}) != 0  && muon_pt > 27 && muon_iso < 0.1 && muon_mt < 30 && tau_decayMode != 5 && tau_decayMode != 6 && abs(tau_eta) < 2.3 && tau_pt > 5 && vis_mass > 40 && vis_mass < 80'.format(selection_id))
    elif ch == "etau":
        df = df.Filter('(tau_sel & {}) != 0  && muon_pt > 27 && muon_iso < 0.1 && muon_mt < 30 && tau_decayMode != 5 && tau_decayMode != 6 && abs(tau_eta) < 2.3 && tau_pt > 20 && vis_mass > 40 && vis_mass < 80'.format(selection_id))
    elif ch == "single_tau":
        #df = df.Filter('(tau_sel & {}) != 0  && muon_pt > 27 && muon_iso < 0.1 && muon_mt < 30 && tau_decayMode != 5 && tau_decayMode != 6 && abs(tau_eta) < 2.3 && tau_pt > 20 && vis_mass > 40 && vis_mass < 80'.format(selection_id))
        df = df.Filter('(tau_sel & {}) != 0  && muon_pt > 27 && muon_iso < 0.1 && muon_mt < 30 && tau_decayMode != 5 && tau_decayMode != 6 && abs(tau_eta) < 2.3 && tau_pt > 20'.format(selection_id))
    elif ch == "ditaujet":
        df = df.Filter('(tau_sel & {}) != 0 && muon_pt > 27 && muon_iso < 0.1 && muon_mt < 30 && tau_decayMode != 5 && tau_decayMode != 6 && abs(tau_eta) < 2.3 && tau_pt > 20 && vis_mass > 40 && vis_mass < 80'.format(selection_id))
    elif ch == "VBFditau_lo":
        df = df.Filter('(tau_sel & {}) != 0  && muon_pt > 27 && muon_iso < 0.1 && muon_mt < 30 && tau_decayMode != 5 && tau_decayMode != 6 && abs(tau_eta) < 2.3 && tau_pt > 20 && vis_mass > 40 && vis_mass < 80'.format(selection_id))
    elif ch == "VBFditau_hi":
        df = df.Filter('(tau_sel & {}) != 0  && muon_pt > 27 && muon_iso < 0.1 && muon_mt < 30 && tau_decayMode != 5 && tau_decayMode != 6 && abs(tau_eta) < 2.3 && tau_pt > 20 && vis_mass > 40 && vis_mass < 80'.format(selection_id))
    else:
        df = df.Filter('(tau_sel & {}) != 0  && muon_pt > 27 && muon_iso < 0.1 && muon_mt < 30 && tau_decayMode != 5 && tau_decayMode != 6 && abs(tau_eta) < 2.3 && tau_pt > 20 && vis_mass > 40 && vis_mass < 80'.format(selection_id))
        #print("In Data after preselection ",df.Histo1D(hist_model,var).GetEntries())
    
    
    df = df.Filter('(byDeepTau2017v2p1VSmu & (1 << 5)) != 0 && (byDeepTau2017v2p1VSjet & (1 << 4)) != 0')

    hist_total,hist_pass,eff = dict(),dict(),dict()
    bool_singletau = False
    if ch == "single_tau":
        bool_singletau =True
    for var in vars:
        bins, x_scales, divide_by_bw = CreateBins(var,bool_singletau)
        hist_model = ROOT.RDF.TH1DModel(var, var, len(bins) - 1, array('d', bins))
        if var == 'tau_eta' or var == 'npv' or var == 'tau_phi':
            df = df.Filter('tau_pt > {}'.format(eta_th[ch]))
        match_mask = 0
        for path_name, path_index in hlt_paths.items():
            match_mask = match_mask | (1 << path_index)
    
        hist_total[var] = df.Histo1D(hist_model,var)
        if ch == 'VBFditau_hi':
            hist_pass[var]  = df.Filter('(hlt_acceptAndMatch & {}) != 0 && l1Tau_pt >= 45 && l1Tau_hwIso > 0'.format(match_mask)).Histo1D(hist_model, var)
        elif ch == 'etau' or ch == 'ditaujet':
            hist_pass[var]  = df.Filter('(hlt_acceptAndMatch & {}) != 0 && l1Tau_hwIso > 0 && l1Tau_pt >= 26'.format(match_mask)).Histo1D(hist_model, var)# && l1Tau_hwIso > 0
        else:
            hist_pass[var]  = df.Filter('(hlt_acceptAndMatch & {}) != 0'.format(match_mask)) \
                    .Histo1D(hist_model, var)

        eff[var] = ROOT.TEfficiency(hist_pass[var].GetPtr(), hist_total[var].GetPtr())
        print(hist_total[var].GetPtr().GetEntries())
    return hist_pass,hist_total,eff
        
def CreateMCHistograms(input_file, selection_id, hlt_paths, vars, output_file,ch,pu):
    df = ROOT.RDataFrame('events',input_file)
    eta_th = {"ditau":45,"mutau":30,"etau":30,"single_tau":180,"ditaujet":45,"VBFditau_lo":30,"VBFditau_hi":47}
    if ch == "VBFditau_lo":
        df = df.Filter('(tau_sel & {}) != 0  && muon_pt > 27 && muon_iso < 0.1 && muon_mt < 30 && tau_decayMode != 5 && tau_decayMode != 6 && abs(tau_eta) < 2.3 && tau_pt > 5 && vis_mass > 40 && vis_mass < 80'.format(selection_id))
    elif ch == "etau":
        df = df.Filter('(tau_sel & {}) != 0  && muon_pt > 27 && muon_iso < 0.1 && muon_mt < 30 && tau_decayMode != 5 && tau_decayMode != 6 && abs(tau_eta) < 2.3 && tau_pt > 20 && vis_mass > 40 && vis_mass < 80'.format(selection_id))
    elif ch == "single_tau":
        #df = df.Filter('(tau_sel & {}) != 0  && muon_pt > 27 && muon_iso < 0.1 && muon_mt < 30 && tau_decayMode != 5 && tau_decayMode != 6 && abs(tau_eta) < 2.3 && tau_pt > 20 && vis_mass > 40 && vis_mass < 80'.format(selection_id))
        df = df.Filter('(tau_sel & {}) != 0 && muon_pt > 27 && muon_iso < 0.1 && muon_mt < 30 && tau_decayMode != 5 && tau_decayMode != 6 && abs(tau_eta) < 2.3 && tau_pt > 20'.format(selection_id))
    elif ch == "ditaujet":
        df = df.Filter('(tau_sel & {}) != 0 && muon_pt > 27 && muon_iso < 0.1 && muon_mt < 30 && tau_decayMode != 5 && tau_decayMode != 6 && abs(tau_eta) < 2.3 && tau_pt > 20 && vis_mass > 40 && vis_mass < 80'.format(selection_id))
    elif ch == "VBFditau_lo":
        df = df.Filter('(tau_sel & {}) != 0  && muon_pt > 27 && muon_iso < 0.1 && muon_mt < 30 && tau_decayMode != 5 && tau_decayMode != 6 && abs(tau_eta) < 2.3 && tau_pt > 20 && vis_mass > 40 && vis_mass < 80'.format(selection_id))
    elif ch == "VBFditau_hi":
        df = df.Filter('(tau_sel & {}) != 0  && muon_pt > 27 && muon_iso < 0.1 && muon_mt < 30 && tau_decayMode != 5 && tau_decayMode != 6 && abs(tau_eta) < 2.3 && tau_pt > 20 && vis_mass > 40 && vis_mass < 80'.format(selection_id))
    else:
        df = df.Filter('(tau_sel & {}) != 0  && muon_pt > 27 && muon_iso < 0.1 && muon_mt < 30 && tau_decayMode != 5 && tau_decayMode != 6 && abs(tau_eta) < 2.3 && tau_pt > 20 && vis_mass > 40 && vis_mass < 80'.format(selection_id))
        #print("In Data after preselection ",df.Histo1D(hist_model,var).GetEntries())
    
    
    df = df.Filter('(byDeepTau2017v2p1VSmu & (1 << 5)) != 0 && (byDeepTau2017v2p1VSjet & (1 << 4)) != 0')
    df = df.Filter('tau_charge + muon_charge == 0 && tau_gen_match == 5')
    df = df.Define('weight', "PileUpWeightProvider::GetDefault().GetWeight(npu) * genEventWeight")
    hist_total,hist_pass,eff = dict(),dict(),dict()
    bool_singletau = False
    if ch == "single_tau":
        bool_singletau =True
    for var in vars:
        bins, x_scales, divide_by_bw = CreateBins(var,bool_singletau)
        hist_model = ROOT.RDF.TH1DModel(var, var, len(bins) - 1, array('d', bins))
        if var == 'tau_eta' or var == 'npv' or var == 'tau_phi':
            df = df.Filter('tau_pt > {}'.format(eta_th[ch]))
        match_mask = 0
        for path_name, path_index in hlt_paths.items():
            match_mask = match_mask | (1 << path_index)
    
        hist_total[var] = df.Histo1D(hist_model,var,"weight")
        if ch == 'VBFditau_hi':
            hist_pass[var]  = df.Filter('(hlt_acceptAndMatch & {}) != 0 && l1Tau_pt >= 45 && l1Tau_hwIso > 0'.format(match_mask)).Histo1D(hist_model, var,"weight")
        elif ch == 'etau' or ch == 'ditaujet':
            hist_pass[var]  = df.Filter('(hlt_acceptAndMatch & {}) != 0 && l1Tau_hwIso > 0 && l1Tau_pt >= 26'.format(match_mask)).Histo1D(hist_model, var,"weight")# && l1Tau_hwIso > 0
        else:
            hist_pass[var]  = df.Filter('(hlt_acceptAndMatch & {}) != 0'.format(match_mask)) \
                    .Histo1D(hist_model, var,"weight")

        eff[var] = ROOT.TEfficiency(hist_pass[var].GetPtr(), hist_total[var].GetPtr())
        print(hist_total[var].GetPtr().GetEntries())
    return hist_pass,hist_total,eff
        
