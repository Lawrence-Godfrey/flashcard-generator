import json
import logging
import os
import fire
from dotenv import load_dotenv

from openai import OpenAI


class FlashcardGenerator:
    """
    A class to generate flashcards from text using an LLM.
    """

    def __init__(
        self,
        api_key: str = None,
        model: str = "gpt-4-turbo",
        input_dir: str = None,
        output_dir: str = None,
        verbose: bool = False,
    ):
        """
        Initialize the FlashcardGenerator class.
        """
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

        # Make sure model is a string
        if not isinstance(model, str):
            raise TypeError("model must be a string.")

        self.model = model

        if not input_dir:
            self.input_dir = os.getcwd()
        else:
            self.input_dir = input_dir

        if not output_dir:
            self.output_dir = os.path.join(self.input_dir, "flashcards")
        else:
            self.output_dir = os.path.join(output_dir, "flashcards")

        # Set up logging
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        else:
            logging.getLogger().setLevel(logging.INFO)

    def create_flashcard(self, content: str) -> dict:
        """
        Create a flashcard from the content using GPT.

        Parameters
        ----------
        content:
            The content to create a flashcard from.

        Returns
        -------
        dict:
            The dict containing a list of flashcards in the format:
            {
                "cards": [
                    {
                        "front": "Front of the flashcard",
                        "back": "Back of the flashcard"
                    }
                ]
            }
        """

        system_message = """
        You are a flashcard generation bot. Given a piece of text, you will generate a flashcard as a JSON
        object with the following format:
        {
            "cards": [
                {
                    "front": "Front of the flashcard",
                    "back": "Back of the flashcard"
                }
            ]
        }
        
        For example, given the text:
        The capital of France is Paris.
        
        You would generate the flashcard:
        {
            "cards": [
                {
                    "front": "What is the capital of France?",
                    "back": "Paris"
                }
            ]
        }

        If multiple flashcards can be generated from the text, you should generate all of them.
        For example, given the text:
        The capital of France is Paris. The capital of Spain is Madrid.
        
        You would generate the flashcards:
        {
            "cards": [
                {
                    "front": "What is the capital of France?",
                    "back": "Paris"
                },
                {
                    "front": "What is the capital of Spain?",
                    "back": "Madrid"
                }
            ]
        }
        
        NB: Return a valid JSON object.
        """

        user_message = f"""
        Create a flashcard from the following content:
        {content}
        NB: Return a valid JSON object.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            response_format={"type": "json_object"},
        )

        flashcards = json.loads(response.choices[0].message.content)["cards"]

        logging.debug(f"Generated flashcards: {flashcards}")
        logging.info(
            f"Generated {len(flashcards)} flashcards. Used {response.usage.total_tokens} tokens."
        )

        return flashcards

    def process_file(
        self, input_file_path: str, output_file_path: str, print_output: bool = False
    ):
        """
        Process a single .md file and create flashcards in the output directory.

        Parameters
        ----------
        input_file_path:
            The path to the input .md file.
        output_file_path:
            The path to the output file.
        print_output:
            Whether to print the output to the console.
        """
        # Read the content of the .md file
        with open(input_file_path, "r", encoding="utf-8") as infile:
            logging.debug(f"Reading content from {input_file_path}.")
            content = infile.read()

        # Create a flashcard using GPT
        flashcards = self.create_flashcard(content)

        output_content = self.format_flashcards(flashcards)

        if print_output:
            print(output_content)
        else:
            # Write the flashcard to the output file
            with open(output_file_path, "w", encoding="utf-8") as outfile:
                logging.info(f"Writing flashcards to {output_file_path}.")
                logging.debug(f"Writing {output_content} to {output_file_path}.")

                outfile.write(output_content)

    def process_files(self, overwrite_files: bool = False):
        """
        Recursively process .md files in input_dir and create flashcards in output_dir,
        maintaining the directory structure.

        Parameters
        ----------
        overwrite_files:
            Whether to overwrite files in the output directory.
        """
        for root, _, files in os.walk(self.input_dir):
            if root.startswith(self.output_dir):
                logging.debug(f"Skipping {root}. Output directory.")
                continue

            for file in files:
                if file.endswith(".md"):
                    input_file_path = os.path.join(root, file)
                    output_file_path = os.path.join(
                        self.output_dir, os.path.relpath(input_file_path, self.input_dir)
                    )

                    # Create the output directory if it doesn't exist
                    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

                    if os.path.exists(output_file_path) and not overwrite_files:
                        logging.info(f"Skipping {output_file_path}. File already exists.")
                    else:
                        self.process_file(input_file_path, output_file_path)

    def format_flashcards(
        self,
        flashcards: dict,
        format_type: str = "obsidian_spaced_repetition",
        include_tag: bool = True,
    ) -> str:
        """
        Format the flashcards into a string.

        Parameters
        ----------
        flashcards:
            The flashcards to format.
        format_type:
            The format to use. Options are "obsidian_spaced_repetition".
        include_tag:
            Whether to include the `#flashcards` tag required by the spaced repetition plugin.

        Returns
        -------
        str:
            The formatted flashcards.
        """
        output = ""

        if format_type == "obsidian_spaced_repetition":
            if include_tag:
                output += "#flashcards\n\n"

            for card in flashcards:
                if "front" in card and "back" in card:
                    front = card["front"]
                    back = card["back"]
                    output += f"{front}\n?\n{back}\n\n"
                else:
                    logging.debug(f"Skipping invalid flashcard: {card}")

        else:
            raise ValueError(f"Invalid format type: {format_type}")

        return output

    def validate_flashcards(self, flashcards: dict):
        """
        Validate the flashcards dict.

        Parameters
        ----------
        flashcards:
            The flashcards to validate.

        Raises
        ------
        ValueError:
            If the flashcards are not in the correct format.
        """

        if not isinstance(flashcards, list):
            raise ValueError("Flashcards must be a list.")

        for card in flashcards:
            if not isinstance(card, dict):
                raise ValueError("Each flashcard must be a dict.")
            if "front" not in card or "back" not in card:
                raise ValueError("Each flashcard must have a 'front' and 'back' key.")
            if not isinstance(card["front"], str) or not isinstance(card["back"], str):
                raise ValueError("The 'front' and 'back' keys must be strings.")


def main():
    # Load environment variables from .env file
    load_dotenv()

    fire.Fire(FlashcardGenerator)


if __name__ == "__main__":
    main()
