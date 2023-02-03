"""

"""

from typing import Union

import re
import gmsh


def create_physicalgroups(
    tree,
    solid_names: list,
    ring_ids: dict,
    GeomParams: dict,
    hideIsolant: bool,
    groupIsolant: bool,
    debug: bool = False,
):
    """
    creates PhysicalVolumes
    """

    tr_subelements = tree.xpath("//" + GeomParams["Solid"][1])
    stags = {}
    for i, sgroup in enumerate(tr_subelements):
        for j, child in enumerate(sgroup):
            sname = solid_names[j]
            oname = sname
            print(f"sname={sname}: child.attrib={child.attrib}")
            if "name" in child.attrib and child.attrib["name"] != "":
                # print(f"sname={sname}, {child.attrib['name']}")
                sname = child.attrib["name"].replace("from_", "")
                # print(f'sname={sname}')
                if sname.startswith("Ring-H"):
                    sname = ring_ids[sname]

            indices = int(child.attrib["index"]) + 1
            if debug:
                print(
                    f"sname[{j}]: oname={oname}, sname={sname}, child.attrib={child.attrib}, solid_name={solid_names[j]}, indices={indices}"
                )

            skip = False
            if hideIsolant and (
                "Isolant" in sname or "Glue" in sname or "Kapton" in sname
            ):
                if debug:
                    print(f"skip isolant: {sname}")
                skip = True

            # TODO if groupIsolant and "glue" in sname:
            #    sname = remove latest digit from sname
            if groupIsolant and (
                "Isolant" in sname or "Glue" in sname or "Kapton" in sname
            ):
                sname = re.sub(r"\d+$", "", sname)

            if not skip:
                if sname in stags:
                    stags[sname].append(indices)
                else:
                    stags[sname] = [indices]

    # Physical Volumes
    if debug:
        print("Solidtags:")
    for stag in stags:
        pgrp = gmsh.model.addPhysicalGroup(GeomParams["Solid"][0], stags[stag])
        gmsh.model.setPhysicalName(GeomParams["Solid"][0], pgrp, stag)
        if debug:
            print(f"{stag}: {stags[stag]}, pgrp={pgrp}")

    return stags


