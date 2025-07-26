"""Script writer module - Generate engaging scripts with Mistral LLM"""
import utils as ut
import os

class ScriptWriter:
    """Generate TikTok-style scripts from research"""
    
    def __init__(self, prompt_file_path: str):
        """
        Initialize the ScriptWriter with a prompt template.

        Args:
            prompt_file_path (str): Path to the file containing the prompt template.
        """
        self.prompt_template = ut.read_prompt_file(prompt_file_path)


    def generate_script(self, key_points):
        """Generate engaging script from paper content"""
        prompt = f"{self.prompt_template}\n\n{key_points}"
        return ut.call_mistral_api(prompt, api_key=os.getenv("MISTRAL_API_KEY"))

    
    def segment_script(self, script):
        """Segment script for image generation"""
        script_parts = script.split("\n")

        return [elm for elm in script_parts[2:-1] if len(elm) > 20 and elm[0] != "*"]