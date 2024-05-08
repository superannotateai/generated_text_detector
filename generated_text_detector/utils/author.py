from enum import Enum


class Author(str, Enum):
    LLM_GENERATED = "LLM Generated"
    PROBABLY_LLM_GENERATED = "Probably LLM Generated"
    NOT_SURE = "Not sure"
    PROBABLY_HUMAN_WRITTEN = "Probably human written"
    HUMAN = "Human"
