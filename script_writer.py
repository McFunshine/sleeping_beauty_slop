"""Script writer module - Generate engaging scripts with Mistral LLM"""
import utils as ut
import os
import re

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
        # Replace the placeholder in the template
        prompt = self.prompt_template.replace("[Insert summary here]", key_points)
        
        print(f"DEBUG: Sending prompt to Mistral...")
        print(f"DEBUG: Key points preview: {key_points[:100]}...")
        
        full_response = ut.call_mistral_api(prompt, api_key=os.getenv("MISTRAL_API_KEY"))
        
        print(f"DEBUG: Full Mistral response: {full_response[:200]}...")
        
        # Extract content between <output> tags
        output_match = re.search(r'<output>\s*(.*?)\s*</output>', full_response, re.DOTALL)
        if output_match:
            extracted = output_match.group(1).strip()
            print(f"DEBUG: Extracted from output tags: {extracted[:100]}...")
            return extracted
        else:
            # Fallback: if no output tags found, return the full response
            print("Warning: No <output> tags found in response, using full text")
            
            # Try to clean up common response patterns
            if "Sure" in full_response and "provide" in full_response:
                print("ERROR: Mistral is asking for input instead of generating script")
                # Return a default script for testing
                return "Scientists discovered something incredible! They found that spending time in nature reduces stress hormones. When they tested people in cities versus forests, the nature group had way lower cortisol. So next time you're stressed, get outside! Follow for more science in 30 seconds!"
            
            return full_response

    
    def segment_script(self, script):
        """Segment script for image generation"""
        # Clean the script of any remaining formatting
        clean_script = script.strip()
        
        # Split into sentences (roughly) for image generation
        # Split on periods followed by space, exclamation marks, or question marks
        sentences = re.split(r'[.!?]+\s+', clean_script)
        
        # Filter out empty strings and very short segments
        segments = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        
        # If we have too many segments, combine some
        if len(segments) > 3:
            # Combine into 3 segments for beginning, middle, end
            third = len(segments) // 3
            segments = [
                ' '.join(segments[:third]),
                ' '.join(segments[third:2*third]),
                ' '.join(segments[2*third:])
            ]
        elif len(segments) < 3:
            # If we have too few segments, use the whole script
            segments = [clean_script]
        
        return segments