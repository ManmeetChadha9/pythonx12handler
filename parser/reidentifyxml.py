import xml.etree.ElementTree as ET
import json
import argparse
import os
import sys

def reidentify_file(deid_xml, output_dir, mapping_json):
    input_basename = os.path.basename(deid_xml)
    name, ext = os.path.splitext(input_basename)
    if name.endswith('_deidentified'):
        name = name[:-13]  # remove 13 chars: len('_deidentified')
    os.makedirs(output_dir, exist_ok=True)
    reid_xml = os.path.join(output_dir, f"{name}_reidentified{ext}")

    # Check if input file exists
    if not os.path.exists(deid_xml):
        print(f"Error: Input file '{deid_xml}' does not exist.")
        return

    # Check if mapping file exists
    if not os.path.exists(mapping_json):
        print(f"Error: Mapping file '{mapping_json}' does not exist.")
        return

    with open(mapping_json, 'r') as f:
        phi_map = json.load(f)

    tree = ET.parse(deid_xml)
    root = tree.getroot()

    for elem in root.iter():
        if elem.tag == 'ele' and elem.text and elem.text in phi_map:
            elem.text = phi_map[elem.text]

    tree.write(reid_xml, encoding='utf-8', xml_declaration=True)
    print(f"Re-identification complete. Output: {reid_xml}")

def main():
    parser = argparse.ArgumentParser(description="Re-identify PHI fields in XML file(s) using a mapping file.")
    parser.add_argument('--input', '-i', required=True, help='Input (de-identified) XML file or folder path')
    args = parser.parse_args()

    input_path = args.input
    mapping_json = 'rules/phi_deid_reid_mapping.json'

    if os.path.isfile(input_path):
        output_dir = os.path.join('data', 'xml_files', 'reidentified')
        reidentify_file(input_path, output_dir, mapping_json)
    elif os.path.isdir(input_path):
        folder_name = os.path.basename(os.path.normpath(input_path))
        output_dir = os.path.join('data', 'xml_files', 'reidentified', folder_name)
        os.makedirs(output_dir, exist_ok=True)
        xml_files = [f for f in os.listdir(input_path) if f.lower().endswith('.xml')]
        if not xml_files:
            print(f"No XML files found in folder '{input_path}'.")
            sys.exit(1)
        for xml_file in xml_files:
            full_xml_path = os.path.join(input_path, xml_file)
            reidentify_file(full_xml_path, output_dir, mapping_json)
    else:
        print(f"Error: '{input_path}' is not a file or directory.")
        sys.exit(1)

if __name__ == "__main__":
    main()
