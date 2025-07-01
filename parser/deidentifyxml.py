import xml.etree.ElementTree as ET
import json
import argparse
import os
import sys

def deidentify_file(input_xml, output_dir, masking_json, mapping_json):
    input_basename = os.path.basename(input_xml)
    name, ext = os.path.splitext(input_basename)
    os.makedirs(output_dir, exist_ok=True)
    deid_xml = os.path.join(output_dir, f"{name}_deidentified{ext}")

    # Load nested masking rules
    with open(masking_json, 'r') as f:
        phi_rules = json.load(f)

    tree = ET.parse(input_xml)
    root = tree.getroot()

    phi_map = {}
    tag_counters = {}

    # Iterate over all loop elements
    for loop_elem in root.iter('loop'):
        loop_id = loop_elem.attrib.get('id')
        if loop_id in phi_rules:
            # For each ele under this loop
            for ele in loop_elem.iter('ele'):
                ele_id = ele.attrib.get('id')
                if ele_id in phi_rules[loop_id] and ele.text and ele.text.strip():
                    tag_key = (loop_id, ele_id)
                    tag_counters[tag_key] = tag_counters.get(tag_key, 0) + 1
                    masked_value = phi_rules[loop_id][ele_id]
                    if tag_counters[tag_key] > 1:
                        masked_value = f"{masked_value}_{tag_counters[tag_key]}"
                    phi_map[masked_value] = ele.text
                    ele.text = masked_value

    tree.write(deid_xml, encoding='utf-8', xml_declaration=True)

    with open(mapping_json, 'w') as f:
        json.dump(phi_map, f, indent=2)

    print(f"De-identification complete. Output: {deid_xml}")
    print(f"Mapping file saved as: {mapping_json}")

def main():
    parser = argparse.ArgumentParser(description="De-identify PHI fields in XML file(s).")
    parser.add_argument('--input', '-i', required=True, help='Input XML file or folder path')
    args = parser.parse_args()

    input_path = args.input
    masking_json = 'rules/phi_fields_to_mask.json'
    mapping_json = 'rules/phi_deid_reid_mapping.json'

    if os.path.isfile(input_path):
        # Single file
        output_dir = os.path.join('data', 'xml_files', 'deidentified')
        deidentify_file(input_path, output_dir, masking_json, mapping_json)
    elif os.path.isdir(input_path):
        # Folder: process all .xml files
        folder_name = os.path.basename(os.path.normpath(input_path))
        output_dir = os.path.join('data', 'xml_files', 'deidentified', folder_name)
        os.makedirs(output_dir, exist_ok=True)
        xml_files = [f for f in os.listdir(input_path) if f.lower().endswith('.xml')]
        if not xml_files:
            print(f"No XML files found in folder '{input_path}'.")
            sys.exit(1)
        for xml_file in xml_files:
            full_xml_path = os.path.join(input_path, xml_file)
            deidentify_file(full_xml_path, output_dir, masking_json, mapping_json)
    else:
        print(f"Error: '{input_path}' is not a file or directory.")
        sys.exit(1)

if __name__ == "__main__":
    main()





#
# import xml.etree.ElementTree as ET
# import json
# import argparse
# import os
# import sys
#
# def deidentify_file(input_xml, output_dir, masking_json, mapping_json):
#     input_basename = os.path.basename(input_xml)
#     name, ext = os.path.splitext(input_basename)
#     os.makedirs(output_dir, exist_ok=True)
#     deid_xml = os.path.join(output_dir, f"{name}_deidentified{ext}")
#
#     # Load masking rules
#     with open(masking_json, 'r') as f:
#         phi_rules = json.load(f)
#
#     tree = ET.parse(input_xml)
#     root = tree.getroot()
#
#     phi_map = {}
#     tag_counters = {}
#
#     for elem in root.iter():
#         if elem.tag == 'ele':
#             tag = elem.attrib.get('id')
#             if tag in phi_rules and elem.text and elem.text.strip():
#                 tag_counters[tag] = tag_counters.get(tag, 0) + 1
#                 masked_value = phi_rules[tag]
#                 if tag_counters[tag] > 1:
#                     masked_value = f"{masked_value}_{tag_counters[tag]}"
#                 phi_map[masked_value] = elem.text
#                 elem.text = masked_value
#
#     tree.write(deid_xml, encoding='utf-8', xml_declaration=True)
#
#     with open(mapping_json, 'w') as f:
#         json.dump(phi_map, f, indent=2)
#
#     print(f"De-identification complete. Output: {deid_xml}")
#     print(f"Mapping file saved as: {mapping_json}")
#
# def main():
#     parser = argparse.ArgumentParser(description="De-identify PHI fields in XML file(s).")
#     parser.add_argument('--input', '-i', required=True, help='Input XML file or folder path')
#     args = parser.parse_args()
#
#     input_path = args.input
#     masking_json = 'rules/phi_fields_to_mask.json'
#     mapping_json = 'rules/phi_deid_reid_mapping.json'
#
#     if os.path.isfile(input_path):
#         # Single file
#         output_dir = os.path.join('data', 'xml_files', 'deidentified')
#         deidentify_file(input_path, output_dir, masking_json, mapping_json)
#     elif os.path.isdir(input_path):
#         # Folder: process all .xml files
#         folder_name = os.path.basename(os.path.normpath(input_path))
#         output_dir = os.path.join('data', 'xml_files', 'deidentified', folder_name)
#         os.makedirs(output_dir, exist_ok=True)
#         xml_files = [f for f in os.listdir(input_path) if f.lower().endswith('.xml')]
#         if not xml_files:
#             print(f"No XML files found in folder '{input_path}'.")
#             sys.exit(1)
#         for xml_file in xml_files:
#             full_xml_path = os.path.join(input_path, xml_file)
#             deidentify_file(full_xml_path, output_dir, masking_json, mapping_json)
#     else:
#         print(f"Error: '{input_path}' is not a file or directory.")
#         sys.exit(1)
#
# if __name__ == "__main__":
#     main()
