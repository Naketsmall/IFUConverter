import json
from abc import ABC, abstractmethod


class UltComponent:
    def __init__(self, name: str, d: dict):
        self.d = {}
        with open('basis_refs/comp_ref.json', 'r') as f:
            self.d = json.loads(f.read())
        self.d['name'] = name
        self.d['id'] = name
        self.d['basicProperties']['acentricFactor'] = d['parameters']['acentricFac']
        self.d['basicProperties']['criticalPressure'] = d['parameters']['critPres']
        self.d['basicProperties']['criticalTemperature'] = d['parameters']['critTemp']
        self.d['basicProperties']['criticalCompressibilityFactor'] = d['parameters']['critZ']
        self.d['basicProperties']['molarMass'] = d['parameters']['molarMass']
        self.d['correlationProperties'][1]['coeffs'] = d['parameters']['cp']['coeffs']
        self.d['correlationProperties'][1]['tmax'] = d['parameters']['cp']['tmax']
        self.d['correlationProperties'][1]['tmin'] = d['parameters']['cp']['tmin']

    def get_json(self):
        return json.dumps(self.d)


class UltComponentList:
    def __init__(self, d: dict):
        self.names = d['components']
        self.components = []
        for name in self.names:
            self.components.append(UltComponent(name, d['components-data'][name]))

        self.bics = []
        for key in d['PR-bics'].keys():
            bic = {}
            names = key.split('&')
            bic['comp1'] = names[0]
            bic['comp2'] = names[1]
            bic['value'] = d['PR-bics'][key]
            self.bics.append(bic)

    def __str__(self):
        s = """{"componentList":["""
        for component in self.components:
            s += component.get_json()
            s += ','
        s = s[:-1]
        s += ("""],"""
              """"bics":[""")

        for i in range(len(self.bics)):
            s += json.dumps(self.bics[i])
            s += ','
        s = s[:-1]
        s += ']}'
        return s

    def get_dict(self):
        return json.loads(str(self))


def get_basis_dict(complists: dict):
    d = {}
    with open('basis_refs/basis_ref.json', 'r') as f:
        d = json.loads(f.read())
    d['basis']['componentList'] = complists['componentList']
    d['basis']['bics'] = complists['bics']
    return d


def parse_material(d: dict, comps: list, mm: list, id: str):
    md = {}  # material_dict
    with open('input_refs/material_input_ref.json', 'r') as f:
        md = json.loads(f.read())
    md['id'] = id
    md['portId'] = id
    md['pressure'] = d['pres']
    md['temperature'] = d['temp']
    if 'moleFractions' in d.keys():
        divisor = sum([d['moleFractions'][i] * mm[i] for i in range(len(mm))])
        massFlow = d['molarFlow'] * divisor
        md['massFlow'] = massFlow
        mf = [{"id": comps[i], "value": mm[i] * d['moleFractions'][i] / divisor} for i in range(len(comps))]
        md['massFractions'] = mf
    else:
        md['massFlow'] = d['massFlow']
        md['massFractions'] = [{"id": comps[i], "value": d['massFractions'][i]} for i in range(len(comps))]
    return md


def parse_energy(d: dict, id: str):
    with open('input_refs/energy_input_ref.json', 'r') as f:
        ed = json.loads(f.read())
    ed['id'] = id
    ed['portId'] = id
    ed['power'] = d['power']
    return ed

def parse_unit(d: dict):
    parameters = []
    #print('dict:', d)
    #print('values:', d['values'])
    keys = d['values']
    for key in keys:
        if d['values'][key] != '':
            parameters.append({'name':key, 'value':d['values'][key]['value']})
    #print(parameters)
    return parameters