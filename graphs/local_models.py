from enum import Enum

class LLMModelsAvailable(str, Enum):
    phi4 = "phi4"
    llama31 = "llama3.1"
    deepseekR17b = "deepseek-r1:7b"
    deepseekR214b = "deepseek-r1:14b"


DEFAULT_LOCAL_MODEL = LLMModelsAvailable.phi4