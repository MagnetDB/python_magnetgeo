import yaml

def Insert_constructor(loader, node):
    print("Insert_constructor")
    values = loader.construct_mapping(node)
    print(f'values: {values}')
    name = values["name"]
    print("Helices:", values.get("Helices", []), type(values.get("Helices", [])))
    return values

yaml.add_constructor('Insert', Insert_constructor)

def Helix_constructor(loader, node):
    print("Helix_constructor")
    values = loader.construct_mapping(node)
    print(f'values: {values}')
    name = values["name"]
    return values

yaml.add_constructor('Helix', Helix_constructor)

def Groove_constructor(loader, node):
    print("Groove_constructor")
    values = loader.construct_mapping(node)
    print(f'values: {values}')
    name = values["name"]
    return values

yaml.add_constructor('Groove', Groove_constructor)

def Groove_constructor(loader, node):
    print("Groove_constructor")
    values = loader.construct_mapping(node)
    print(f'values: {values}')
    return values

yaml.add_constructor('Groove', Groove_constructor)

def Shape_constructor(loader, node):
    print("Shape_constructor")
    values = loader.construct_mapping(node)
    print(f'values: {values}')
    return values

yaml.add_constructor('Shape', Shape_constructor)

# Exemple de fichier YAML
yaml_content = """
!<Insert>
name: example
Helices:
  - item1
  - item2
  - item3
"""

tutu_content = """
!<Insert>
currentleads: []
hangles: [1, 2]
helices:
- !<Helix>
  chamfers: []
  cutwidth: 0.22
  dble: true
  grooves: !<Groove>
    eps: 0
    gtype: null
    n: 0
  name: HL-31_H1
  odd: true
  r:
  - 19.3
  - 24.2
  shape: !<Shape>
    angle: 0
    length: 0
    name: null
    onturns: 0
    position: ABOVE
    profile: ''
  z:
  - -226
  - 108
- !<Helix>
  chamfers: []
  cutwidth: 0.22
  dble: true
  grooves: !<Groove>
    eps: 0
    gtype: null
    n: 0
  name: HL-31_H2
  odd: false
  r:
  - 25.1
  - 30.7
  shape: !<Shape>
    angle: 0
    length: 0
    name: ''
    onturns: 0
    position: ABOVE
    profile: ''
  z:
  - -108
  - 108
innerbore: 7
name: tutu
outerbore: 8
rangles: [3, 4]
rings: []
"""
data = yaml.load(yaml_content, Loader=yaml.FullLoader)
print("Data loaded from YAML:", data)

data = yaml.load(tutu_content, Loader=yaml.FullLoader)
print("Data loaded from YAML:", data)

# data = yaml.load(open('tt.yaml', 'r'), Loader=yaml.FullLoader)