def create_bcs(
    tree,
    ring_ids,
    gname,
    GeomParams,
    NHelices,
    innerLead_exist,
    outerLead_exist,
    groupCoolingChannels,
    Channel_Submeshes,
    compound,
    hideIsolant,
    groupIsolant,
    debug: bool = False,
):

    tr_elements = tree.xpath("//group")

    if debug:
        print("Ring_ids")
        for rkey in ring_ids:
            print(f"rkey={rkey}, rvalue={ring_ids[rkey]}")

    bctags = {}
    for i, group in enumerate(tr_elements):
        if debug:
            print(
                "name=",
                group.attrib["name"],
                group.attrib["dimension"],
                group.attrib["count"],
            )

        indices = []
        if group.attrib["dimension"] == GeomParams["Face"][1]:
            print(f"BCs[{i}]: {group.attrib['name']}")
            for child in group:
                indices.append(int(child.attrib["index"]) + 1)

            # get bc name
            insert_id = gname.replace("_withAir", "")
            sname = group.attrib["name"].replace(insert_id + "_", "")
            sname = sname.replace("===", "_")

            if debug:
                print(f"sname={sname}")

            if not ring_ids is None:
                if sname.endswith("_rInt") or sname.endswith("_rExt"):
                    for rkey in ring_ids:
                        if sname.startswith(rkey):
                            sname = sname.replace(rkey, ring_ids[rkey])

                if sname.startswith("Ring-H"):
                    for rkey in ring_ids:
                        if sname.startswith(rkey):
                            sname = sname.replace(rkey, ring_ids[rkey])

            sname = sname.replace("Air_", "")
            if debug:
                print(sname, indices, insert_id)

            skip = False

            # remove unneeded surfaces for Rings: BP for even rings and HP for odd rings
            if sname.startswith("R") and ("_BP" in sname or "_HP" in sname):
                num = int(sname.split("_")[0].replace("R", ""))
                if num % 2 == 0 and "BP" in sname:
                    skip = True
                if num % 2 != 0 and "HP" in sname:
                    if not ("H_HP" in sname or re.search("_H\d+_HP", sname)):
                        skip = True
                    else:
                        sname = re.sub("R\d+_", "", sname)

                print(f"{group.attrib['name']}, sname={sname}, num={num}, skip={skip}")

            # keep only H0_V0 if no innerlead otherwise keep Lead_V0
            # keep only H14_V1 if not outerlead otherwise keep outerlead V1
            # print(innerLead_exist, re.search('H\d+_V0',sname))
            if innerLead_exist:
                match = re.search("H\d+_V0", sname)
                if match or (sname.startswith("Inner") and sname.endswith("V1")):
                    skip = True
            else:
                match = re.search("H\d+_V0", sname)
                if match:
                    num = int(sname.split("_")[0].replace("H", ""))
                    if num != 1:
                        skip = True
            if outerLead_exist:
                match = re.search("H\d+_V1", sname)
                if match:
                    skip = True
                if sname.startswith("Outer") and sname.endswith("V1"):
                    skip = True
            else:
                match = re.search("H\d+_V1", sname)
                if match:
                    num = int(sname.split("_")[0].replace("H", ""))
                    if num != NHelices:
                        skip = True

            # groupCoolingChannels option (see Tools_SMESH::CreateChannelSubMeshes for HL and for HR ??) + watch out when hideIsolant is True
            # TODO case of HR: group HChannel and muChannel per Helix
            if groupCoolingChannels:
                for j, channel_id in enumerate(Channel_Submeshes):
                    for cname in channel_id:
                        if sname.endswith(cname):
                            sname = f"Channel{j}"
                            break

                # TODO make it more general
                # so far assume only one insert and  insert is the 1st compound
                if compound:
                    if sname.startswith(compound[0]):
                        if "_rInt" in sname or "_rExt" in sname:
                            skip = True
                        if "_IrInt" in sname or "_IrExt" in sname:
                            skip = True
                        if "_iRint" in sname or "_iRext" in sname:
                            skip = True
                else:
                    if "_rInt" in sname or "_rExt" in sname:
                        skip = True
                    if "_IrInt" in sname or "_IrExt" in sname:
                        skip = True
                    if "_iRint" in sname or "_iRext" in sname:
                        skip = True

            # if hideIsolant remove "iRint"|"iRext" in Bcs otherwise sname: do not record physical surface for Interface
            if hideIsolant:
                if "IrInt" in sname or "IrExt" in sname:
                    skip = True
                if "iRint" in sname or "iRext" in sname:
                    skip = True
                if "Interface" in sname:
                    if groupIsolant:
                        sname = re.sub(r"\d+$", "", sname)

            if groupIsolant:
                if "IrInt" in sname or "IrExt" in sname:
                    sname = re.sub(r"\d+$", "", sname)
                if "iRint" in sname or "iRext" in sname:
                    sname = re.sub(r"\d+$", "", sname)
                    # print("groupBC:", sname)
                if "Interface" in sname:
                    # print("groupBC: skip ", sname)
                    skip = True

            print(
                f"name={group.attrib['name']}, {group.attrib['dimension']}, {group.attrib['count']}, sname={sname}, skip={skip}"
            )
            if debug:
                print(
                    f"name={group.attrib['name']}, {group.attrib['dimension']}, {group.attrib['count']}, sname={sname}, skip={skip}"
                )
            if not skip:
                if not sname in bctags:
                    bctags[sname] = indices
                else:
                    for index in indices:
                        bctags[sname].append(index)

    # Physical Surfaces
    if debug:
        print("BCtags:")
    for bctag in bctags:
        pgrp = gmsh.model.addPhysicalGroup(GeomParams["Face"][0], bctags[bctag])
        gmsh.model.setPhysicalName(GeomParams["Face"][0], pgrp, bctag)
        if debug:
            print(bctag, bctags[bctag], pgrp)

    return bctags


def create_channels(
    NChannels: Union[int, list], hideIsolant: bool, debug: bool = False
):
    """
    create channels

    TODO regexp shall be associated to a magnet
    """
    Channel_Submeshes = []

    if isinstance(NChannels, int):
        _NChannels = NChannels
    elif isinstance(NChannels, list):
        _NChannels = NChannels[0]
    for i in range(0, _NChannels):
        names = []
        inames = []
        if i == 0:
            names.append(f"R{i+1}_R0n")  # check Ring nummerotation
        if i >= 1:
            names.append(f"H{i}_rExt")
            if not hideIsolant:
                isolant_names = [f"H{i}_IrExt"]
                kapton_names = [f"H{i}_kaptonsIrExt"]
                names = names + isolant_names + kapton_names
                # inames = inames + isolant_names + kapton_names
        if i >= 2:
            names.append(f"R{i-1}_R1n")
        if i < _NChannels:
            names.append(f"H{i+1}_rInt")
            if not hideIsolant:
                isolant_names = [f"H{i+1}_IrInt"]
                kapton_names = [f"H{i+1}_kaptonsIrInt"]
                names = names + isolant_names + kapton_names
                # inames = inames + isolant_names + kapton_names
        # Better? if i+1 < nchannels:
        if i != 0 and i + 1 < _NChannels:
            names.append(f"R{i}_CoolingSlits")
            names.append(f"R{i}_R0n")
        Channel_Submeshes.append(names)
        #
        # For the moment keep iChannel_Submeshes into
        # iChannel_Submeshes.append(inames)

    if debug:
        print("Channel_Submeshes:")
        for channel in Channel_Submeshes:
            print(f"\t{channel}")

    return Channel_Submeshes
