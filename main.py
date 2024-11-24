import json
from converter import *


path = "flowsim_in_examples/fs_format.json"
# отсюда берем файл в формате flowsim, который будем конвертировать в ультиматековский

j_in = {}
with open(path, 'r') as f:
    j_in = json.loads(f.read())



# сюда записываем
with open('written.json', 'w') as output:
    output.write(json.dumps(Converter(j_in).get_dict())) # вся магия в Converter


