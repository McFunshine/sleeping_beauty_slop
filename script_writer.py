"""Script writer module - Generate engaging scripts with Mistral LLM"""


class ScriptWriter:
    """Generate TikTok-style scripts from research"""
    
    def __init__(self):
        self.prompt_template = """
You're an AI scriptwriter for TikTok videos. 
You take boring research and turn it into short, dramatic, or funny monologues that sound like something a curious and slightly unhinged narrator would say. 

Here's the research abstract:
{abstract}

Now turn that into a 30–60 second video script with:
- A dramatic or funny hook (first line)
- A surprising twist
- A weird fact
- A closing line with flair
"""
    
    def generate_script(self, abstract, key_points):
        """Generate engaging script from paper content"""
        # TODO: Call Mistral LLM with prompt
        pass
    
    def segment_script(self, script):
        """Segment script for image generation"""
        # TODO: Split script into 3-4 logical segments
        pass