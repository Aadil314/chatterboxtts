import os

def split_script(filename, min_chars=2650):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    part_number = 1
    start_index = 0
    total_length = len(content)

    while start_index < total_length:
        # Calculate the point to start looking for a full stop
        search_index = start_index + min_chars
        
        # Find the next full stop after the minimum character count
        end_index = content.find('.', search_index)

        # If no more periods are found, take the remaining text
        if end_index == -1:
            end_index = total_length
        else:
            # Include the period in the current part
            end_index += 1

        # Extract the segment
        segment = content[start_index:end_index].strip()
        
        if segment:
            output_filename = f"{part_number}.txt"
            with open(output_filename, 'w', encoding='utf-8') as out_file:
                out_file.write(segment)
            print(f"Saved {output_filename} (Length: {len(segment)})")
            part_number += 1

        # --- OVERLAP LOGIC ---

        if end_index < total_length:
            # Look for the period BEFORE the one we just found.
            # We search backwards from end_index - 2 (to skip the period we just added).
            last_sentence_start = content.rfind('.', start_index, end_index - 300)
            
            if last_sentence_start == -1 or last_sentence_start <= start_index:
                # Fallback: if there's only one sentence in the block, move to end_index to avoid infinite loop
                start_index = end_index
            else:
                # Start the next block right after the previous sentence ended
                start_index = last_sentence_start + 1
        else:
            break

# Run the function
split_script('full_script.txt')