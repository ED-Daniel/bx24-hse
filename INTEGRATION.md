# Как устроена интеграция?

## Answer
Приходит примерно такой пакет:

```json
{
  "header_data": {
    "poll_id": 430131691,
    "answer_id": 814573981,
    "create_time": "2023-02-15T10:16:22.652Z",
    "analytics": {
      "url": "https://ba.hse.ru/polls/430131691.html",
      "params": {
        "utm_source": "direct",
        "utm_medium": "direct",
        "utm_campaign": "direct",
        "utm_term": "direct",
        "utm_content": "direct"
      },
      "cookies": {
        "_ym_uid": "1607603521955414288",
        "tracking": "ZEsUBF/Yq9OBi6j1G3IiAg",
        "_ga": "GA1.2.564819297.1608023318",
        "rete_uid": "a33d94e4-1da7-458d-89db-3cfadc6d687c",
        "roistat_visit": "8467460"
      },
      "ip": "185.117.121.169",
      "date": "2023-02-15 13:16",
      "timeZone": "Europe/Moscow"
    },
    "form_kind": 2
  },
  "data": {
    "lastname": "Services TEST",
    "firstname": "CRM TEST",
    "email": "crmservices_server_test@test.test",
    "telephone": "+79104061652",
    "additionalfield1": "Учащийся 9-10 классов",
    "additionalfield3": "Москва",
    "hse_school": "52",
    "educational_program_1": [
      "Цифровой юрист",
      "Античность"
    ],
    "middlename": "52"
  }
}
```

### Шаги
- Ищем опросную форму (список в Битриксе) по `poll_id`
  - Если не нашли - 404
  - Если нашли забираем ее ID
- Ищем контакт по email
  - Если не нашли, то создаем и забираем ID
  - Если нашли, то запоминаем ID
- Ищем образовательную программу (ОП)
  - Если не нашли образовательную программу - 404
  - Если нашли, то забираем ID
- Ищем сделку по CONTACT_ID и EDUCATIONAL_PROGRAM_ID
  - Если не нашли, то создаем
  - Если нашли, то обогащаем

### По наполнению
#### Контакт
В контакт записываем:
- ФИО
- Почту
- Телефон
- Привязываем опросную форму

#### Сделка
В сделку записываем:
- Контакт
- Образовательную программу
- cookies из пакета
- Все additional fields
- Все поля question

### Маппинг полей
...