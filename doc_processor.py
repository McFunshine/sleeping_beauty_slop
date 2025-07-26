"""Document processor module - Process papers with Mistral"""
import os
import utils as ut

class DocProcessor:
    """Process academic papers using Mistral"""
    
    def __init__(self, prompt_file_path: str):
        """
        Initialize the ScriptWriter with a prompt template.

        Args:
            prompt_file_path (str): Path to the file containing the prompt template.
        """
        self.prompt_template = ut.read_prompt_file(prompt_file_path)    

    def extract_key_points(self, paper_content):
        """Extract key points for script generation"""
        prompt = f"{self.prompt_template}\n\n{paper_content}"
        
        ut.call_mistral_api(prompt, api_key=os.getenv("MISTRAL_API_KEY"))