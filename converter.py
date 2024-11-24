import json


class UltComponent:
    '''
    Класс, хранящий компоненту в формате ультиматек
    '''

    def __init__(self, name: str, d: dict):
        '''

        :param name: Имя компоненты
        :param d: словарь параметров компоненты
        '''
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

    def get_dict(self):
        ''''
        Возвращает словарь компоненты в формате ультиматек
        '''
        return self.d


class UltComponentList:
    def __init__(self, d: dict):
        '''
        Составляет словари componentList и bics
        :param d: весь словарь в формате FS
        '''
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

    def get_dict(self):
        return {"componentList": [comp.get_dict() for comp in self.components], "bics": self.bics}


def get_basis_dict(complists: dict):
    '''
    Тут стоит глянуть на формат UT и заметить, что состоит он из 4 ветвей. эта ф-я собирает ветвь basis
    :param complists:  dict complists + bict
    :return: dict basis
    '''
    d = {}
    with open('basis_refs/basis_ref.json', 'r') as f:
        # Немного темной магии. пока в силу отсутствия достаточного числа примеров нового входа, базис thermopackage задаем так
        d = json.loads(f.read())
    d['basis']['componentList'] = complists['componentList']
    d['basis']['bics'] = complists['bics']
    return d


def parse_material(d: dict, comps: list, mm: list, id: str):
    '''
    Снова устремляем взор на ультиматековский формат. потоки с заданными ТД-параметрами называются материалами.
    Их здесь создаем
    :param d: описание потока (flowdefinition)
    :param comps: лист компонент
    :param mm: молярные массы компонент
    :param id: который мы хотим присвоить потоку
    :return: dict потока в формате UT
    '''
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
    '''
    Задает энергетический поток в формате UT
    :param d: dict энергетического потока в формате FS
    :param id: id, который мы хотим ему присвоить
    :return: dict ЭП в формате UT
    '''
    with open('input_refs/energy_input_ref.json', 'r') as f:
        ed = json.loads(f.read())
    ed['id'] = id
    ed['portId'] = id
    ed['power'] = d['power']
    return ed


def parse_unit(d: dict):
    '''
    Создает json параметров юнита
    :param d: objects/separator2-1/d
    :return: параметры юнита в формате UT
    '''
    parameters = []
    #print('dict:', d)
    #print('values:', d['values'])
    keys = d['values']
    for key in keys:
        if d['values'][key] != '':
            parameters.append({'name': key, 'value': d['values'][key]['value']})
    #print(parameters)
    return parameters


class Converter:
    def __init__(self, d: dict):
        '''
        Инициализирует конвертер с полями в формате ультиматека
        :param d:  словарь из флоусимовского json
        '''
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
                'parameters': self.parameters}
