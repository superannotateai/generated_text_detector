import re

from generated_text_detector.controllers.schemas_type import Author
from generated_text_detector.utils.text_detector import GeneratedTextDetector


class AggregatedDetector:
    """Detector for identifying generated content aggregateing text detector and code detector

    :param text_detector_model_name_or_path: Either the `model_id` (string) of a model hosted on the Hub, or a path to a `directory` containing model weights for GeneratedTextDetector
    :type text_detector_model_name_or_path: str
    :param device: The device identifier string (e.g. `cpu` or `cuda`) on which the model will be loaded.
    :type device: str
    """
    def __init__(
        self,
        text_detector_model_name_or_path: str,
        device: str,
        code_default_score: float = 0.5
    ) -> None:
        
        self.code_default_score = code_default_score

        self.text_detector = GeneratedTextDetector(text_detector_model_name_or_path, device=device)

        self.code_block_pattern = re.compile(r"```(\w+)?\s*([\s\S]*?)\s*```")


    def __split_text_and_code(self, text: str) -> tuple[str, str]:
        """Split input text to text and code blocks.
        
        :param text: Input text
        :type text: str
        :return: Combined pieces of text and code
        :rtype: tuple(str, str)
        """
        code_blocks = self.code_block_pattern.findall(text)
        code_blocks = [code for lang, code in code_blocks]
        code = "\n\n".join(code_blocks)

        texts = self.code_block_pattern.split(text)
        text = "\n".join([t.strip() for t in texts if t and t.strip()])

        return text, code

        
    def detect_report(self, text: str) -> dict:
        """Detects if text is generated and prepare a report.

        :param text: Input text
        :type text: str
        :return: Text chunks with generated scores
        :rtype: dict with keys: 'generated_score' and 'author'
        """
        text, code = self.__split_text_and_code(text)

        results = []

        if text.strip():
            text_chunks = self.text_detector.detect(text)
            results += text_chunks
        if code.strip():
            results += [(code, self.code_default_score)]

        score = self.__aggregate_scores(results)
        author = self.__determine_author(score)

        res = {
            "generated_score": score,
            "author": author
        }

        return res


    @staticmethod
    def __aggregate_scores(chunk_scores: list[tuple[str, float]]) -> float:
        """Calculate the weighted mean of scores based on the lengths of text chunks.

        :param chunk_scores: List of tupels where each tuple contains a text chunk and a score (from 0 to 1).
        :type text: list[tuple[str, float]]
        :return: The weighted mean of the scores.
        :rtype: float
        """
        weighted_scores_sum = 0.0
        total_weights = 0
        
        for chunk, score in chunk_scores:
            weight = len(chunk)
            
            weighted_scores_sum += score * weight
            total_weights += weight
        
        weighted_mean = weighted_scores_sum / total_weights
    
        return weighted_mean

    
    @staticmethod
    def __determine_author(generated_score: float) -> Author:
        """Function for converting score for final prediction
        The generated score is compared with heuristics obtained from analysis on validation data
        As a result, we get 5 categories described in the `Author` class
        
        :param text: Generated score from detector model
        :type text: float, should be from 0 to 1
        :return: Final prediction athor
        :rtype: Autrhor
        """
        assert 0 <= generated_score <= 1

        if generated_score > 0.9:
            return Author.LLM_GENERATED
        elif generated_score > 0.7:
            return Author.PROBABLY_LLM_GENERATED
        elif generated_score > 0.3:
            return Author.NOT_SURE
        elif generated_score > 0.1:
            return Author.PROBABLY_HUMAN_WRITTEN
        else:
            return Author.HUMAN
    

if __name__ == "__main__":
    import json

    with open("etc/configs/detector_config.json") as f:
        detector_config = json.load(f)

    detector = AggregatedDetector(
        text_detector_model_name_or_path = detector_config["text_detector_model"],
        code_default_score = detector_config["code_default_probability"],
        device = "cuda:0",
    )

    res = detector.detect_report("Hello, world!")

    print(res)
