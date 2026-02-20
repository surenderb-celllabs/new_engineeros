from typing import List, Dict, Any, Optional
from pathlib import Path
import re, yaml, json

from app import ColoredLogger, Model, load_file, log_error
from app.phase_5.session_04 import STEP_PATH, State, ResponseType
from utils.file_management import load_yaml

from langchain_core.prompts import PromptTemplate
from langchain_core.messages import (
    AIMessage,
    SystemMessage,
    ToolMessage,
    RemoveMessage
)
from langgraph.config import get_stream_writer


USER_STORY_INDEX = 37

def count_tokens(text: str) -> int:
    """Estimate token count for a string."""
    return len(text.split()) // 4 * 3  # Rough estimate




class BaseNode:
    """Base class containing common methods for all node classes."""
    
    def __init__(self, 
                 agent_tools: List, 
                 system_prompt: bool,
                 prompt_data: str,
                 model = None, 
        ):
        self.node_logger = ColoredLogger(name=self.__class__.__name__)
        self.agent_tools = agent_tools
        self.model = model or Model.Nvidia.gpt_oss_20b
        self.system_prompt = system_prompt
        self._build_chain(prompt_data)

    def _build_chain(self, prompt_data: str):
        """(Re)build prompt + model chain at runtime"""
        if self.system_prompt:
            self.prompt = [SystemMessage(content=prompt_data)]
            self.model_chain = self.model
        else:
            self.prompt = PromptTemplate(template=prompt_data)
            self.model_chain = self.prompt | self.model
        
        # self.node_logger.debug("Build Chain Successful")

    def _log_section_header(self, title: str) -> None:
        """Log a formatted section header."""
        self.node_logger.debug(f"{'=' * 80}")
        self.node_logger.debug(f"{title:^80}")
        self.node_logger.debug(f"{'=' * 80}")
    
    def _log_separator(self) -> None:
        """Log a separator line."""
        self.node_logger.debug("-" * 80)
    
    def _log_input_tokens(self, messages: List) -> int:
        """Log input tokens from messages and return token count."""
        # self._log_section_header("INPUT TOKENS")
        total_input_tokens = 0
        
        # Count system prompt tokens
        system_token_count = count_tokens(str(self.prompt))
        total_input_tokens += system_token_count
        # self.node_logger.debug(f"System Prompt Tokens: {system_token_count}")
        
        # Count message tokens
        for i, msg in enumerate(messages):
            msg_content = getattr(msg, 'content', str(msg))
            msg_token_count = count_tokens(msg_content)
            total_input_tokens += msg_token_count
            msg_type = type(msg).__name__
            self.node_logger.debug(f"Message {i+1} [{msg_type}] Tokens: {msg_token_count}")
        
        # self.node_logger.debug(f"{'=' * 40}")
        # self.node_logger.debug(f"TOTAL INPUT TOKENS: {total_input_tokens}")
        # self._log_separator()
        
        return total_input_tokens
    
    def _log_output_tokens(self, response: AIMessage) -> int:
        """Log output tokens from response and return token count."""
        # self._log_section_header("OUTPUT TOKENS")
        
        # Try to get token usage from response metadata (LangChain)
        output_tokens = 0
        if hasattr(response, 'usage_metadata') and response.usage_metadata:
            output_tokens = response.usage_metadata.get('output_tokens', 0)
            # self.node_logger.debug(f"Model Reported Output Tokens: {output_tokens}")
        
        # Fallback to estimation
        if output_tokens == 0 and hasattr(response, 'content'):
            output_tokens = count_tokens(response.content)
            # self.node_logger.debug(f"Estimated Output Tokens: {output_tokens}")
        
        # Log tool calls if any
        if hasattr(response, 'tool_calls') and response.tool_calls:
            tool_call_tokens = count_tokens(str(response.tool_calls))
            self.node_logger.debug(f"Tool Calls Tokens: {tool_call_tokens}")
            output_tokens += tool_call_tokens
        
        # self.node_logger.debug(f"{'=' * 40}")
        # self.node_logger.debug(f"TOTAL OUTPUT TOKENS: {output_tokens}")
        # self._log_separator()
        
        return output_tokens
    
    def _yaml_string_with_fence_to_json(self, yaml_string: str) -> dict:
        try:
            cleaned = re.sub(r"^```yaml\s*|\s*```$", "", yaml_string.strip(), flags=re.MULTILINE)
            return yaml.safe_load(cleaned)
        except Exception as e:
            self.node_logger.error(f"[_yaml_string_with_fence_to_json]: {e}")

    def _yaml_string_with_fence_to_json_str(self, yaml_string: str) -> str:
        data = self._yaml_string_with_fence_to_json(yaml_string)
        return json.dumps(data, indent=None, ensure_ascii=False)
    
    def _write_message_on_writer_stream(self, message: str) -> None:
        """Stream the response on to the custom value"""
        writer = get_stream_writer()
        writer({
            "type": "ai_response",
            "response": message 
        })

    def _write_options_on_writer_stream(self, message: str) -> None:
        """Stream the response on to the custom value"""
        writer = get_stream_writer()
        writer({
            "type": ResponseType.ANSWER_SUGGESTION.value,
            "response": message 
        })



