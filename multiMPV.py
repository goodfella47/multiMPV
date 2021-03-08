import os
from tkinter import Tk
from tkinter.filedialog import askopenfilenames, askopenfilename
import configparser
from shutil import copytree
import ctypes


class mpvMulti:
    def __init__(self):
        self.__config_file = 'config.ini'
        self.__config = configparser.ConfigParser()
        self.__config.read(self.__config_file)
        self.__filetypes = [
            ("video format", ".mp4"),
            ("video format", ".MP4"),
            ("video format", ".mkv"),
            ("video format", ".MKV"),
            ("video format", ".avi"),
            ("video format", ".AVI"),
            ("text_format", ".txt")
        ]
        self.__default_video_scale = 'scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:-1:-1:color=black'
        self.__filenames = None
        self.__external_file_stack = None

        self._is_video_extension = lambda file: any([file.endswith(ext) for ext in self.__filetypes])

    def get_vids(self):

        vids = []
        # show an "Open" dialog box and return the path to the selected file
        files = askopenfilenames(initialdir="C:/", title='select video', filetypes=self.__filetypes)
        ends_with_txt = [file.endswith('.txt') for file in files]
        if any(ends_with_txt):
            for text_file in files:
                with open(text_file) as f:
                    for vid_path in f:
                        vids.append(vid_path.strip('\n'))
        else:
            vids = files
        assert len(vids) >= 1, 'no video files were selected'
        assert len(vids) <= 9, 'more than 9 video files were selected'
        return vids

    def assert_mpv_exe(self):
        def mpv_file_picker():
            ctypes.windll.user32.MessageBoxW(0, "Please select the MPV executable file", "MPV executable not found", 1)
            return askopenfilename(initialdir="/", title='Select MPV executable', filetypes=[("executable", ".exe")])

        mpv_path = None
        if 'MPV' in self.__config and 'mpv_destination' in self.__config['MPV']:
            mpv_path = self.__config['MPV']['mpv_destination']

        while not os.path.exists(mpv_path):
            mpv_path = mpv_file_picker()
            with open(self.__config_file, 'w') as conf:
                self.__config['MPV']['mpv_destination'] = mpv_path
                self.__config.write(conf)

        mpv_dir = os.path.dirname(mpv_path)
        print(mpv_dir)
        return mpv_dir

    def generate_scale(self, input_count):
        generated_scale = ''
        for i in range(1, input_count + 1):
            generated_scale += f'[vid{i}]' + self.__default_video_scale + f'[v{i}];'
        return generated_scale

    def get_mpv_command(self, vids):
        input_count = len(vids)
        generated_scale = self.generate_scale(input_count)
        external_file_stack = '"' + ';'.join(vids[1:]) + '"'

        if len(vids) == 1:
            mpv_command = f' "{vids[0]}"'
        elif len(vids) == 2:
            mpv_command = f' --profile="two" --lavfi-complex="[vid1]{self.__default_video_scale}[v1];[vid2]{self.__default_video_scale}[v2];[v1][v2]hstack[vo]" "{vids[0]}" --external-file={external_file_stack}'
        elif len(vids) == 3:
            mpv_command = f' --profile="three" --lavfi-complex="{generated_scale}[v1][v2][v3]xstack=inputs=3:layout=0_0|w0_0|0_h0:fill=black[vo]" "{vids[0]}" --external-files={external_file_stack}'
        elif len(vids) == 4:
            mpv_command = f' --profile="four" --lavfi-complex="{generated_scale}[v1][v2]hstack=inputs=2[top];[v3][v4]hstack=inputs=2[bottom];[top][bottom]vstack=inputs=2[vo]" "{vids[0]}" --external-files={external_file_stack}'
        elif len(vids) == 5:
            mpv_command = f' --profile="five" --lavfi-complex="{generated_scale}[v1][v2][v3][v4][v5]xstack=inputs=5:layout=0_0|w0_0|w0+w1_0|0_h0|w0_h0|w0+w1_h0:fill=black[vo]" "{vids[0]}" --external-files={external_file_stack}'
        elif len(vids) == 6:
            mpv_command = f' --profile="six" --lavfi-complex="{generated_scale}[v1][v2][v3]hstack=inputs=3[top];[v4][v5][v6]hstack=inputs=3[bottom];[top][bottom]vstack=inputs=2[vo]" "{vids[0]}" --external-files={external_file_stack}'
        elif len(vids) == 7:
            mpv_command = f' --profile="seven" --lavfi-complex="{generated_scale}[v1][v2][v3][v4][v5][v6][v7]xstack=inputs=7:layout=0_0|w0_0|w0+w1_0|0_h0|w0_h0|w0+w1_h0|0_h0+h1|w0_h0+h1|w0+w1_h0+h1:fill=black[vo]" "{vids[0]}" --external-files={external_file_stack}'
        elif len(vids) == 8:
            mpv_command = f' --profile="eight" --lavfi-complex="{generated_scale}[v1][v2][v3][v4][v5][v6][v7][v8]xstack=inputs=8:layout=0_0|w0_0|w0+w1_0|0_h0|w0_h0|w0+w1_h0|0_h0+h1|w0_h0+h1|w0+w1_h0+h1:fill=black[vo]" "{vids[0]}" --external-files={external_file_stack}'
        else:
            mpv_command = f' --profile="nine" --lavfi-complex="{generated_scale}[v1][v2][v3][v4][v5][v6][v7][v8][v9]xstack=inputs=9:layout=0_0|w0_0|w0+w1_0|0_h0|w0_h0|w0+w1_h0|0_h0+h1|w0_h0+h1|w0+w1_h0+h1[vo]" "{vids[0]}" --external-files={external_file_stack}'
        return mpv_command

    def copy_portable_config(self, mpv_path):
        copytree('portable_config', os.path.join(mpv_path, 'portable_config'))

    # def load_auto_play(self):
    #     if config['autoplay']['autoplay'] == 'on' and config['autoplay']['folder_path'] and config['autoplay']['autoplay_suffix']:
    #         autoplay_files = []
    #         autoplay_folder = config['autoplay']['folder_path']
    #         # autoplay_suffix = config['autoplay']['autoplay_suffix']
    #         if os.path.exists(autoplay_folder):
    #             for file in os.listdir('autoplay_folder'):
    #                 if is_video_extenstion(file):
    #                     autoplay_files.append(file)
    #                     print(os.path.join("/mydir", file))
    #         return autoplay_files

    def run(self):
        Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
        mpv_path = self.assert_mpv_exe()
        if not os.path.exists(os.path.join(mpv_path, 'portable_config')):
            self.copy_portable_config(mpv_path)
        vids = self.get_vids()
        mpv_command = self.get_mpv_command(vids)
        os.system(os.path.join(mpv_path, 'mpv.exe') + mpv_command)


if __name__ == '__main__':
    mpv_multi = mpvMulti()
    mpv_multi.run()
