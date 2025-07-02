#!/bin/bash

# Code to accept deidentified x12 file(s) or folder and then reidentify the PHI data which was originally deidentified. Returns the reidentified X12 file in folder data/x12_files/reidentified
# This includes calls to x12xml(a pyx12 method), parser/reidentifyxml.py and parser/xml2x12.py
# For reidentifying originally deidentified PHI data, the phi_deid_reid_mapping file should be present in the 'rules' folder. This file is automatically created by the deidentify_phi.sh script.

usage() {
  echo "Usage: $0 <input_x12_file_or_folder>"
  exit 1
}

if [ $# -ne 1 ]; then
  usage
fi

input_path="$1"

process_single_x12() {
  local x12_file="$1"
  local base_name=$(basename "$x12_file")
  local name="${base_name%.*}"

  # Step 1: X12 to XML
  xml_file="data/xml_files/deidentified/${name}.xml"
  echo "Converting $x12_file to XML $xml_file"
  x12xml "$x12_file" --outputfile "$xml_file"

  # Step 2: Re-identify XML
  echo "Re-identifying $xml_file..."
  python parser/reidentifyxml.py --input="$xml_file"

  # Step 3: XML to X12 (re-identified)
  reid_xml_file="data/xml_files/reidentified/${name}_reidentified.xml"
  echo "Converting re-identified XML back to X12..."
  python3.13 parser/xml2x12.py "$reid_xml_file"

  echo "Re-identified X12 file saved at: data/x12_files/reidentified/${name}.x12"
  echo "---------------------------------------------"
}

process_x12_folder() {
  local x12_folder="$1"
  local folder_name=$(basename "$x12_folder")
  local xml_folder="data/xml_files/deidentified/$folder_name"
  mkdir -p "$xml_folder"

  shopt -s nullglob
  x12_files=("$x12_folder"/*.x12)
  if [ ${#x12_files[@]} -eq 0 ]; then
    echo "No .x12 files found in folder '$x12_folder'."
    exit 1
  fi

  # Step 1: Convert all .x12 files to XML
  for x12_file in "${x12_files[@]}"; do
    base_name=$(basename "$x12_file")
    name="${base_name%.*}"
    xml_file="$xml_folder/${name}.xml"
    echo "Converting $x12_file to XML $xml_file"
    x12xml "$x12_file" --outputfile "$xml_file"
    if [ ! -f "$xml_file" ]; then
      echo "Error: XML file $xml_file was not created."
      exit 1
    fi
  done

  # Step 2: Re-identify all XML files in the folder
  echo "Re-identifying all XML files in $xml_folder..."
  python parser/reidentifyxml.py --input="$xml_folder"

  # Step 3: Convert all re-identified XML files back to X12
  reid_xml_folder="data/xml_files/reidentified/$folder_name"
  echo "Converting all re-identified XML files in $reid_xml_folder to X12..."
  python3.13 parser/xml2x12.py "$reid_xml_folder"

  echo "Re-identified X12 files saved at: data/x12_files/reidentified/$folder_name/"
  echo "---------------------------------------------"
  shopt -u nullglob
}

if [ -f "$input_path" ]; then
  process_single_x12 "$input_path"
elif [ -d "$input_path" ]; then
  process_x12_folder "$input_path"
else
  echo "Error: '$input_path' is not a file or directory."
  usage
fi

echo "All re-identification processing completed."
