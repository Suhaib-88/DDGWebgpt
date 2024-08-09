from dotenv import load_dotenv
from groq import Groq
import yaml,os
from pyprojroot import here

load_dotenv()

class LoadConfig:
    def __init__(self) -> None:
        with open(here("config.yaml")) as cfg:
            app_config= yaml.load(cfg,Loader= yaml.FullLoader)

        self.gpt_model=app_config['gpt_model']
        self.temperature= app_config['temperature']
        self.llm_func_caller=app_config['llm_function_caller_system_role']
        self.llm_system_role=app_config['llm_system_role']
