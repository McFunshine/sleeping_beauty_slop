"""Image generator module - Create visuals with Flux via FAL.AI"""
import os
import requests
import fal_client
import utils as ut


class ImageGenerator:
    """Generate cartoon-style images using Flux model"""

    def __init__(self):
        # Initialize any necessary variables or clients here
        pass

    @staticmethod
    def improve_prompt(text_segment):

        prompt = ut.read_prompt_file("assets/prompts/image_generation_prompt_improve.txt")
        prompt += f"\n{text_segment}"
        print(prompt)
        return ut.call_mistral_api(prompt, api_key=os.getenv("MISTRAL_API_KEY"))
    
    def generate_images(self, script_segments):
        """Generate images for each script segment"""
        images = []
        for segment in script_segments:

            improved_prompt = self.improve_prompt(segment)

            handler = fal_client.submit(
                "fal-ai/flux/dev",
                arguments={
                    "prompt": improved_prompt,
                    # "image_size": {
                    #     "width": 1690,
                    #     "height": 1690
                    #     },
                    "aspect_ratio": "16:9",
                    "num_images": 1
                    },
            )
            request_id = handler.request_id
            result = fal_client.result("fal-ai/flux/dev", request_id)

            images.append(result)

        self.save_images(images, output_dir="assets/images/")
        
    @staticmethod
    def download_generated_image(api_url, save_path):
   
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an error for bad status codes

        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"Image successfully downloaded and saved to {save_path}")

    def save_images(self, images, output_dir="assets/images/"):
        """Save generated images to the specified directory"""
        os.makedirs(output_dir, exist_ok=True)

        for i, image in enumerate(images):
            image_path = os.path.join(output_dir, f"image_{i}.png")
            download_path = image["images"][0]["url"]
            self.download_generated_image(download_path, image_path)

        print(f"Images saved to {output_dir}")
