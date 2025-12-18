"""
Advanced usage example with custom translation backend.

This example shows how to create and use a custom translation backend
in the pipeline for specialized translation needs.
"""

from video_textbox_pipeline import SubtitleTranslationPipeline
from video_textbox_pipeline.translation import Translator
from video_textbox_pipeline.translation.backends import TranslatorBackend


class CustomTranslatorBackend(TranslatorBackend):
    """Custom translation backend example."""
    
    def __init__(self, api_key=None):
        """Initialize custom backend.
        
        Args:
            api_key: Optional API key for your translation service
        """
        self.api_key = api_key
        # Initialize your custom translation service here
    
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text using your custom service.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Translated text
        """
        # This is a placeholder - implement your actual translation logic
        # For example, you might call an API:
        # response = requests.post(
        #     'https://api.example.com/translate',
        #     json={'text': text, 'from': source_lang, 'to': target_lang},
        #     headers={'Authorization': f'Bearer {self.api_key}'}
        # )
        # return response.json()['translated_text']
        
        # For this example, we'll just add a prefix
        return f"[CustomTranslation] {text}"


def main():
    # Create custom translator backend
    custom_backend = CustomTranslatorBackend(api_key='your-api-key-here')
    
    # Create translator with custom backend
    translator = Translator(backend=custom_backend)
    
    # Initialize pipeline
    pipeline = SubtitleTranslationPipeline(
        target_lang='en',
        source_lang='ru',
        render_mode='inpaint',  # Use inpainting mode
        use_gpu=False
    )
    
    # Replace the default translator with custom one
    pipeline.translator = translator
    
    # Process video
    print("Processing video with custom translation backend...")
    stats = pipeline.process_video(
        input_path='russian_video.mp4',
        output_path='english_video.mp4'
    )
    
    print(f"\nProcessed {stats['segments']} segments")


if __name__ == '__main__':
    main()
