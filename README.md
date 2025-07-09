WHAT THIS REPOSITORY DOES:

1. DE-IDENTIFICATION of PHI
Input: Raw 837 and 835 X12 EDI files

Processing: Files are parsed using the PyX12 library and converted into structured XML using standard implementation maps.
A custom Python script (deidentify.py) uses a configurable masking JSON file to locate and replace PHI fields (e.g., patient name, SSN, address) with anonymized placeholders.
A mapping JSON file is generated to track original-to-masked values.

Output: De-identified XMLs are converted back to X12 format using XML2X12.py, ready for safe use in clinical research or analytics.

2. RE-IDENTIFICATION of PHI
Input: De-identified 837/835 files and the saved mapping JSON.

Processing: Files are again converted to XML using PyX12. reidentify.py script uses the mapping JSON to repopulate the original PHI back into the correct fields.
The XML is converted back to fully re-identified X12 using XML2X12.py.

Use Case: Enables retrieval of original PHI when needed for authorized operational workflows


PROJECT STRUCTURE:
pythonX12handler/
├── data/
│   ├── x12_files/
│   └── xml_files/
├── parser/
│   ├── deidentify.py
│   ├── reidentify.py
│   ├── XML2X12.py
│   └── __init__.py
├── rules/
│   ├── phi_deid_reid_mapping.json
│   └── phi_fields_to_mask.json
├── readme/
│   ├── README.md
├── deidentify_phi.sh/
├── reidentify_phi.sh/

PROJECT STRUCTURE EXPLANATION:
parser/: Core logic for de-identifying and re-identifying PHI, and converting XML ↔ X12.
rules/: JSON files containing masking rules and mappings.
data/: Input and output X12/XML files.
readme/: Documentation.


# pythonx12handler
# pip install pyx12
# pip install lxml
# pip install xmltodict
# pip install jsonschema
# pip install jsonpickle
# pip install requests


############ STEPS to deidentify and reidentify X12 files ####################

## STEP 1: Get the X12 file ready to be de-identified. There should be no tilde (~) or any other special characters in the file.
## STEP 2: Identify PHI identifiers to be masked.
## STEP 3: Create the masking file 'phi_fields_to_mask.json' and include the required PHI identifiers(Sample here)
## STEP 4: Identify EDI file(s) or folders to be deidentified and place them in the 'data/x12_files' directory.
## STEP 5: Execute the de-identification script to mask the PHI identifiers in the EDI files. This will utilise file 'phi_fields_to_mask.json'
        ./deidentify_phi.sh data/x12_files/<filename>
        ./deidentify_phi.sh data/x12_files/<foldername>
##NOTE - If required provide required executable permissions  "chmod +x deidentify_phi.sh"
## STEP 6: The deidentified files can be accessed from the 'data/x12_files/deidentified' directory.
## STEP 7: The mapping file is also created which can be utilised for re-identifcaion later.
## STEP 8: If required, re-identify the de-identified EDI files. The deidentification script utilises the mapping file 'phi_deid_reid_mapping.json'.
        ./reidentify_phi.sh data/x12_files/deidentified/<filename>
        ./reidentify_phi.sh data/x12_files/deidentified/<foldername>
## STEP 9: The reidentified edi files can be accessed from the 'data/x12_files/reidentified' directory.

############ Explaining all other scripts available in this repository ######################

##Covert X12 to XML, using the pyx12 library. If required provide the map path also using --map-path option.
##x12xml data/x12_files/837_sample.x12 --outputfile data/xml_files/837_sample.xml --map-path /Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages/pyx12/map
x12xml data/x12_files/<filename.x12> --outputfile data/xml_files/<filename.xml>

#Deidentifying XML files
python parser/deidentifyxml.py --input=data/xml_files/<filename.xml>
python parser/deidentifyxml.py --input=data/xml_files/<foldername>

#Reidentifying XML files
python parser/reidentifyxml.py --input=data/xml_files/deidentified/<filename.xml>
python parser/reidentifyxml.py --input=data/xml_files/deidentified/<foldername>

#Converting XML files to X12 format
python parser/xml2x12.py data/xml_files/deidentified/<filename>
python parser/xml2x12.py data/xml_files/deidentified/<foldername>
python parser/xml2x12.py data/xml_files/reidentified/<filename>
python parser/xml2x12.py data/xml_files/reidentified/<foldername>
