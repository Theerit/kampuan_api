from typing import List, Union, Dict
import pythainlp.tokenize as tk
from pythainlp.tokenize import syllable_tokenize
from kampuan.lang_tools import extract_vowel_form
from kampuan.sub_word import ThaiSubWord


def test(name: str = "World!"):
    return f'Hello {name}'


def tokenize(text: str = "สวัสดี") -> List[str]:
    # return tk.word_tokenize(text=phrase)
    return syllable_tokenize(text=text)


def extract_vowel(text: str) -> Dict:
    if isinstance(text, str):
        phrases = tokenize(text=text)
    results = {}
    for word in text:
        results[word] = extract_vowel_form(word).vowel_form

    return results


def puan_kam_preprocess(text, skip_tokenize=True):
    # 2. Split phrase to syllables
    if isinstance(text, str):
        tokenized = tokenize(text)
    elif isinstance(text, List):
        if skip_tokenize:
            tokenized = text
        else:
            tokenized = [w for txt in text for w in tokenize(txt)]
    else:
        raise ValueError('incorrect value')
    # 3. Sub word processing, types and tones
    sub_words = [ThaiSubWord(word) for word in tokenized]

    # 4. preprocessing on two syllable words
    split_words = [
        word_split for word in sub_words for word_split in word.split_non_conform()]

    return split_words


def puan_2_kam(a_raw, b_raw, keep_tone=None):
    a_raw_tone = a_raw._tone
    b_raw_tone = b_raw._tone

    # swap vowel
    a_target = b_raw._vowel_form_sound.replace('-', a_raw.init_con)
    b_target = a_raw._vowel_form_sound.replace('-', b_raw.init_con)

    # swap final con
    a_target = ThaiSubWord(a_target + b_raw.final_con)
    b_target = ThaiSubWord(b_target + a_raw.final_con)

    # Swap tone
    # assign tones
    if keep_tone is None:
        if a_target._word_class == 'dead' or b_target._word_class == 'dead':
            keep_tone = False
        else:
            keep_tone = True

    if keep_tone:
        a_target_tone = a_raw_tone
        b_target_tone = b_raw_tone
    else:
        a_target_tone = b_raw_tone
        b_target_tone = a_raw_tone

    # apply tone rules
    a_target = ThaiSubWord.pun_wunayook(a_target._raw, a_target_tone)
    b_target = ThaiSubWord.pun_wunayook(b_target._raw, b_target_tone)

    return a_target, b_target


def puan_kam_base(text='สวัสดี', keep_tone=None, use_first=True, index=None):

    if isinstance(text, str):
        split_words = puan_kam_preprocess(text)
    elif isinstance(text[0], str):
        split_words = puan_kam_preprocess(text)
    else:
        split_words = text
    # 5. Determine two syllable to do the puan
    if not index:
        n_subwords = len(split_words)
        index = (0, 0)
        if n_subwords == 1:
            index = (0, 0)
        elif n_subwords == 2:
            index = (0, 1)
        elif use_first:
            index = (0, -1)
        else:
            index = (1, -1)
    # 6. Puan process, output new
    # puan kum given two subwords
    a_raw = split_words[index[0]]
    b_raw = split_words[index[1]]

    # apply tone rules
    a_target, b_target = puan_2_kam(a_raw, b_raw, keep_tone=keep_tone)

    # 7. combine
    kam_puan = [w._raw for w in split_words]
    kam_puan[index[0]] = a_target
    kam_puan[index[1]] = b_target

    return kam_puan


def puan_kam_all(text='สวัสดี'):
    use_first = [True, False]
    keep_tone = [True, False]
    result = {}
    count = 0
    for j in use_first:
        for k in keep_tone:
            result[count] = puan_kam_base(
                text=text, use_first=j, keep_tone=k)
            count += 1
    return result


def puan_kam_auto(text='สวัสดี', use_first=None):

    if isinstance(text, str):
        split_words = puan_kam_preprocess(text)
    elif isinstance(text[0], str):
        split_words = puan_kam_preprocess(text)
    else:
        split_words = text

    n_subwords = len(split_words)

    index = (0, 0)
    if n_subwords == 1:
        index = (0, 0)
    elif n_subwords == 2:
        index = (0, 1)
    elif n_subwords == 3:
        if split_words[0]._word_class == 'dead':  # not sure
            index = (1, -1)
        else:
            index = (0, -1)
    else:  # more than 3
        if use_first is None:
            return [puan_kam_base(text=split_words, keep_tone=None, index=(i, -1)) for i in [0, 1]]
        elif use_first:
            index = (0, -1)
        else:
            index = (1, -1)

    return puan_kam_base(text=split_words, keep_tone=None, index=index)


def puan_kam(text) -> List[str]:
    return puan_kam_auto(text=text, use_first=None)


def pun_wunayook(text):
    text = puan_kam_preprocess(text)
    result = []
    for i, txt in enumerate(text):
        result.append([ThaiSubWord.pun_wunayook(txt._raw, tone_target=i)
                       for i in range(0, 5)])
    return result
