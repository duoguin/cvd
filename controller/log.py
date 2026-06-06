import os, datetime, traceback, functools, tabulate, pprint, textwrap
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Optional, Union, Any
from colorama import init, Fore, Style
init(autoreset=True)        # Reset color to default (autoreset=True handles this automatically)
import pandas as pd

COLOR_DICT = defaultdict(lambda: Style.RESET_ALL)
COLOR_DICT.update({
    'gray': Fore.LIGHTBLACK_EX,
    'orange': Fore.LIGHTYELLOW_EX,
    'red': Fore.RED,
    'green': Fore.GREEN,
    'blue': Fore.BLUE,
    'yellow': Fore.YELLOW,
    'magenta': Fore.MAGENTA,
    'cyan': Fore.CYAN,
    'white': Fore.WHITE, 
    'bold_blue': Style.BRIGHT + Fore.BLUE
})

class LogUtils:
    @staticmethod
    def format_user_input(prompt_text, prompt_color='blue', input_color='bold_blue'):
        """ styled user input """
        user_input = input(COLOR_DICT[prompt_color] + prompt_text + COLOR_DICT[input_color])
        print(Style.RESET_ALL, end='')
        return user_input
    
    @staticmethod
    def format_infos_with_pprint(infos:Any) -> str:
        return pprint.pformat(infos)
    
    @staticmethod
    def format_infos_basic(infos: Any, width: int=100, replace_whitespace: bool=False) -> str:
        """ prefer to format long string """
        if not isinstance(infos, str):
            infos = str(infos)
        
        # Wrap the text to the specified width
        wrapped_text = textwrap.fill(infos, width=width, replace_whitespace=replace_whitespace)
        
        # surround the text with a box
        lines = wrapped_text.split('\n')
        box_width = max(len(line) for line in lines) + 2
        top_border = '+' + '-' * (box_width+2) + '+'
        bottom_border = '+' + '-' * (box_width+2) + '+'
        boxed_text = top_border + '\n'
        for line in lines:
            boxed_text += '| ' + line.ljust(box_width) + ' |\n'
        boxed_text += bottom_border
        
        return boxed_text
    
    @staticmethod
    def format_infos_with_tabulate(
        infos: Any, 
        tablefmt='psql', maxcolwidths=100, headers='keys',
        color: str = None, auto_transform: bool = False
    ) -> str:
        """ format infos tables with tabulate """
        if isinstance(infos, dict):
            infos = pd.DataFrame([infos]).T
        elif isinstance(infos, pd.DataFrame):
            pass
        elif isinstance(infos, (list, tuple)):
            if isinstance(infos[0], (list, tuple)):
                infos = pd.DataFrame(infos)
            else:
                infos = pd.DataFrame([infos]).T
        elif isinstance(infos, (str, int, float)):
            infos = str(infos)
            infos = pd.DataFrame([infos.split('\n')]).T
        else:
            raise NotImplementedError
        # smartly .T the df?
        if auto_transform:
            if infos.shape[1] > infos.shape[0]:
                infos = infos.T
        
        infos_str = tabulate.tabulate(infos, tablefmt=tablefmt, maxcolwidths=maxcolwidths, headers=headers)

        if color is not None:
            infos_str = COLOR_DICT[color] + infos_str + Style.RESET_ALL
        return infos_str

    @staticmethod
    def format_str_with_color(text: str, color: str = 'blue') -> str:
        return COLOR_DICT[color] + text + Style.RESET_ALL


class SystemLogger:
    _log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "system_run.log")

    @classmethod
    def log(cls, layer: str, location: str, message: str, with_print: bool = False):
        # 1. Map layer to one of the 4 valid layers: UI, USER, BOT, API
        layer_lower = layer.lower()
        if layer_lower in ('ui', 'controller'):
            mapped_layer = 'UI'
        elif layer_lower == 'user':
            mapped_layer = 'USER'
        elif layer_lower == 'bot':
            mapped_layer = 'BOT'
        elif layer_lower in ('api', 'backend', 'database'):
            mapped_layer = 'API'
        elif layer_lower == 'utils':
            # Resolve calling layer using stack trace
            import inspect
            mapped_layer = 'BOT'  # default fallback
            frame = inspect.currentframe()
            while frame:
                filename = frame.f_code.co_filename.lower()
                if 'bot.py' in filename:
                    mapped_layer = 'BOT'
                    break
                elif 'user.py' in filename:
                    mapped_layer = 'USER'
                    break
                elif 'api.py' in filename or 'app.py' in filename:
                    mapped_layer = 'API'
                    break
                elif 'ui' in filename or 'run_flowagent_cli.py' in filename:
                    mapped_layer = 'UI'
                    break
                frame = frame.f_back
        else:
            mapped_layer = 'UI'

        # 2. Write log to file
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        formatted = f"{timestamp} [{mapped_layer}] [{location}] {message}"
        try:
            with open(cls._log_file, "a", encoding="utf-8") as f:
                f.write(formatted + "\n")
        except Exception:
            pass


class BaseLogger:
    """ Base logger without dumping to file """
    def __init__(self):
        pass
    def log(self, message:str, with_print=False, *args, **kwargs):
        if with_print:
            print(message)
        SystemLogger.log("ui", "BaseLogger.log", message)

    def debug(self, message:str, *args, **kwargs):
        print(message)
        SystemLogger.log("ui", "BaseLogger.debug", message)

    def log_to_stdout(self, message:str, color=None):
        colored_message = COLOR_DICT[color] + message + Style.RESET_ALL
        print(colored_message)
        
        layer = "ui"
        if color == 'red' or color == 'blue':
            layer = "user"
        elif color == 'orange' or color == 'green':
            layer = "bot"
        elif color == 'cyan' or color == 'yellow':
            layer = "api"
        
        SystemLogger.log(layer, f"BaseLogger.stdout({color})", message)


class FileLogger(BaseLogger):
    """ Local file logger """
    log_dir: Union[str, Path] = None
    log_fn: Union[str, Path] = None
    log_detail_fn: Union[str, Path] = None
    
    num_logs = 0
    logger_id: str = "tmp"
    def __init__(self, log_dir:str, t:datetime.datetime=None):
        """ 
        args:
          log_dir: str, the directory to save the log files
        """
        super().__init__()
        if not t:
            t = datetime.datetime.now()
        s_day = t.strftime("%Y-%m-%d")
        s_second = t.strftime("%Y-%m-%d_%H-%M-%S")
        s_millisecond = t.strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
        self.logger_id = s_millisecond
        
        self.log_dir = log_dir
        _log_subdir = f"{log_dir}/{s_day}"
        os.makedirs(_log_subdir, exist_ok=True)
        self.log_fn = f"{_log_subdir}/{s_millisecond}.log"
        log_detail_fn = f"{_log_subdir}/{s_millisecond}_detail.log"
        self.log_detail_fn = log_detail_fn
        
        self.num_logs = 0

    def log(self, message:str, add_line=True, with_print=False):
        self.num_logs += 1
        SystemLogger.log("ui", "FileLogger.log", message)
        with open(self.log_fn, 'a') as f:
            f.write(message + "\n" if add_line else "")
            f.flush()
        if with_print:
            print(message)
    
    def debug(self, message:str):
        SystemLogger.log("ui", "FileLogger.debug", message)
        with open(self.log_detail_fn, 'a') as f:
            f.write(f"{message}\n\n")
            f.flush()
        with open(self.log_detail_fn, 'a') as f:
            f.write(f"{message}\n\n")
            f.flush()



