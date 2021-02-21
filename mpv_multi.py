import os
from tkinter import Tk
from tkinter.filedialog import askopenfilenames

mpv_dir = 'mpv_binaries\\'

Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
filenames = askopenfilenames(initialdir="C:/",title='select video', filetypes=[
                    ("all video format", ".mp4"),
                    ("all video format", ".MP4"),
                ])  # show an "Open" dialog box and return the path to the selected file
assert len(filenames) >= 1, 'no video files were selected'
assert len(filenames) <= 9, 'more than 9 video files were selected'
external_file_stack = '"' + ';'.join(filenames[1:]) + '"'
scale = 'scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:-1:-1:color=black'
input_count = len(filenames)


def generate_scale(input_count):
    generated_scale = ''
    for i in range(1, input_count + 1):
        generated_scale += f'[vid{i}]' + scale + f'[v{i}];'
    return generated_scale


vid_scale = generate_scale(input_count)
if len(filenames) == 1:
    command = f'mpv "{filenames[0]}"'
elif len(filenames) == 2:
    command = f'mpv --profile="two" --lavfi-complex="[vid1]{scale}[v1];[vid2]{scale}[v2];[v1][v2]hstack[vo]" "{filenames[0]}" --external-file={external_file_stack}'
elif len(filenames) == 3:
    command = f'mpv --profile="five" --lavfi-complex="{vid_scale}[v1][v2][v3]xstack=inputs=3:layout=0_0|w0_0|0_h0:fill=black[vo]" "{filenames[0]}" --external-files={external_file_stack}'

elif len(filenames) == 4:
    command = f'mpv --profile="four" --lavfi-complex="{vid_scale}[v1][v2]hstack=inputs=2[top];[v3][v4]hstack=inputs=2[bottom];[top][bottom]vstack=inputs=2[vo]" "{filenames[0]}" --external-files={external_file_stack}'
elif len(filenames) == 5:
    command = f'mpv --profile="five" --lavfi-complex="{vid_scale}[v1][v2][v3][v4][v5]xstack=inputs=5:layout=0_0|w0_0|w0+w1_0|0_h0|w0_h0|w0+w1_h0:fill=black[vo]" "{filenames[0]}" --external-files={external_file_stack}'
elif len(filenames) == 6:
    command = f'mpv --profile="six" --lavfi-complex="{vid_scale}[v1][v2][v3]hstack=inputs=3[top];[v4][v5][v6]hstack=inputs=3[bottom];[top][bottom]vstack=inputs=2[vo]" "{filenames[0]}" --external-files={external_file_stack}'
elif len(filenames) == 7:
    command = f'mpv --profile="seven" --lavfi-complex="{vid_scale}[v1][v2][v3][v4][v5][v6][v7]xstack=inputs=7:layout=0_0|w0_0|w0+w1_0|0_h0|w0_h0|w0+w1_h0|0_h0+h1|w0_h0+h1|w0+w1_h0+h1:fill=black[vo]" "{filenames[0]}" --external-files={external_file_stack}'
elif len(filenames) == 8:
    command = f'mpv --profile="eight" --lavfi-complex="{vid_scale}[v1][v2][v3][v4][v5][v6][v7][v8]xstack=inputs=8:layout=0_0|w0_0|w0+w1_0|0_h0|w0_h0|w0+w1_h0|0_h0+h1|w0_h0+h1|w0+w1_h0+h1:fill=black[vo]" "{filenames[0]}" --external-files={external_file_stack}'
else:
    command = f'mpv --profile="nine" --lavfi-complex="{vid_scale}[v1][v2][v3][v4][v5][v6][v7][v8][v9]xstack=inputs=9:layout=0_0|w0_0|w0+w1_0|0_h0|w0_h0|w0+w1_h0|0_h0+h1|w0_h0+h1|w0+w1_h0+h1[vo]" "{filenames[0]}" --external-files={external_file_stack}'

os.system(mpv_dir + command)
