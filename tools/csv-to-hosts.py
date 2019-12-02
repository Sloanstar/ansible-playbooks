# !/usr/bin/python
# Little tool for me to read a csv and generate an ansible hosts file.
# Open File Report_All_Firewalls_Report.csv
# Read CSV
# Output Host File

import csv

input_file = csv.DictReader(open("Report_All_Firewalls_Report.csv"))
firewalls = []
allModels = []
primary = []
allPrimary = []
secondary = []
allSecondary = []
lastModel = None
fwNewModel = False
index=0

#SET ASA:vars for host file
asaFileHost = "127.0.0.1"
asaFileTransport = "tftp"
asaSshTimeout = 5
#End ASA:vars

for line in input_file:
    firewalls.append(line)

for firewall in firewalls:
    fwModel = firewall["Machine Type"].replace(" ","_")

    if len(firewalls) > index+1:
        fwNextModel = firewalls[index+1]["Machine Type"].replace(" ","_")
        if fwModel != fwNextModel:
            fwNewModel = True
        else:
            fwNewModel = False
    else:
        fwNewModel = True

    if firewall['Caption'].lower().endswith("_secondary"):
        secondary.append(firewall['Caption'] + "\tansible_ssh_host=" + firewall['IP Address'])
    else:
        primary.append(firewall['Caption'] + "\tansible_ssh_host=" + firewall['IP Address'])

    if fwNewModel is True: #Dump the list
        if fwModel:
            print(f"[{fwModel}]")
            allModels.append(fwModel)
        if fwModel and len(primary) > 0 and len(secondary) > 0:
            print(f"[{fwModel}:children]")
            print(f"{fwModel}_PRIMARY")
            allPrimary.append(f"{fwModel}_PRIMARY")
            print(f"{fwModel}_SECONDARY")
            allSecondary.append(f"{fwModel}_SECONDARY")
            print("\n")
            #dump primary
            print(f"[{fwModel}_PRIMARY]")
            for fw in primary:
                print(f"{fw}")
            print("\n")
            #dump secondary
            print(f"[{fwModel}_SECONDARY]")
            for fw in secondary:
                print(f"{fw}")
            print("\n")
        elif fwModel and len(primary) > 0:
            allPrimary.append(fwModel)
            for fw in primary:
                print(f"{fw}")
            print("\n")
        primary = []
        secondary = []
    index += 1
#List All Primary Groups
print(f"[ASA_PRIMARY]")
print(f"[ASA_PRIMARY:children]")
for model in allPrimary:
    print(f"{model}")
print("\n")

#List All Secondary Groups
print(f"[ASA_SECONDARY]")
print(f"[ASA_SECONDARY:children]")
for model in allSecondary:
    print(f"{model}")
print("\n")

#List ALL Groups
#List All Secondary Groups
print(f"[ASA]")
print(f"[ASA:children]")
for model in allModels:
    print(f"{model}")
print("\n")

# TODO VARS as variables at top, printed here.
# TODO Model Specific variables.

print(f"[ASA:vars]")
print(f"ansible_network_os=asa")
print(f"ansible_become=yes")
print(f"ansible_become_method=enable")
print(f"asaFileTransport={asaFileTransport}")
print(f"asaFileHost={asaFileHost}")
print(f"asaMulticontext=false")
print(f"asaAsdmImage=asdm-7131.bin")
print(f"asaRestImage=asa-restapi-7131-lfbff-k8.SPA")
print(f"asaSshTimeout={asaSshTimeout}")

