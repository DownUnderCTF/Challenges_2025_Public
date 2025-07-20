bilingual
============

## Solution

* The Python script contains an embedded DLL. The flag checking logic is split between the Python code and the DLL.
* The DLL will call back into Python to access script globals and evaluate expressions.
* Run the challenge with the password "Hydr0ph11na3" to get the flag. (A hydrophiinae is a sea snake. Because it's C and Python? Wocka wockaaa!)
