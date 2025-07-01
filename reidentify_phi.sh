#!/bin/bash

# Code to accept deidentified edi file(s) or folder and then reidentify the PHI data which was originally deidentified. Returns the reidentified EDI file in folder data/edi_files/reidentified
# This includes calls to x12xml(a pyx12 method), parser/reidentifyxml.py and parser/xml2x12.py
# For reidentifying originally deidentified PHI data, the phi_deid_reid_mapping file should be present in the 'rules' folder. This file is automatically created by the deidentify_phi.sh script.

usage() {
  echo "Usage: $0 <input_edi_file_or_folder>"
  exit 1
}

if [ $# -ne 1 ]; then
  usage
fi

input_path="$1"

process_single_edi() {
  local edi_file="$1"
  local base_name=$(basename "$edi_file")
  local name="${base_name%.*}"

  # Step 1: EDI to XML
  xml_file="data/xml_files/deidentified/${name}.xml"
  echo "Converting $edi_file to XML $xml_file"
  x12xml "$edi_file" --outputfile "$xml_file"

  # Step 2: Re-identify XML
  echo "Re-identifying $xml_file..."
  python parser/reidentifyxml.py --input="$xml_file"

  # Step 3: XML to EDI (re-identified)
  reid_xml_file="data/xml_files/reidentified/${name}_reidentified.xml"
  echo "Converting re-identified XML back to EDI..."
  python3.13 parser/xml2x12.py "$reid_xml_file"

  echo "Re-identified EDI file saved at: data/edi_files/reidentified/${name}.edi"
  echo "---------------------------------------------"
}

process_edi_folder() {
  local edi_folder="$1"
  local folder_name=$(basename "$edi_folder")
  local xml_folder="data/xml_files/deidentified/$folder_name"
  mkdir -p "$xml_folder"

  shopt -s nullglob
  edi_files=("$edi_folder"/*.edi)
  if [ ${#edi_files[@]} -eq 0 ]; then
    echo "No .edi files found in folder '$edi_folder'."
    exit 1
  fi

  # Step 1: Convert all .edi files to XML
  for edi_file in "${edi_files[@]}"; do
    base_name=$(basename "$edi_file")
    name="${base_name%.*}"
    xml_file="$xml_folder/${name}.xml"
    echo "Converting $edi_file to XML $xml_file"
    x12xml "$edi_file" --outputfile "$xml_file"
    if [ ! -f "$xml_file" ]; then
      echo "Error: XML file $xml_file was not created."
      exit 1
    fi
  done

  # Step 2: Re-identify all XML files in the folder
  echo "Re-identifying all XML files in $xml_folder..."
  python parser/reidentifyxml.py --input="$xml_folder"

  # Step 3: Convert all re-identified XML files back to EDI
  reid_xml_folder="data/xml_files/reidentified/$folder_name"
  echo "Converting all re-identified XML files in $reid_xml_folder to EDI..."
  python3.13 parser/xml2x12.py "$reid_xml_folder"

  echo "Re-identified EDI files saved at: data/edi_files/reidentified/$folder_name/"
  echo "---------------------------------------------"
  shopt -u nullglob
}

if [ -f "$input_path" ]; then
  process_single_edi "$input_path"
elif [ -d "$input_path" ]; then
  process_edi_folder "$input_path"
else
  echo "Error: '$input_path' is not a file or directory."
  usage
fi

echo "All re-identification processing completed."
