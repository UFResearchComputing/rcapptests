import os
import hashlib

import config

def read_bash_code(file_path):
    with open(file_path, 'r') as file:
        bash_code = file.read()
    return bash_code

def addTrap(file_path):
    bash_code = read_bash_code(config.TRAP_FILE)
    with open(file_path, 'r') as file:
        lines = file.readlines()
    modified_lines = []
    addedTrap = False

    for line in lines:
        if line.startswith('# BEGIN'):
            return
        if addedTrap or line.startswith('#') or line.startswith('\n'):
            modified_lines.append(line)
        else:
            modified_lines.append(bash_code + "\n")
            modified_lines.append(line)
            addedTrap = True

    input_bytes = file_path.encode('utf-8')
    # Compute the SHA-256 hash
    sha_hash = hashlib.sha256(input_bytes)

    # Return the hexadecimal representation of the hash
    newPath = config.TEMP_TEST_FILE + sha_hash.hexdigest()

    with open(newPath, 'w') as file:
        file.writelines(modified_lines)
    return newPath

def removeTrap(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    modified_lines = []
    inTrapBlock = False

    for line in lines:
        if line.startswith('# BEGIN'):
            inTrapBlock = True
        if line.startswith('# END'):
            inTrapBlock = False
            continue

        if not inTrapBlock:
            modified_lines.append(line)

    with open(file_path, 'w') as file:
        file.writelines(modified_lines)