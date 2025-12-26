import os
import pyperclip  # 1. Import the library

def set_prompt():
    return """
Look up best midjourney prompting practices and generate high quality  image prompts that the highest audience retention chance and also fits the theme of the script.

Only use split screen ideas only when required. 
make primarily Historical or cinematic - we are making prompts for history based narrations.

Identify visual cues to insert the images
Output format:
table: quote (start words)...(end words), image prompt

General visual style (improve prompts based on specific scene):
cinematic historical realism, museum-grade oil painting aesthetic blended with photorealism, 
18th–19th century fine art influence, subdued natural color palette, earthy tone

Parameters (recommended defaults):
--ar 16:9 --raw --s 140 --q 2 --no readable text --no logos --no watermark --no modern elements

I have created start and end points,try to make visual cues in each start and end points - you can move texts between these markers if the narration would fit better in adjacent cue

Script/narration:

    """

# Photorealistic historical finance thriller, chiaroscuro documentary lighting, dominant artifact + mechanism prop
# cinematic historical realism, symbolic composition, museum-quality lighting, dramatic chiaroscuro, realistic textures (aged metal, parchment, stone)
# Empty private office of power, the single dominant subject is a leather portfolio locked with a small iron clasp resting beside a stopped pocket watch, piles of sealed documents in soft blur, one tight light shaft through dust, heavy chiaroscuro, tactile leather cracks and metal patina, restrained tension --ar 16:9 --style raw --s 200 --q 2 --no people --no faces --no modern elements --no text --no logos --no cartoon
def split_script(filename, min_chars=150):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    part_number = 1
    start_index = 0
    total_length = len(content)
    result = []

    prompt = set_prompt()

    while start_index < total_length:
        search_index = start_index + min_chars
        end_index = content.find('.', search_index)

        if end_index == -1:
            end_index = total_length
        else:
            end_index += 1

        segment = content[start_index:end_index].strip()
        result.append(segment)
        start_index = end_index


    printed_lines = []

    for i, text in enumerate(result[0:10]):
        line = "START->"+text+"<-END"
        print(line)
        printed_lines.append(line)

    # Join the lines with a newline and copy to clipboard
    clipboard_content = prompt+"\n".join(printed_lines)
    pyperclip.copy(clipboard_content)
    
    print("\n--- Success: The text above has been copied to your clipboard! ---")
    print(f"Total Segments: {len(result)}")

# Run the function
split_script('full_script.txt')
