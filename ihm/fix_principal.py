#!/usr/bin/env python3
"""
Fix Principal.lad by adding CALL ROT5-9 and renumbering all subsequent lines
"""

# Template for CALL instruction
CALL_TEMPLATE = """[Line{line_num:05d}]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:CALL    T:-001 Size:001 E:{routine}
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:00
    {{0;00;00F7;-1;-1;-1;-1;00}}
    ###

"""

# Read original file
with open('temp_principal/Principal.lad', 'r') as f:
    content = f.read()

# Find where to insert (after Line00006 which contains CALL ROT4)
lines = content.split('\n')
insert_after_line = None
line_count = 1  # Start at Line00001

for i, line in enumerate(lines):
    if line.startswith('[Line'):
        # Extract line number
        current_num = int(line.split(']')[0].replace('[Line', ''))
        if current_num == 6:
            # Found Line00006 (CALL ROT4), need to find its end (###)
            for j in range(i+1, len(lines)):
                if lines[j].strip() == '###':
                    insert_after_line = j + 1  # Insert after the ### and blank line
                    break
            break

if insert_after_line is None:
    print("ERROR: Could not find Line00006 end")
    exit(1)

print(f"Will insert CALL ROT5-9 after line {insert_after_line}")

# Generate new CALL statements for ROT5-9
new_calls = []
for rot_num in range(5, 10):
    new_calls.append(CALL_TEMPLATE.format(
        line_num=rot_num + 2,  # Line00007 = ROT5, Line00008 = ROT6, etc.
        routine=f"ROT{rot_num}"
    ))

# Insert new calls
lines_before = lines[:insert_after_line]
lines_after = lines[insert_after_line:]

# Now renumber all lines after the insertion
new_lines_after = []
offset = 5  # We're adding 5 new lines

for line in lines_after:
    if line.startswith('[Line'):
        # Extract current line number and add offset
        old_num = int(line.split(']')[0].replace('[Line', ''))
        new_num = old_num + offset
        new_line = f"[Line{new_num:05d}]"
        new_lines_after.append(new_line)
    else:
        new_lines_after.append(line)

# Combine everything
final_lines = lines_before + [''.join(new_calls)] + new_lines_after

# Update line count at the top
final_lines[0] = 'Lines:00029'  # Original had 24, we add 5 = 29

# Write output
with open('v12_FINAL/Principal.lad', 'w') as f:
    f.write('\n'.join(final_lines))

print("✅ Principal.lad fixed!")
print("   - Added CALL ROT5-9 (Lines 7-11)")
print("   - Renumbered all subsequent lines (+5 offset)")
print("   - Total lines: 29")
