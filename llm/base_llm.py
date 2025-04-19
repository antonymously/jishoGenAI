class BaseLLM:
    def __init__(self):
        pass

    def invoke(self, prompt: str) -> str:
        raise NotImplementedError


class ChatLLM(BaseLLM):
    '''
    A stateful chat LLM.
    Chat history is retained within the object.
    '''

    def __init__(self, system_message: str = ""):
        super().__init__()
        self.system_message = system_message

    def invoke(self, prompt: str) -> str:
        raise NotImplementedError

# TODO: add invoke_stream