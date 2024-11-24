import json

from converter import *
from IFUconverter import *

#path = "flowsim_in_examples/separator2_example1_in.json"
#path = "flowsim_in_examples/heater_example3_in.json"
path = "flowsim_in_examples/fs_format.json"

j_in = {}
with open(path, 'r') as f:
    j_in = json.loads(f.read())

#Converter(j_in).get_dict()

with open('written.json', 'w') as output:
   output.write(json.dumps(Converter(j_in).get_dict()))


#cl = UltComponentList(j_in)
#with open('written.json', 'w') as output:
 #   output.write(str(cl))

#with open('written.json', 'w') as output:
 #  output.write(json.dumps(get_basis_dict(cl.get_dict())))