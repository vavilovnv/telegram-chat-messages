import re
import json
import random
from collections import defaultdict


def tokenize(text):
    """Токенизация текста, пустые строки отбрасываются"""
    punctuation = "\\" + "\\".join(list("[](){}!?.,:;'\"\\/*&^%$_+-–—=<>@|~"))
    words = "[a-zA-Zа-яА-ЯёЁ]+"
    compounds = f"{words}-{words}"
    scr = "\\.{3}"

    tokenize_re = re.compile(f"({scr}|{compounds}|{words}|[{punctuation}])")
    newlines_re = re.compile(r"\n\s*")
    paragraphed = newlines_re.sub(NEWLINE_SYMBOL, text)

    return [token for token in tokenize_re.split(paragraphed) if token]


def slice_corpus(corpus, smpl_size):
    """Нарезание текста на списки заданного размера smpl_size с учетом пробелов"""
    samples = (corpus[i: i + smpl_size] for i, _ in enumerate(corpus))
    return [s for s in samples if len(s) == sample_size]


def collect_transitions(samples):
    """Выделим ключи и переходы по сэмплам и соберём для каждого ключа список всех встретившихся переходов:"""
    transitions = defaultdict(list)
    # Разбиваем семпл на токены для ключа и токен-переход.
    for sample in samples:
        # Из первых (n - 1) токенов составляем ключ,
        # по которому будем искать список потенциальных переходов:
        state = "".join(sample[0:-1])
        # Последний токен — переход:
        nxt = sample[-1]
        # Дальше — всё, как в прошлый раз :–)
        # Ищем список, создаём его, если не нашли,
        # добавляем в него новый токен-переход:
        transitions[state].append(nxt)
    return transitions


def predict_next_word(chain, transitions, smpl_size):
    """"Поиск нового токена путем поиска по последнему токену в матрице возможных переходов"""
    last_state = "".join(chain[-(smpl_size - 1):])
    next_words = transitions[last_state]
    return random.choice(next_words) if next_words else ""


def create_chain(start_text, transitions):
    """"Инициация цепи токенов"""
    head = start_text or random.choice(list(transitions.keys()))
    return tokenize(head)


def generate_chain(start_text, transitions, smpl_size):
    """Генерация цепи токенов"""
    chain = create_chain(start_text, transitions)

    while True:
        state = predict_next_word(chain, transitions, smpl_size)
        yield state

        if state:
            chain.append(state)
        else:
            chain = chain[:-1]


def tokens_to_text(tokens):
    """Склеивание результата генерации в текст"""
    paragraph_char= '\n\n'
    return "".join(tokens).replace(NEWLINE_SYMBOL, paragraph_char)


def get_data_from_json_file():
    """"Парсим json-файл FILENAME с выгрузкой из канала telegram"""
    with open(FILENAME, encoding='utf-8') as f:
        templates = json.load(f)

    messages = {section['from']: '' for section in templates['messages'] if section.get('from')}
    for section in templates['messages']:
        if (section.get('from') is not None
                and isinstance(section['text'], str)):
            messages[section['from']] += section['text'] + ' '

    return messages


def get_sample_size(len_text_message):
    """"Определяем количество сэмплов в зависимости от длины словаря автора"""
    if len_text_message > 70000:
        return 8
    elif 10000 <= len_text_message <= 70000:
        return int(len_text_message // 10000)
    else:
        return 2


def generate(source, start='', words_count=100, sample_size=2):
    """Генерация токенов"""
    corpus = tokenize(source)
    samples = slice_corpus(corpus, sample_size)
    transitions = collect_transitions(samples)

    generator = generate_chain(start, transitions, sample_size)
    generated_tokens = [next(generator) for _ in range(words_count)]

    return tokens_to_text(generated_tokens)


def main():
    messages = get_data_from_json_file()
    for key, text_message in messages.items():
        len_text_message = len(text_message)
        print(f'*** Отвечает {key} (число символов в корпусе: {len_text_message}) ***')
        sample_size = get_sample_size(len_text_message)
        print(generate(source=text_message, words_count=WORDS_COUNT, sample_size=sample_size))
        print()
        
        
if __name__ == '__main__':
    # константы
    NEWLINE_SYMBOL = "§"  # знак параграфа в тексте
    FILENAME = 'input.json'  # имя файла с данными
    FROM = 'lvnvl 😐'  # имя пользователя, по сообщениям которого формируется ответ
    WORDS_COUNT = 150  # количество слов в формируемом сообщении

    main()