class ArchitectureRequirement(BaseNode):
    def __init__(self, agent_tools: List):
        goal = load_yaml("app/phase_5/problem.yaml")
        user_story = load_yaml("app/phase_5/user_stories.yaml")
        func_nonfunc = load_yaml("app/phase_5/func_nonfunc.yaml")

        prompt_path = Path(STEP_PATH) / "prompts/architecture_convo.md"
        prompt_data = load_file(str(prompt_path))
        
        # super().__init__(agent_tools, True, prompt_data, Model.Groq.gpt_oss_20b.bind_tools(agent_tools))
        super().__init__(agent_tools, True, prompt_data, Model.Groq.gpt_oss_20b.bind_tools(agent_tools))
        

    def __call__(self, state: State) -> State:
        try:

            self._log_section_header("User Story Analysis")
            # self.node_logger.warning(state["messages"])
            
            # Log input tokens
            # input_tokens = self._log_input_tokens(state["messages"])
            # self.node_logger.warning(f"Input Tokens Uses: {input_tokens}")

            response = self.model_chain.invoke(
                self.prompt + state["messages"]
            )
            self.node_logger.debug(response.tool_calls)
            self.node_logger.debug(response.content)

            self.node_logger.warning(f"Input: {response.usage_metadata["input_tokens"]}, Output: {response.usage_metadata["output_tokens"]}, Total: {response.usage_metadata["total_tokens"]}")

            if isinstance(state["messages"][-1], ToolMessage):
                RemoveMessage(state["messages"][-1].id)

            if response.tool_calls:
                return {
                    "messages": [response],
                    "convo_end": False
                }
            

            resp_json = self._yaml_string_with_fence_to_json(response.content)
            self.node_logger.debug(resp_json)
            
            if resp_json == None:
                return {
                    "messages": [AIMessage(content="")],
                    "resp_type": ResponseType.NONE.value,
                    "convo_end": False
                }
            
            # Log output tokens
            # output_tokens = self._log_output_tokens(response)
            # self.node_logger.warning(f"Output Tokens Uses: {output_tokens}")
            
            # self._write_message_on_writer_stream(resp_json["question"])
            # self._write_options_on_writer_stream(resp_json["suggestions"])

            convo_end = resp_json["convo_end"]
            resp_json.pop("convo_end")

            return {
                "messages": [AIMessage(content=json.dumps(resp_json))],
                "resp_type": ResponseType.MESSAGE.value,
                "convo_end": convo_end
            }
        
        except Exception as e:
            self.node_logger.error(e)
            return {
                "messages": "",
                "resp_type": ResponseType.ERROR.value,
                "convo_end": False
            }

