# Генерация при помощи цепей Маркова сообщений на основе корпуса текста 

Это учебный pet-project в рамках которого разбираюсь с реализацией простого алгоритма "генерации" (в кавычках, т.к. в основе цепи Маркова, а не какая-то нейросеть) текста, созданием отдельных модулей для импортирования, бота для телеги и пр.

## Планы по развитию мини-проекта
- [х] Разработать основной алгоритм генерации сообщение
- [х] Создать первый модуль для импорта
- [ ] Создать web-форму для настройки параметров модели (в процессе)
- [ ] Разобраться с написанием бота 
- [ ] Реализовать бота 
- [ ] Что-нибудь еще...

## Установка и настройка
Пока особо нечего устанавливать. 

Алгоритм генерации можно посмотреть в message_generation.py (модуль в .generate_message/). Параметры модели настроиваются там же.

Установить message_generation как модуль для импорта: `pip install .\dist\generate_message-1.0.tar.gz`