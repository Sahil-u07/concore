# copythefile.py
import sys
import os
import subprocess
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def run_copy_script(template_script_path_arg, new_port_name_arg, new_zmq_port_arg, output_directory_arg, python_exe):
    base_template_name = os.path.basename(template_script_path_arg)
    template_root, template_ext = os.path.splitext(base_template_name)
    output_filename = f"{template_root}{template_ext}"
    expected_output_path = os.path.join(output_directory_arg, output_filename)

    if os.path.exists(expected_output_path):
        logging.info(f"Specialized script '{expected_output_path}' already exists. Skipping generation.")
        return output_filename
    
    copy_script_path = os.path.join(".","copy_with_port_portname.py")

    cmd = [
        python_exe,
        copy_script_path,
        new_port_name_arg,
        new_zmq_port_arg,
        template_script_path_arg,
        output_directory_arg
    ]
    logging.info(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding='utf-8')
        logging.info(f"Successfully generated '{output_filename}' using copy_with_port_portname.py.")
        if result.stdout: logging.debug(f"copy_with_port_portname.py stdout:\n{result.stdout}")
        if result.stderr: logging.warning(f"copy_with_port_portname.py stderr:\n{result.stderr}")
        return output_filename
    except subprocess.CalledProcessError as e:
        logging.error(f"Error calling copy_with_port_portname.py for '{template_script_path_arg}' with port_name '{new_port_name_arg}':")
        logging.error(f"Command: {' '.join(e.cmd)}")
        logging.error(f"Return code: {e.returncode}")
        logging.error(f"Stdout: {e.stdout}")
        logging.error(f"Stderr: {e.stderr}")
        return None
    except FileNotFoundError:
        logging.error(f"Error: Python executable or copy_with_port_portname.py script not found.")
        logging.error(f"Attempted command: {' '.join(cmd)}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred while trying to run copy_script: {e}")
        return None


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