import torch
import torch.nn.functional as F
from nltk.tokenize import sent_tokenize
from transformers import RobertaTokenizer

from generated_text_detector.controllers.schemas_type import Author
from generated_text_detector.utils.preprocessing import preprocessing_text
from generated_text_detector.utils.model.roberta_classifier import RobertaClassifier


class GeneratedTextDetector:
    """Detector for identifying generated text.

    :param model_name_or_path: Either the `model_id` (string) of a model hosted on the Hub, or a path to a `directory` containing model weights
    :type model_name_or_path: str
    :param device: The device identifier string (e.g. `cpu` or `cuda`) on which the model will be loaded.
    :type device: str
    :param max_len: Maximum length of input text sequences in model input, defaults to 512
    :type max_len: int, optional
    """
    def __init__(
        self,
        model_name_or_path: str,
        device: str,
        max_len: int = 512,
        preprocessing: bool = False
    ) -> None:
        
        self.device = torch.device(device)
        self.tokenizer = RobertaTokenizer.from_pretrained(model_name_or_path, do_lower_case=True)
        self.model = RobertaClassifier.from_pretrained(model_name_or_path)
        self.model.to(self.device)
        self.model.eval()

        self.__max_len = max_len
        self.preprocessing = preprocessing

        # Optimizing GPU inference
        if self.device.type == 'cuda':
            self.model = self.model.half()
            self.model = torch.compile(self.model)

            # Running synthetic data for correct compilation
            sample = "Hello, world! " * 120
            for _ in range(5):
                self.detect(sample)


    def __split_by_chunks(self, text: str) -> list[str]:
        """Split text into chunks to handle large inputs.

        :param text: Input text
        :type text: str
        :return: List of text chunks
        :rtype: list[str]
        """
        if len(self.tokenizer.encode(text)) < self.__max_len:
            return [text]

        chunks = []
        cur_chunk = ""
        cur_count_tokens = 0

        for sentence in sent_tokenize(text):
            temp_count_tokens = len(self.tokenizer.encode(sentence))
            if cur_count_tokens + temp_count_tokens > self.__max_len:
                chunks.append(cur_chunk.strip())
                cur_chunk = sentence
                cur_count_tokens = temp_count_tokens
            else:
                cur_count_tokens += temp_count_tokens
                cur_chunk += " " + sentence
        
        chunks.append(cur_chunk.strip())

        return chunks


    def __model_pass(self, texts: list[str]) -> list[float]:
        """Forward pass through the model to obtain scores.

        :param texts: List of text inputs
        :type texts: list[str]
        :return: List of scores
        :rtype: list[float]
        """
        tokens = self.tokenizer.batch_encode_plus(
            texts,
            add_special_tokens=True,
            max_length=self.__max_len,
            padding='longest',
            truncation=True,
            return_token_type_ids=True,
            return_tensors="pt"
        )

        tokens.to(self.device)

        with torch.inference_mode():
            _, logits = self.model(**tokens)

        probas = F.sigmoid(logits).squeeze(1)
        
        return probas


    def detect(self, text: str) -> list[tuple[str, float]]:
        """Detects if text is generated and return chunks with scores.

        :param text: Input text
        :type text: str
        :return: Text chunks with generated scores
        :rtype: list[tuple[str, float]]
        """
        # Preprocessing
        if self.preprocessing:
            text = preprocessing_text(text)
        else:
            text = " ".join(text.split())

        text_chunks = self.__split_by_chunks(text)

        scores = self.__model_pass(text_chunks).tolist()

        res = list(zip(text_chunks, scores))
       
        return res
    

    def detect_report(self, text: str) -> dict:
        """Detects if text is generated and prepare a report.

        :param text: Input text
        :type text: str
        :return: Text chunks with generated scores
        :rtype: list[tuple[str, float]]
        """
        # Preprocessing
        if self.preprocessing:
            text = preprocessing_text(text)
        else:
            text = " ".join(text.split())

        text_chunks = self.__split_by_chunks(text)
        scores = self.__model_pass(text_chunks)

        # Average scores
        gen_score = sum(scores) / len(scores)
        gen_score = gen_score.item() 
        author = self.__determine_author(gen_score).value

        res = {
            "generated_score": gen_score,
            "author": author
        }
       
        return res


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
    detector = GeneratedTextDetector(
        "SuperAnnotate/ai-detector",
        "cuda:0",
        preprocessing=True
    )

    res = detector.detect_report("Hello, world!")

    print(res)
