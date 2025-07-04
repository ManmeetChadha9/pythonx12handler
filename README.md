# pythonx12handler

############ STEPS to deidentify and reidentify X12 files ####################

## STEP 1: Identify PHI identifiers to be masked.
## STEP 2: Create the masking file 'phi_fields_to_mask.json' and include the required PHI identifiers(Sample here)
## STEP 3: Identify EDI file(s) or folders to be deidentified and place them in the 'data/x12_files' directory.
## STEP 4: Execute the de-identification script to mask the PHI identifiers in the EDI files. This will utilise file 'phi_fields_to_mask.json'
        ./deidentify_phi.sh data/x12_files/<filename>
        ./deidentify_phi.sh data/x12_files/<foldername>
##NOTE - If required provide required executable permissions  "chmod +x deidentify_phi.sh"
## STEP 5: The deidentified edi files can be accessed from the 'data/x12_files/deidentified' directory.
## STEP 6: If required, re-identify the de-identified EDI files. The deidentification script utilises the mapping file 'phi_deid_reid_mapping.json'.
        ./reidentify_phi.sh data/x12_files/deidentified/<filename>
        ./reidentify_phi.sh data/x12_files/deidentified/<foldername>
## STEP 7: The reidentified edi files can be accessed from the 'data/x12_files/reidentified' directory.

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
