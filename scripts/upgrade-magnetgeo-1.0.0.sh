#! /bin/dash

perl -pi -e "s|^Helices\:|helices\:|g" *.yaml
perl -pi -e "s|^Rings\:|rings\:|g" *.yaml
perl -pi -e "s|^HAngles\:|hangles\:|g" *.yaml
perl -pi -e "s|^RAngles\:|rangles\:|g" *.yaml
perl -pi -e "s|^CurrentLeads\:|currentleads\:|g" *.yaml
perl -pi -e "s|^axi\:|modelaxi\:|g" *.yaml
perl -pi -e "s|^m3d\:|model3d\:|g" *.yaml
perl -ni -e "print unless /^material/" *.yaml

