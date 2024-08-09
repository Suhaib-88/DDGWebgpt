from pydantic import create_model
from src.utils.web_search import WebSearch
from groq import Groq
import cohere
import json,os
from dotenv import find_dotenv,load_dotenv
from inspect import Parameter
import inspect
from typing import Dict,List, Any

load_dotenv(find_dotenv())

class Apputils:
    @staticmethod
    def jsonschema(f) -> Dict:
        """
        Generate a JSON schema for the input parameters of the given function.

        Parameters:
            f (FunctionType): The function for which to generate the JSON schema.

        Returns:
            Dict: A dictionary containing the function name, description, and parameters schema.
        """
        # Replace inspect._empty with Any
        kw = {n: (Any if o.annotation == inspect._empty else o.annotation, 
                  ... if o.default == Parameter.empty else o.default)
              for n, o in inspect.signature(f).parameters.items()}
        
        # Create a custom Pydantic model with arbitrary types allowed
        class Config:
            arbitrary_types_allowed = True
        
        s = create_model(f'Input for `{f.__name__}`', **kw, __config__=Config).schema()
        print(dict(name=f.__name__, description=f.__doc__, parameters=s))
        return dict(name=f.__name__, description=f.__doc__, parameters=s)
    @staticmethod
    def wrap_functions():
        return [
            Apputils.jsonschema(WebSearch.retrieve_web_search_results),
            Apputils.jsonschema(WebSearch.web_search_text),
            Apputils.jsonschema(WebSearch.web_search_pdf),
            Apputils.jsonschema(WebSearch.web_search_image),
            Apputils.jsonschema(WebSearch.web_search_video),
            Apputils.jsonschema(WebSearch.web_search_news),
            Apputils.jsonschema(WebSearch.web_search_map)

        ]
    @staticmethod
    def execute_json_function(response):
        func_name=response.choices[0].message.function_call.name
        func_args=json.loads(response.choices[0].message.function_call.name)

        if func_name=="retrieve_web_search_results":
            result= WebSearch.retrieve_web_search_results(**func_args)

        elif func_name=="web_search_text":
            result= WebSearch.web_search_text(**func_args)
        
        elif func_name=="web_search_pdf":
            result= WebSearch.web_search_pdf(**func_args)

        elif func_name=="web_search_image":
            result= WebSearch.web_search_image(**func_args)
        
        elif func_name=="web_search_videos":
            result= WebSearch.web_search_video(**func_args)
        
        elif func_name=="web_search_news":
            result= WebSearch.web_search_news(**func_args)

        elif func_name=="web_search_map":
            result= WebSearch.web_search_maps(**func_args)

        else:
            raise ValueError(f"Function: {func_name} not found")

        return result
    
    def ask_llm_func_caller(cohere_model,messages,tools,chat_history):
        co = cohere.Client(api_key="acMOejrzouLs3cDYQf3zuxQsNmty2Il3FPq6tNQt")
        response=co.chat(
                message=messages,
                model=cohere_model,
                tools=tools,
                chat_history=chat_history,
                force_single_step=True
            )

        
        return response


    @staticmethod
    def ask_llm_chatbot(gpt_model,temperature,messages):
        client= Groq(api_key=os.getenv("GROQ_API"))
        response=client.chat.completions.create(
                messages=messages,
                model=gpt_model,
                temperature=temperature
            )

        return response