In salome container:

```
export HIFIMAGNET=/opt/SALOME-9.7.0-UB20.04/INSTALL/HIFIMAGNET/bin/salome
salome -w1 -t $HIFIMAGNET/HIFIMAGNET_Cmd.py args:HL-31.yaml,--axi,--air,2,2
```

Then:

```
python -m python_magnetgeo.xao HL-31-Axi.xao mesh --group CoolingChannels --geo HL-31.yaml
```

