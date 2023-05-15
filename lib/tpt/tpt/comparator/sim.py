"""
SIM module
"""
import os
import subprocess
import re
import platform
from tpt.commons import TPTException


class SIM:
    """
    SIM class
    """
    @staticmethod
    def run(comparison_type, arg_list):
        """
        Execute SIM with comparison type and arg_list provided
        :param comparison_type:
        :param arg_list:
        :return:
        """
        return_value = None

        # Get the correct command
        command = None
        if comparison_type in ('text', 'text_only'):
            command = "sim_text"
        elif comparison_type == 'c':
            command = "sim_c"
        elif comparison_type == 'c++':
            command = "sim_c++"
        elif comparison_type == 'java':
            command = "sim_java"
        elif comparison_type == 'lisp':
            command = "sim_lisp"
        elif comparison_type == 'm2':
            command = "sim_m2"
        elif comparison_type == 'miranda':
            command = "sim_mira"
        elif comparison_type == 'pascal':
            command = "sim_pasc"
        elif comparison_type == 'assembler':
            command = "sim_8086"

        # Only continue if type is correct
        if command is not None:
            sys_name = platform.system()
            supported_platforms = {
                "Windows": "win32",
                "Darwin": "osx",
                "Linux": "linux"
            }

            if sys_name in supported_platforms:
                command = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'lib',
                                       'sim', supported_platforms[sys_name], command)
            else:
                raise TPTException("Unrecognized system")

            cmd_args = [command]
            for arg in arg_list:
                cmd_args.append(arg)

            # Call the method
            return_value = subprocess.check_output(cmd_args)

        return return_value

    def cmp_files(self, comparison_type, file_src, file_ref):
        """
        Execute comparison between source and reference files
        :param comparison_type:
        :param file_src:
        :param file_ref:
        :return:
        """
        # Call the SIM method
        result = self.run(comparison_type, ['-p', '-a', '-R', '-t', '1', file_src, file_ref])

        # Parse the output
        score_a_b = 0
        score_b_a = 0

        if result is not None:
            res = re.findall(r'(?P<f1>\S+) consists for (?P<p>\d+) % of (?P<f2>\S+) material',
                             result.decode('utf-8'))

            if res is not None and len(res) > 1:
                score_a_b = int(res[1][1])
                score_b_a = int(res[0][1])

        return score_a_b, score_b_a

    def get_diff(self, comparison_type, file_src, file_ref):
        """
        Get diff between source and reference file
        :param comparison_type:
        :param file_src:
        :param file_ref:
        :return:
        """
        # Call the SIM method
        diff = self.run(comparison_type, ['-d', '-s', file_src, file_ref])
        return diff
