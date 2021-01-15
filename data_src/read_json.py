import ipdb
st=ipdb.set_trace
import json

with open('bvp_ses1_trn1.json') as f:
  data = json.load(f)


with open('bvp_ses1_trn1_torender.json') as f:
  data2 = json.load(f)


st()
print("end")
