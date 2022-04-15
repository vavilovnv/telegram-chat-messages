import re
import json
import random
from collections import defaultdict
from typing import Dict, List, DefaultDict, Generator


def tokenize(text: str) -> List[str]:
    """Токенизация текста, пустые строки отбрасываются"""
    punctuation = "\\" + "\\".join(list("[](){}!?.,:;'\"\\/*&^%$_+-–—=<>@|~"))
    words = "[a-zA-Zа-яА-ЯёЁ]+"
    compounds = f"{words}-{words}"
    scr = "\\.{3}"

    tokenize_re = re.compile(f"({scr}|{compounds}|{words}|[{punctuation}])")
    newlines_re = re.compile(r"\n\s*")
    paragraphed = newlines_re.sub(NEWLINE_SYMBOL, text)

    return [token for token in tokenize_re.split(paragraphed) if token]


def slice_corpus(corpus: list, smpl_size: int) -> List[str]:
    """Нарезание текста на списки заданного размера smpl_size с учетом пробелов"""
    samples = (corpus[i: i + smpl_size] for i, _ in enumerate(corpus))
    return [s for s in samples if len(s) == smpl_size]


def collect_transitions(samples: list) -> DefaultDict[str, str]:
    """Выделим ключи и переходы по сэмплам и соберём для каждого ключа список всех встретившихся переходов:"""
    transitions = defaultdict(list)
    # Разбиваем семпл на токены для ключа и токен-переход.
    for sample in samples:
        # Из первых (n - 1) токенов составляем ключ,
        # по которому будем искать список потенциальных переходов:
        state = "".join(sample[0:-1])
        # Последний токен — переход:
        nxt = sample[-1]
        # Дальше ищем список, если не нашли - создаем,
        # добавляем в него новый токен-переход:
        transitions[state].append(nxt)
    return transitions


def predict_next_word(chain: List[str], transitions: DefaultDict[str, str], smpl_size: int) -> str:
    """"Поиск нового токена путем поиска по последнему токену в матрице возможных переходов"""
    last_state = "".join(chain[-(smpl_size - 1):])
    next_words = transitions[last_state]
    return random.choice(next_words) if next_words else ""


def create_chain(start_text: str, transitions: defaultdict) -> List[str]:
    """"Инициация цепи токенов"""
    head = start_text or random.choice(list(transitions.keys()))
    return tokenize(head)


def generate_chain(start_text: str, transitions: DefaultDict[str, str], smpl_size: int) -> Generator:
    """Генерация цепи токенов"""
    chain = create_chain(start_text, transitions)
    while True:
        state = predict_next_word(chain, transitions, smpl_size)
        yield state

        if state:
            chain.append(state)
        else:
            chain = chain[:-1]


def tokens_to_text(tokens: List[str]) -> str:
    """Склеивание результата генерации в текст"""
    paragraph_char = '\n\n'
    return "".join(tokens).replace(NEWLINE_SYMBOL, paragraph_char)


def get_data_from_json_file() -> Dict[str, str]:
    """"Парсим json-файл FILENAME с выгрузкой из канала telegram"""
    with open(FILENAME, encoding='utf-8') as f:
        templates = json.load(f)

    messages = {section['from']: '' for section in templates['messages'] if section.get('from')}
    for section in templates['messages']:
        if (section.get('from') is not None
                and isinstance(section['text'], str)):
            messages[section['from']] += section['text'] + ' '

    return messages


def get_sample_size(len_text_message: str) -> int:
    """"Определяем количество сэмплов в зависимости от длины словаря автора"""
    if len_text_message > MAX_COUNT:
        return MAX_SAMPLE
    elif MIN_COUNT <= len_text_message <= MAX_COUNT:
        return int(len_text_message // MIN_COUNT)
    else:
        return MIN_SAMPLE


def generate(source: str, sample_size: int = 2, start: str = '') -> str:
    """Генерация токенов"""
    corpus = tokenize(source)
    samples = slice_corpus(corpus, sample_size)
    transitions = collect_transitions(samples)
    generator = generate_chain(start, transitions, sample_size)
    generated_tokens = [next(generator) for _ in range(WORDS_COUNT)]

    return tokens_to_text(generated_tokens)


def main() -> None:
    messages = get_data_from_json_file()
    for key, text_message in messages.items():
        len_text_message = len(text_message)
        print(f'*** Отвечает {key} (число символов в корпусе: {len_text_message}) ***')
        sample_size = get_sample_size(len_text_message)
        print(generate(text_message, sample_size), '', sep='\n')

        
if __name__ == '__main__':
    # общие настройки
    NEWLINE_SYMBOL = "§"  # знак параграфа в тексте
    FILENAME = 'input.json'  # имя файла с данными
    FROM = 'lvnvl 😐'  # имя пользователя, по сообщениям которого формируется ответ

    # настройки модели
    MAX_COUNT = 90000  # максимальный предел для определения размера sample
    MIN_COUNT = 10000  # минимальный предел для определения размера sample
    MAX_SAMPLE = 8  # максимальный размер sample
    MIN_SAMPLE = 5  # минимальный размер sample
    WORDS_COUNT = 100  # количество слов в формируемом сообщении

    main()
