#!/bin/bash

# Code to accept x12 file(s) or folder and deidentifying PHI data. Returns the deidentified X12 file in folder data/x12_files/deidentified
# This includes calls to x12xml(a pyx12 method), parser/deidentifyxml.py and parser/xml2x12.py
# This utilises the masking rules defined in phi_fields_to_mask.json. The de-identification process also creates a mapping file called phi_deid_reid_mapping.json.

# Usage message
usage() {
  echo "Usage: $0 <input_x12_file_or_folder>"
  exit 1
}

if [ $# -ne 1 ]; then
  usage
fi

input_path="$1"

# Single X12 file
process_single_x12() {
  local x12_file="$1"
  local base_name=$(basename "$x12_file")
  local name="${base_name%.*}"

  # Step 1: X12 to XML
  #xml_file="data/xml_files/${name}.xml"
  xml_dir="data/xml_files"
  mkdir -p "$xml_dir"
  xml_file="${xml_dir}/${name}.xml"
  echo "Converting $x12_file to XML file $xml_file"
  #python3.13 -m pyx12.x12xml "$x12_file" --outputfile "$xml_file"
  # For calling x12xml the pyx12 directory path should be added to PATH variable.
  x12xml "$x12_file" --outputfile "$xml_file"

  # Step 2: De-identify XML
  echo "De-identifying $xml_file..."
  python parser/deidentifyxml.py --input="$xml_file"

  # Step 3: XML to X12 (de-identified)
  deid_xml_file="data/xml_files/deidentified/${name}_deidentified.xml"
  echo "Converting de-identified XML back to X12..."
  python3.13 parser/xml2x12.py "$deid_xml_file"

  echo "De-identified X12 file saved at: data/x12_files/deidentified/${name}.x12"
  echo "---------------------------------------------"
}

# Folder of X12 files
process_x12_folder() {
  local x12_folder="$1"
  local folder_name=$(basename "$x12_folder")
  local xml_folder="data/xml_files/$folder_name"

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
    # For calling x12xml the pyx12 directory path should be added to PATH variable.
    x12xml "$x12_file" --outputfile "$xml_file"
    if [ ! -f "$xml_file" ]; then
      echo "Error: XML file $xml_file was not created. x12xml likely failed."
      exit 1
    fi
  done

  # Step 2: De-identify all XML files in the folder (your script handles the folder)
  echo "De-identifying all XML files in $xml_folder..."
  python parser/deidentifyxml.py --input="$xml_folder"

  # Step 3: Convert all de-identified XML files back to X12 (your script handles the folder)
  deid_xml_folder="data/xml_files/deidentified/$folder_name"
  echo "Converting de-identified XML files back to X12..."
  python3.13 parser/xml2x12.py "$deid_xml_folder"

  echo "De-identified X12 files saved at: data/x12_files/deidentified/$folder_name/"
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

echo "All processing completed."
