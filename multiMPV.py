import os
import sys
from tkinter import Tk
from tkinter.filedialog import askopenfilenames, askopenfilename
from tkinter import messagebox
import configparser
import subprocess

FILE_EXTENSION = ".mmpv"


class multiMPV:
    def __init__(self, cwd):
        self.__cwd = cwd
        self.__config_file_path = os.path.join(cwd, 'config.ini')
        self.__first_run = False
        self.__config = configparser.ConfigParser()
        self.__config.read(self.__config_file_path)
        self.__filetypes = [
            ("video file", FILE_EXTENSION),
            ("video file", ".mp4"),
            ("video file", ".MP4"),
            ("video file", ".mkv"),
            ("video file", ".MKV"),
            ("video file", ".avi"),
            ("video file", ".AVI"),
            ("video file", ".txt")
        ]
        if 'first_run' in self.__config['MPV']:
            self.__first_run = True
            with open(self.__config_file_path, 'w') as conf:
                self.__config.remove_option('MPV', 'first_run')
                self.__config.write(conf)
        video_scale = self.__config['MPV']['video_scale']
        force_original_aspect_ratio = self.__config['MPV']['force_original_aspect_ratio']
        self.__video_scale = f'scale={video_scale}:force_original_aspect_ratio={force_original_aspect_ratio},pad={video_scale}:-1:-1:color=black'
        self.__relative_vid_path = self.__config['MPV']['relative_vid_path']
        self.__filenames = None
        self.__external_file_stack = None

    def _is_video_extension(self, file):
        return any([file.endswith(ext) for ext in self.__filetypes])

    def get_vids(self):
        vids = []
        # show an "Open" dialog box and return the path to the selected file
        files = askopenfilenames(initialdir="C:/", title='select video', filetypes=self.__filetypes)
        txt_files = [file for file in files if file.endswith('.txt') or file.endswith(FILE_EXTENSION)]
        vid_files = [file for file in files if not file.endswith('.txt') and not file.endswith(FILE_EXTENSION)]
        vid_from_txt = self.get_vids_from_txt(txt_files)
        vids.extend(vid_from_txt)
        vids.extend(vid_files)
        return vids

    @staticmethod
    def get_vids_from_txt(txt_files):
        vids = []
        for txt_file in txt_files:
            with open(txt_file) as f:
                for vid in f:
                    vid_path = vid.strip('\n')
                    vids.append(vid_path)
        return vids

    def assert_vids_location(self, vids):
        assert len(vids) >= 1, 'no video files were selected'
        assert len(vids) <= 9, 'multiMPV support up to 9 video files'
        for i, vid in enumerate(vids):
            if os.path.exists(os.path.join(self.__relative_vid_path, vid)):
                vids[i] = os.path.join(self.__relative_vid_path, vids[i])
            else:
                if not os.path.exists(vid):
                    messagebox.showwarning(title="Exception", message=f"{vid} was not found")
                    sys.exit()

    def _assert_mpv_exe(self):
        def mpv_file_picker():
            mbox_select = messagebox.askokcancel(title="mpv executable not found",
                                                 message="Please select an mpv executable file")
            if not mbox_select:
                sys.exit()
            filenames = askopenfilename(initialdir="/", title='Select mpv executable',
                                        filetypes=[("executable", ".exe")])
            if not filenames:
                sys.exit()
            return filenames

        mpv_path = self.__config['MPV']['mpv_path']

        if not os.path.exists(mpv_path):
            mpv_path = mpv_file_picker()
            try:
                with open(self.__config_file_path, 'w') as conf:
                    self.__config['MPV']['mpv_path'] = mpv_path
                    self.__config.write(conf)
                if self.__first_run:
                    sys.exit()
            except OSError:
                warning = f'Failed to save the mpv path. please change the "mpv_path" field in the config.ini file'
                messagebox.showwarning(title="Warning", message=warning)

        mpv_dir = os.path.dirname(mpv_path)
        return mpv_dir

    def _generate_scale(self, input_count):
        generated_scale = ''
        for i in range(1, input_count + 1):
            generated_scale += f'[vid{i}]' + self.__video_scale + f'[v{i}];'
        return generated_scale

    def _get_mpv_command(self, vids):
        input_count = len(vids)
        input_name = f"input\\input{input_count}.conf"
        input_conf = f'--input-conf="{os.path.join(self.__cwd, input_name)}"'
        script_name = f"scripts\\cycle-commands.lua"
        script = f'--script="{os.path.join(self.__cwd, script_name)}"'
        generated_scale = self._generate_scale(input_count)
        external_file_stack = '"' + ';'.join(vids[1:]) + '"'

        if len(vids) == 1:
            mpv_command = f' "{vids[0]}"'
        elif len(vids) == 2:
            mpv_command = f' {script} {input_conf} --lavfi-complex="[vid1]{self.__video_scale}[v1];[vid2]{self.__video_scale}[v2];[v1][v2]hstack[vo]" "{vids[0]}" --external-file={external_file_stack}'
        elif len(vids) == 3:
            mpv_command = f' {script} {input_conf} --lavfi-complex="{generated_scale}[v1][v2][v3]xstack=inputs=3:layout=0_0|w0_0|0_h0:fill=black[vo]" "{vids[0]}" --external-files={external_file_stack}'
        elif len(vids) == 4:
            mpv_command = f' {script} {input_conf} --lavfi-complex="{generated_scale}[v1][v2]hstack=inputs=2[top];[v3][v4]hstack=inputs=2[bottom];[top][bottom]vstack=inputs=2[vo]" "{vids[0]}" --external-files={external_file_stack}'
        elif len(vids) == 5:
            mpv_command = f' {script} {input_conf} --lavfi-complex="{generated_scale}[v1][v2][v3][v4][v5]xstack=inputs=5:layout=0_0|w0_0|w0+w1_0|0_h0|w0_h0|w0+w1_h0:fill=black[vo]" "{vids[0]}" --external-files={external_file_stack}'
        elif len(vids) == 6:
            mpv_command = f' {script} {input_conf} --lavfi-complex="{generated_scale}[v1][v2][v3]hstack=inputs=3[top];[v4][v5][v6]hstack=inputs=3[bottom];[top][bottom]vstack=inputs=2[vo]" "{vids[0]}" --external-files={external_file_stack}'
        elif len(vids) == 7:
            mpv_command = f' {script} {input_conf} --lavfi-complex="{generated_scale}[v1][v2][v3][v4][v5][v6][v7]xstack=inputs=7:layout=0_0|w0_0|w0+w1_0|0_h0|w0_h0|w0+w1_h0|0_h0+h1|w0_h0+h1|w0+w1_h0+h1:fill=black[vo]" "{vids[0]}" --external-files={external_file_stack}'
        elif len(vids) == 8:
            mpv_command = f' {script} {input_conf} --lavfi-complex="{generated_scale}[v1][v2][v3][v4][v5][v6][v7][v8]xstack=inputs=8:layout=0_0|w0_0|w0+w1_0|0_h0|w0_h0|w0+w1_h0|0_h0+h1|w0_h0+h1|w0+w1_h0+h1:fill=black[vo]" "{vids[0]}" --external-files={external_file_stack}'
        else:
            mpv_command = f' {script} {input_conf} --lavfi-complex="{generated_scale}[v1][v2][v3][v4][v5][v6][v7][v8][v9]xstack=inputs=9:layout=0_0|w0_0|w0+w1_0|0_h0|w0_h0|w0+w1_h0|0_h0+h1|w0_h0+h1|w0+w1_h0+h1[vo]" "{vids[0]}" --external-files={external_file_stack}'
        return mpv_command

    def run(self, txt_file=None):
        Tk().withdraw()  # keep the root window from appearing
        mpv_path = self._assert_mpv_exe()
        if not txt_file:
            vids = self.get_vids()
        else:
            vids = self.get_vids_from_txt(txt_file)
        self.assert_vids_location(vids)
        mpv_command = self._get_mpv_command(vids)
        cmd_command = os.path.join(mpv_path, 'mpv.exe') + mpv_command
        print(cmd_command)
        subprocess.run(cmd_command)


if __name__ == '__main__':
    cwd = sys.path[0]
    if cwd.endswith(".zip"):
        cwd = os.path.dirname(cwd)
    multi_mpv = multiMPV(cwd)
    if len(sys.argv) != 2:
        multi_mpv.run()
    else:
        txt_file = sys.argv[1]
        if not isinstance(txt_file, list):
            txt_file = [txt_file]
        multi_mpv.run(txt_file)
