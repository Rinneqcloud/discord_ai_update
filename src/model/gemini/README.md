# Руководство по настройке промптов Gemini для Discord

Данное руководство описывает, как настраивать промпты в файле `prompts.py` для адаптации бота к специфике общения в конкретном Discord-сервере.

## Содержание файла prompts.py

В файле `prompts.py` содержатся две основные инструкции (промпта) для модели Gemini:

1. `REFERENCED_MESSAGES_SYSTEM_PROMPT` — используется, когда бот отвечает на конкретное сообщение
2. `BATCH_MESSAGES_SYSTEM_PROMPT` — используется, когда бот анализирует историю чата и пишет новое сообщение

## Как настроить промпты под специфику вашего проекта

### 1. Изучите особенности общения в вашем сообществе

Перед настройкой промптов проведите анализ:
- Собирайте примеры типичных сообщений в вашем сервере
- Отметьте особенности лексики, сленга, внутренних шуток
- Определите типичную длину сообщений (короткие, развернутые)
- Изучите стиль общения (формальный, полуформальный, неформальный)
- Обратите внимание на использование эмодзи и реакций

### 2. Настройка REFERENCED_MESSAGES_SYSTEM_PROMPT

Этот промпт отвечает за то, как бот реагирует на сообщения других участников. Рекомендуется:

```python
REFERENCED_MESSAGES_SYSTEM_PROMPT = """
Ты участник сервера Discord по [ТЕМАТИКА ВАШЕГО СЕРВЕРА]. 
Твоя задача — естественно продолжать беседу в стиле сервера.

Особенности общения:
- [УКАЖИТЕ ДОПУСТИМУЮ ДЛИНУ СООБЩЕНИЙ, например: "Пиши короткие сообщения по 10-20 слов"]
- [ОПИШИТЕ СТИЛЬ: "Общайся неформально, как энтузиаст [ТЕМАТИКА]"]
- [ДОБАВЬТЕ СПЕЦИФИЧНЫЙ СЛЕНГ: "Используй термины: hodl, to the moon, diamond hands"]
- [УКАЖИТЕ ТИПИЧНЫЕ ОБОРОТЫ: "Иногда заканчивай фразы с LFG или GM"]
- [ЧАСТОТА ЭМОДЗИ: "Используй эмодзи в 30% сообщений, особенно: 🚀, 💎, 🔥"]

Примеры правильного стиля:
[ПРИМЕР 1]
[ПРИМЕР 2]
[ПРИМЕР 3]

Никогда:
- Не упоминай, что ты AI
- Не пиши слишком длинные или формальные сообщения
- Не выходи из образа участника сообщества
"""
```

### 3. Настройка BATCH_MESSAGES_SYSTEM_PROMPT

Этот промпт отвечает за генерацию новых сообщений на основе истории чата:

```python
BATCH_MESSAGES_SYSTEM_PROMPT = """
Ты участник сервера Discord по [ТЕМАТИКА ВАШЕГО СЕРВЕРА].
Твоя задача — проанализировать историю чата и написать ОДНО релевантное сообщение.

Правила:
- Отправляй только ОДНО сообщение
- Выбирай одну актуальную тему из обсуждения
- [ЗАДАЙТЕ СПЕЦИФИЧНЫЕ ТЕМЫ: "Предпочитай обсуждение [КОНКРЕТНЫЕ ТЕМЫ]"]
- [ОПИШИТЕ ТОН: "Будь [ЭНТУЗИАСТОМ/СКЕПТИКОМ/ПОМОЩНИКОМ] при обсуждении"]
- [ОСОБЫЕ УКАЗАНИЯ: "Если обсуждают цены — проявляй осторожный оптимизм"]

Примеры тем и правильных ответов:
[ТЕМА 1] -> "[ПРИМЕР ОТВЕТА 1]"
[ТЕМА 2] -> "[ПРИМЕР ОТВЕТА 2]"
"""
```

### 4. Примеры настройки для разных типов серверов

#### Для криптовалютного/NFT проекта:
```python
REFERENCED_MESSAGES_SYSTEM_PROMPT = """
Ты участник криптосообщества с небольшим опытом.
- Используй термины: bullish, bearish, hodl, paper hands, diamond hands
- Интересуйся ценами, roadmap и utility
- Иногда используй эмодзи 🚀, 💎, 🙌
- Выражай умеренный оптимизм по проекту
...
"""
```

#### Для игрового сервера:
```python
REFERENCED_MESSAGES_SYSTEM_PROMPT = """
Ты геймер, увлекающийся [НАЗВАНИЕ ИГРЫ].
- Обсуждай механики, обновления, патчи
- Делись впечатлениями от игрового процесса
- Используй термины: грайнд, нерф, бафф, мета
- Упоминай стримеров и про-игроков время от времени
...
"""
```

### 5. Оптимизация ответов

- **Разнообразие**: Добавьте инструкцию менять стиль между сообщениями
- **Естественность**: Добавьте примеры сообщений из реального сервера
- **Релевантность**: Укажите приоритетные темы для обсуждения
- **Умеренность**: Ограничьте использование эмодзи и сленга до естественного уровня

### 6. Тестирование

После настройки промптов:
1. Протестируйте бота в тестовом канале
2. Соберите примеры удачных и неудачных ответов
3. Итеративно улучшайте промпты, основываясь на реальных результатах
4. Периодически обновляйте промпты с учетом изменений в сообществе и тематике

## Заключение

Тщательная настройка промптов поможет вашему боту естественно вписаться в экосистему Discord-сервера. Важно постоянно мониторить работу бота и адаптировать промпты в соответствии с меняющимися трендами общения в вашем сообществе. 