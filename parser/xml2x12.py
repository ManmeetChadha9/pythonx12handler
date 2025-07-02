import sys
import os

from pyx12.xmlx12_simple import convert

def find_mode_and_relpath(input_path):
    # Find if 'deidentified' or 'reidentified' is in the path and return mode and relative path after that
    parts = input_path.replace("\\", "/").split('/')
    if 'deidentified' in parts:
        idx = parts.index('deidentified')
        mode = 'deidentified'
    elif 'reidentified' in parts:
        idx = parts.index('reidentified')
        mode = 'reidentified'
    else:
        return '', input_path  # Default: no mode, full path as relpath
    after = parts[idx+1:]
    relpath = os.path.join(*after) if after else ''  # Only join if after is not empty
    return mode, relpath


def convert_file(input_xml, input_root, output_root, mode, rel_folder):
    input_basename = os.path.basename(input_xml)
    name, ext = os.path.splitext(input_basename)
    # Remove suffixes for output file naming
    if name.endswith('_deidentified'):
        name = name[:-13]
    elif name.endswith('_reidentified'):
        name = name[:-13]
    # Output dir: data/x12_files/<mode>/<rel_folder>
    output_dir = os.path.join(output_root, mode, rel_folder)
    os.makedirs(output_dir, exist_ok=True)
    output_edi = os.path.join(output_dir, f"{name}.x12")
    with open(output_edi, 'w', encoding='utf-8') as f_out:
        convert(input_xml, f_out)
    print(f"Conversion complete. Output written to {output_edi}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python parser/xml2x12.py <input.xml or input_folder>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_root = os.path.join('data', 'x12_files')

    if os.path.isfile(input_path):
        # For a single file, determine mode and rel_folder
        abs_input_path = os.path.abspath(input_path)
        mode, rel_folder = find_mode_and_relpath(os.path.dirname(abs_input_path))
        convert_file(abs_input_path, '', output_root, mode or '', rel_folder or '')
    elif os.path.isdir(input_path):
        abs_input_path = os.path.abspath(input_path)
        mode, rel_folder = find_mode_and_relpath(abs_input_path)
        for dirpath, _, files in os.walk(abs_input_path):
            for file in files:
                if file.lower().endswith('.xml'):
                    full_xml_path = os.path.join(dirpath, file)
                    # Find relative dir after mode
                    rel_dir = os.path.relpath(dirpath, abs_input_path)
                    # If rel_dir is '.', skip it
                    final_rel_folder = os.path.join(rel_folder, rel_dir) if rel_dir != '.' else rel_folder
                    convert_file(full_xml_path, '', output_root, mode or '', final_rel_folder or '')
    else:
        print(f"Error: '{input_path}' is not a file or directory.")
        sys.exit(1)

if __name__ == "__main__":
    main()
