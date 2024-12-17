import re

from bs4 import BeautifulSoup
import markdown


URL_PATTERN = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
HOMOGLYPH_MAP = {
    # Cyrillic letters
    'А': 'A',  # U+0410 Cyrillic Capital Letter A
    'В': 'B',  # U+0412 Cyrillic Capital Letter Ve
    'Е': 'E',  # U+0415 Cyrillic Capital Letter Ie
    'К': 'K',  # U+041A Cyrillic Capital Letter Ka
    'М': 'M',  # U+041C Cyrillic Capital Letter Em
    'Н': 'H',  # U+041D Cyrillic Capital Letter En
    'О': 'O',  # U+041E Cyrillic Capital Letter O
    'Р': 'P',  # U+0420 Cyrillic Capital Letter Er
    'С': 'C',  # U+0421 Cyrillic Capital Letter Es
    'Т': 'T',  # U+0422 Cyrillic Capital Letter Te
    'Х': 'X',  # U+0425 Cyrillic Capital Letter Ha
    'а': 'a',  # U+0430 Cyrillic Small Letter A
    'е': 'e',  # U+0435 Cyrillic Small Letter Ie
    'о': 'o',  # U+043E Cyrillic Small Letter O
    'р': 'p',  # U+0440 Cyrillic Small Letter Er
    'с': 'c',  # U+0441 Cyrillic Small Letter Es
    'у': 'y',  # U+0443 Cyrillic Small Letter U
    'х': 'x',  # U+0445 Cyrillic Small Letter Ha
    'І': 'I',  # U+0406 Cyrillic Capital Letter Byelorussian-Ukrainian I
    'і': 'i',  # U+0456 Cyrillic Small Letter Byelorussian-Ukrainian I
    # Greek letters
    'Α': 'A',  # U+0391 Greek Capital Letter Alpha
    'Β': 'B',  # U+0392 Greek Capital Letter Beta
    'Ε': 'E',  # U+0395 Greek Capital Letter Epsilon
    'Ζ': 'Z',  # U+0396 Greek Capital Letter Zeta
    'Η': 'H',  # U+0397 Greek Capital Letter Eta
    'Ι': 'I',  # U+0399 Greek Capital Letter Iota
    'Κ': 'K',  # U+039A Greek Capital Letter Kappa
    'Μ': 'M',  # U+039C Greek Capital Letter Mu
    'Ν': 'N',  # U+039D Greek Capital Letter Nu
    'Ο': 'O',  # U+039F Greek Capital Letter Omicron
    'Ρ': 'P',  # U+03A1 Greek Capital Letter Rho
    'Τ': 'T',  # U+03A4 Greek Capital Letter Tau
    'Υ': 'Y',  # U+03A5 Greek Capital Letter Upsilon
    'Χ': 'X',  # U+03A7 Greek Capital Letter Chi
    'Ϲ': 'C',  # U+03F9 Greek Capital Lunate Sigma
    'а': 'a',  # U+03B1 Greek Small Letter Alpha
    'ο': 'o',  # U+03BF Greek Small Letter Omicron
    'с': 'c',  # U+03F2 Greek Lunate Sigma Symbol
}


def preprocessing_text(text: str) -> str:

        # Replace zero-width spaces with normal spaces
        text = text.replace('\u200B', '')

        # Replace homoglyphs with ASCII equivalents
        text = ''.join(HOMOGLYPH_MAP.get(char, char) for char in text)

        # Remove markdown
        html = markdown.markdown(text)

        # Use BeautifulSoup to extract text from HTML
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
    
        # Remove URLs and EMAILs
        text = URL_PATTERN.sub('', text)
        text = EMAIL_PATTERN.sub('', text) 

        text = " ".join(text.split())

        return text.strip()


if __name__ == "__main__":
    sample = """
Hello,   world!
It's а test of preproccesing funсtion
Google search url: https://www.google.com/
"""

    print(preprocessing_text(sample))