class ArchitectureDocument(BaseNode):
    def __init__(self, agent_tools: List):
        prompt_path = Path(STEP_PATH) / "prompts/architecture_doc.md"
        prompt_data = load_file(str(prompt_path))
        # super().__init__(
        #     agent_tools, False, prompt_data,
        #     model=Model.Groq.gpt_oss_120b.bind_tools(tools=agent_tools)
        # )
        super().__init__(agent_tools, False, prompt_data, Model.Groq.gpt_oss_20b.bind_tools(agent_tools))

    def __call__(self, state: State) -> State:
        try:
            self._log_section_header("User Story Doc Generator")

            response = self.model_chain.invoke({
                "conversation": state["messages"]
            })
            self.node_logger.debug(response.content)
            self.node_logger.warning(f"Input: {response.usage_metadata["input_tokens"]}, Output: {response.usage_metadata["output_tokens"]}, Total: {response.usage_metadata["total_tokens"]}")

            resp_json = self._yaml_string_with_fence_to_json(response.content)
            self.node_logger.debug(resp_json)

            # self._log_input_tokens(state["messages"])
            # self._log_output_tokens(response=response)

            return {
                "messages": [AIMessage(content=json.dumps(resp_json))],
                "resp_type": ResponseType.APPROVAL.value,
                "convo_end": True,
                "start_convo_index": len(state["messages"]),
                
                "goals": resp_json,
                "current_index": 0,
            }



        except Exception as e:
            self.node_logger.error(e)

            return {
                "messages": [],
                "resp_type": ResponseType.ERROR.value,
                "convo_end": False,
            }

 

class ArchitectureTestDiagram(BaseNode):
    def __init__(self, agent_tools: List):
        prompt_path = Path(STEP_PATH) / "prompts/architecture_system.md"
        prompt_data = load_file(str(prompt_path))
        # super().__init__(
        #     agent_tools, False, prompt_data,
        #     model=Model.Groq.gpt_oss_120b.bind_tools(tools=agent_tools)
        # )
        super().__init__(agent_tools, False, prompt_data, Model.Groq.gpt_oss_20b)
        self.functional_requirements = load_yaml("app/phase_5/func_nonfunc.yaml")

    def __call__(self, state: State) -> State:
        try:
            self._log_section_header("User Story Doc Generator")

            response = self.model_chain.invoke({
                "func_non_func_requirements": self.functional_requirements
            })
            self.node_logger.debug(response.content)
            self.node_logger.warning(f"Input: {response.usage_metadata["input_tokens"]}, Output: {response.usage_metadata["output_tokens"]}, Total: {response.usage_metadata["total_tokens"]}")

            resp_json = self._yaml_string_with_fence_to_json(response.content)
            self.node_logger.debug(resp_json)

            # self._log_input_tokens(state["messages"])
            # self._log_output_tokens(response=response)

            return {
                "messages": [AIMessage(content=json.dumps(resp_json))],
                "resp_type": ResponseType.APPROVAL.value,
                "convo_end": True,
            }



        except Exception as e:
            self.node_logger.error(e)

            return {
                "messages": [],
                "resp_type": ResponseType.ERROR.value,
                "convo_end": False,
            }

class ArchitectureTestDiagram1(BaseNode):
    def __init__(self, agent_tools: List):
        prompt_path = Path(STEP_PATH) / "prompts/architecture_system_1.md"
        prompt_data = load_file(str(prompt_path))
        # super().__init__(
        #     agent_tools, False, prompt_data,
        #     model=Model.Groq.gpt_oss_120b.bind_tools(tools=agent_tools)
        # )
        super().__init__(agent_tools, False, prompt_data, Model.Groq.gpt_oss_20b)
        self.functional_requirements = load_yaml("app/phase_5/func_nonfunc.yaml")
        self.system_context_document = load_file("app/phase_5/architect_1.md")

    def __call__(self, state: State) -> State:
        try:
            self._log_section_header("User Story Doc Generator")

            response = self.model_chain.invoke({
                "func_non_func_requirements": self.functional_requirements,
                "system_context_document": self.system_context_document
            })
            self.node_logger.warning(response)
            self.node_logger.debug(response.content)
            self.node_logger.warning(f"Input: {response.usage_metadata["input_tokens"]}, Output: {response.usage_metadata["output_tokens"]}, Total: {response.usage_metadata["total_tokens"]}")

            resp_json = self._yaml_string_with_fence_to_json(response.content)
            self.node_logger.debug(resp_json)

            # self._log_input_tokens(state["messages"])
            # self._log_output_tokens(response=response)

            return {
                "messages": [AIMessage(content=json.dumps(resp_json))],
                "resp_type": ResponseType.APPROVAL.value,
                "convo_end": True,
            }



        except Exception as e:
            self.node_logger.error(e)

            return {
                "messages": [],
                "resp_type": ResponseType.ERROR.value,
                "convo_end": False,
            }


