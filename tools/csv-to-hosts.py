# !/usr/bin/python
# Little tool for me to read a csv and generate an ansible hosts file.
# Open File Report_All_Firewalls_Report.csv
# Read CSV
# Output Host File

import csv
import configparser

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

for line in input_file:
    firewalls.append(line)

# Pull VARS from INI file.
asaVars = configparser.ConfigParser()
asaVars.optionxform=str
asaVars.read("asa_vars.ini")

for firewall in firewalls:
    fwModel = firewall["Machine Type"].replace(" ","_")
    fwModel = fwModel.replace("-","_")

    if len(firewalls) > index+1:
        fwNextModel = firewalls[index+1]["Machine Type"].replace(" ","_")
        fwNextModel = fwNextModel.replace("-","_")
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
            #dump primary vars from INI
            if asaVars.has_section(fwModel):
                print(f"[{fwModel}_PRIMARY:vars]")
                for key,value in asaVars.items(fwModel):
                    print(f"{key}={value}")
                print(f"\n")
            #dump secondary
            print(f"[{fwModel}_SECONDARY]")
            for fw in secondary:
                print(f"{fw}")
            print("\n")
            #dump secondary vars from INI
            if asaVars.has_section(fwModel):
                print(f"[{fwModel}_SECONDARY:vars]")
                for key,value in asaVars.items(fwModel):
                    print(f"{key}={value}")
                print(f"\n")
        elif fwModel and len(primary) > 0:
            allPrimary.append(fwModel)
            for fw in primary:
                print(f"{fw}")
            print("\n")
            #dump vars from INI for model type, if no pri/sec
            if asaVars.has_section(fwModel):
                print(f"[{fwModel}:vars]")
                for key,value in asaVars.items(fwModel):
                    print(f"{key}={value}")
                print(f"\n")
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

print(f"[ASA:vars]")
for key,value in asaVars.items('ASA'):
    print(f"{key}={value}")
print(f"\n")

#Warn for unused sections/models basted on host generation.
for section in asaVars:
    if section == "DEFAULT":
        continue
    if section != "ASA":
        if section not in allModels:
            print(f"# WARNING!!! - Variable Section with no matching model!\n# WARNING!!! - These variables will not be used!")
            print(f"[{section}:vars]")
            for key,value in asaVars.items(section):
                print(f"{key}={value}")
            print(f"\n")
