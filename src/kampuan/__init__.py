from typing import List, Union
import pythainlp.tokenize as tk
from pythainlp.tokenize import syllable_tokenize 

def test(name: str = "World!"):
    return f'Hello {name}'


def tokenize(phrase: str = "สวัสดี") -> List[str]:
    # return tk.word_tokenize(text=phrase)
    return syllable_tokenize(text=phrase)


def puan_kam(phrase: Union[List[str],str]=['กิน','ข้าว'])->List[str]:

    if isinstance(phrase,str):
        phrase=tokenize(phrase=phrase)
    

    return phrase