class ArchitectureTestDiagram2(BaseNode):
    def __init__(self, agent_tools: List):
        prompt_path = Path(STEP_PATH) / "prompts/architecture_system_2.md"
        prompt_data = load_file(str(prompt_path))
        # super().__init__(
        #     agent_tools, False, prompt_data,
        #     model=Model.Groq.gpt_oss_120b.bind_tools(tools=agent_tools)
        # )
        super().__init__(agent_tools, False, prompt_data, Model.Groq.gpt_oss_20b)
        self.functional_requirements = load_yaml("app/phase_5/func_nonfunc.yaml")
        self.system_context_document = load_file("app/phase_5/architect_1.md")
        self.system_container = load_file("app/phase_5/architect_2.md")

    def __call__(self, state: State) -> State:
        try:
            self._log_section_header("User Story Doc Generator")

            response = self.model_chain.invoke({
                "func_non_func_requirements": self.functional_requirements,
                "system_context_document": self.system_context_document,
                "container_document": self.system_container
            })
            self.node_logger.warning(response)
            self.node_logger.debug(response.content)
            self.node_logger.warning(f"Input: {response.usage_metadata["input_tokens"]}, Output: {response.usage_metadata["output_tokens"]}, Total: {response.usage_metadata["total_tokens"]}")

            resp_json = self._yaml_string_with_fence_to_json(response.content)
            self.node_logger.debug(resp_json)

            # self._log_input_tokens(state["messages"])
            # self._log_output_tokens(response=response)

            return {
                "messages": [AIMessage(content=json.dumps(resp_json))],
                "resp_type": ResponseType.APPROVAL.value,
                "convo_end": True,
            }



        except Exception as e:
            self.node_logger.error(e)

            return {
                "messages": [],
                "resp_type": ResponseType.ERROR.value,
                "convo_end": False,
            }

class ArchitectureTestDiagram3(BaseNode):
    def __init__(self, agent_tools: List):
        prompt_path = Path(STEP_PATH) / "prompts/architecture_system_3.md"
        prompt_data = load_file(str(prompt_path))
        # super().__init__(
        #     agent_tools, False, prompt_data,
        #     model=Model.Groq.gpt_oss_120b.bind_tools(tools=agent_tools)
        # )
        super().__init__(agent_tools, False, prompt_data, Model.Groq.gpt_oss_20b)
        self.functional_requirements = load_yaml("app/phase_5/func_nonfunc.yaml")
        self.system_context_document = load_file("app/phase_5/architect_1.md")
        self.system_container = load_file("app/phase_5/architect_2.md")
        self.system_component = load_file("app/phase_5/architect_3.md")

    def __call__(self, state: State) -> State:
        try:
            self._log_section_header("User Story Doc Generator")

            response = self.model_chain.invoke({
                "func_non_func_requirements": self.functional_requirements,
                "system_context_document": self.system_context_document,
                "container_document": self.system_container,
                "component_document": self.system_component
            })
            self.node_logger.warning(response)
            self.node_logger.debug(response.content)
            self.node_logger.warning(f"Input: {response.usage_metadata["input_tokens"]}, Output: {response.usage_metadata["output_tokens"]}, Total: {response.usage_metadata["total_tokens"]}")

            resp_json = self._yaml_string_with_fence_to_json(response.content)
            self.node_logger.debug(resp_json)

            # self._log_input_tokens(state["messages"])
            # self._log_output_tokens(response=response)

            return {
                "messages": [AIMessage(content=json.dumps(resp_json))],
                "resp_type": ResponseType.APPROVAL.value,
                "convo_end": True,
            }



        except Exception as e:
            self.node_logger.error(e)

            return {
                "messages": [],
                "resp_type": ResponseType.ERROR.value,
                "convo_end": False,
            }





