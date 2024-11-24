from converter import *


class Converter:
    def __init__(self, d: dict):
        basis = get_basis_dict(UltComponentList(d).get_dict())
        self.basis = basis
        comp_names = d['components']
        comp_mms = [d['components-data'][name]['parameters']['molarMass'] for name in comp_names]

        inputs = []
        parameters = []
        for key in d['objects'].keys():
            if 'input' in key:
                inputs.append(parse_material(d['objects'][key]['flowdefinition'], comp_names, comp_mms, key))
            elif 'energy' in key:
                inputs.append(parse_energy(d['objects'][key], key))
            else:
                parameters.append(parse_unit(d['objects'][key]))
        self.inputs = inputs
        self.parameters = parameters[0]

        outputs = []
        if 'separator' in d['scheme']['pattern']:
            with open('output_refs/separator_output_ref.json') as f:
                outputs = json.loads(f.read())
        elif 'mixer' in d['scheme']['pattern']:
            with open('output_refs/mixer_output_ref.json') as f:
                outputs = json.loads(f.read())
        else:
            with open('output_refs/fluid_output_ref.json') as f:
                outputs = json.loads(f.read())
        self.outputs = outputs




    def get_dict(self):
        return {'basis': self.basis['basis'],
                'inputs': self.inputs,
                'outputs': self.outputs['outputs'],
                'parameters':self.parameters}