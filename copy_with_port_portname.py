# copythefile.py
import sys
import os

def create_modified_script(template_script_path, zmq_port_name_val, zmq_port_val, output_dir):

    try:
        with open(template_script_path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Template script '{template_script_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading template script '{template_script_path}': {e}")
        sys.exit(1)

    definitions = [
        '\n',
        f'ZMQ_PORT_NAME = "{zmq_port_name_val}"\n',
        f'ZMQ_PORT = "{zmq_port_val}"\n',
        '\n'
    ]

    insert_index = 0
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        if stripped_line.startswith('import ') or stripped_line.startswith('from '):
            insert_index = i + 1
        elif insert_index > 0 and stripped_line and not stripped_line.startswith('#'):
            break
    if insert_index == 0 and lines and lines[0].startswith('#!'):
        insert_index = 1

    modified_lines = lines[:insert_index] + definitions + lines[insert_index:]

    # Determine output filename
    base_template_name = os.path.basename(template_script_path)
    template_root, template_ext = os.path.splitext(base_template_name)
    output_filename = f"{template_root}{template_ext}"
    output_script_path = os.path.join(output_dir, output_filename)

    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")

        with open(output_script_path, 'w') as f:
            f.writelines(modified_lines)
        
        print(f"Successfully created '{output_script_path}' with:")
        print(f"  ZMQ_PORT_NAME = \"{zmq_port_name_val}\"")
        print(f"  ZMQ_PORT = \"{zmq_port_val}\"")

    except Exception as e:
        print(f"Error writing output script '{output_script_path}': {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python3 copy_with_port_portname.py <New_ZMQ_PORT_NAME> <New_ZMQ_PORT> <TEMPLATE_SCRIPT_PATH> <OUTPUT_DIRECTORY>")
        print("Example: python3 copy_with_port_portname.py FUNBODY_REP_1 \"2355\" \"./templates/funbody_base.py\" \"./generated_scripts/\"")
        sys.exit(1)

    new_port_name_arg = sys.argv[1]
    new_bind_address_arg = sys.argv[2]
    template_script_path_arg = sys.argv[3]
    output_directory_arg = sys.argv[4]

    create_modified_script(template_script_path_arg, new_port_name_arg, new_bind_address_arg, output_directory_arg)