
"""
"""
from python_magnetgeo.utils import getObject



Object = getObject("HL-31-H1H2.yaml")
print(f"Object={Object}, type={type(Object)}")
Object = getObject("M9Bitters.yaml")
print(f"Object={Object}, type={type(Object)}")
Object = getObject("Oxford.yaml")
print(f"Object={Object}, type={type(Object)}")
Object = getObject("Nougat.yaml")
print(f"Object={Object}, type={type(Object)}")

Object = getObject("M9_HL-31-H1.yaml")
print(f"Object={Object}, type={type(Object)}")
"""
Object = getObject("msite.yaml")
print(f"Object={Object}, type={type(Object)}")
"""

Object.name = "newtest"
Object.dump()
Obect = getObject("newtest.yaml")
print(f"nObject={Object}, type={type(Object)}")
