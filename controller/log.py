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
        import inspect
        mapped_layer = None
        
        # 1. Tự động phân giải tầng log (UI, CONTROLLER, BACKEND, AGENTS) dựa trên nguồn phát sinh trong stack trace
        frame = inspect.currentframe()
        while frame:
            filename = frame.f_code.co_filename.replace('\\', '/').lower()
            func_name = frame.f_code.co_name
            
            # Bỏ qua chính file cấu hình log
            if 'controller/log.py' in filename:
                frame = frame.f_back
                continue
                
            # Trường hợp đặc biệt ghi log hội thoại từ controller/base.py
            if 'controller/base.py' in filename and func_name in ('log_msg', 'log_to_stdout'):
                layer_lower = layer.lower() if layer else ""
                if layer_lower in ('user', 'bot', 'agents'):
                    mapped_layer = 'AGENTS'
                elif layer_lower in ('api', 'backend', 'database'):
                    mapped_layer = 'BACKEND'
                else:
                    mapped_layer = 'CONTROLLER'
                break
                
            # Phân loại dựa trên thư mục chứa file code
            if '/ui/' in filename or filename.endswith('/ui') or 'run_flowagent_cli.py' in filename:
                mapped_layer = 'UI'
                break
            elif '/controller/' in filename or filename.endswith('/controller'):
                mapped_layer = 'CONTROLLER'
                break
            elif '/backend/' in filename or filename.endswith('/backend'):
                mapped_layer = 'BACKEND'
                break
            elif '/agents/' in filename or filename.endswith('/agents'):
                if 'agents/api.py' in filename or 'agents\\api.py' in filename:
                    mapped_layer = 'BACKEND'
                else:
                    mapped_layer = 'AGENTS'
                break
                
            frame = frame.f_back
            
        # 2. Cơ chế dự phòng dựa trên tham số layer truyền vào
        if not mapped_layer:
            layer_lower = layer.lower() if layer else ""
            if 'ui' in layer_lower:
                mapped_layer = 'UI'
            elif 'controller' in layer_lower:
                mapped_layer = 'CONTROLLER'
            elif 'backend' in layer_lower or 'api' in layer_lower or 'database' in layer_lower:
                mapped_layer = 'BACKEND'
            elif 'agent' in layer_lower or 'bot' in layer_lower or 'user' in layer_lower:
                mapped_layer = 'AGENTS'
            else:
                mapped_layer = 'UI'

        # 3. Ghi log ra file
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
        
        layer = "controller"
        if color in ('red', 'blue', 'orange', 'green'):
            layer = "agents"
        elif color in ('cyan', 'yellow'):
            layer = "backend"
        
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



