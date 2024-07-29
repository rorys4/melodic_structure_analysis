import re

# Function to extract the tune number and title from its ABC representation.
def extract_abc_info(abc_string):
    lines = abc_string.split('\n')
    title = None
    number = None
    for line in lines:
        if line.startswith('X:'):
            number = line[2:].strip()
        elif line.startswith('T:'):
            title = line[2:].strip()
    return title, number


def remove_macros(abc_string):
    # Split the input into lines
    lines = abc_string.split('\n')
    # To store the uppercase letters to be removed and the processed lines
    letters_to_remove = set()
    # Find macro flags to remove.
    for line in lines:
        if line.startswith('m:'):
            # Find the uppercase letter immediately after 'm:'
            match = re.search(r'm:\s*([A-Z])', line)
            if match:
                letter = match.group(1)
                letters_to_remove.add(letter)
    # Remove all instances of the letters to be removed from the processed string
    processed_lines = []
    for line in lines:
        if not re.search("^[A-Z]:", line):
            for letter in letters_to_remove:
                line = line.replace(letter, '')
            processed_lines.append(line)
        else:
            processed_lines.append(line)
    processed_string = '\n'.join(processed_lines)
    lines = processed_string.split('\n')
    processed_lines = []
    for line in lines:
        if not line.startswith('m:'):
            processed_lines.append(line)
    processed_string = '\n'.join(processed_lines)
    return processed_string


def clean_abc(abc_content):
    # Remove ABC macros
    abc_content = remove_macros(abc_content)
    # Substitute repeat shorthand.
    abc_content = abc_content.replace("::", ":||:")
    # Remove strange characters.
    lines = abc_content.split('\n')
    # Remove all instances of W
    processed_lines = []
    for line in lines:
        if not re.search("^[A-Z]:", line):
            line = line.replace('W', '')
            line = line.replace('\"   ~\"', '')
            processed_lines.append(line)
        else:
            processed_lines.append(line)
    processed_string = '\n'.join(processed_lines)
    return processed_string


# Function to read the contents of an abc file, strip any header material that does not form part of a description of a
# tune, and return a list containing a string for each tune in the abc file.
def read_abc_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    # Split the content into lines
    lines = content.split('\n')
    # List of common metadata fields in .abc files
    metadata_fields = {'X:', 'T:', 'M:', 'K:', 'L:', 'Q:', 'C:', 'R:', 'N:', 'P:'}
    # Identify the end of the header section
    header_end_index = 0
    for i, line in enumerate(lines):
        if line.strip()[:2] in metadata_fields:
            header_end_index = i
            break
    # The tunes start at the header end index
    tunes_content = '\n'.join(lines[header_end_index:])
    # Split the remaining content into tunes based on double newlines (indicating a blank line)
    tunes = tunes_content.strip().split('\n\n')
    # Clean up any extra newlines or leading/trailing spaces in each tune
    tunes = [tune.strip() for tune in tunes if tune.strip()]
    return tunes
