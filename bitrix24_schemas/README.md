# Схемы полей Bitrix24

Этот каталог содержит полные схемы полей, полученные из Bitrix24 REST API.

## Файлы

### 1. `contact_fields.json`
Структура полей контактов, полученная через `crm.contact.fields`

**Основные поля:**
- `NAME` - Имя (обязательное)
- `LAST_NAME` - Фамилия (обязательное)
- `SECOND_NAME` - Отчество (обязательное)
- `EMAIL` - Email (множественное поле)
- `PHONE` - Телефон (множественное поле)
- `UTM_*` - UTM метки для аналитики

**Пример использования:**
```bash
curl -X POST "https://crmhse.ru/rest/169/3w9qyda4ckgm94zi/crm.contact.fields"
```

### 2. `deal_fields.json`
Структура полей сделок, полученная через `crm.deal.fields`

**Основные поля:**
- `TITLE` - Название сделки
- `CONTACT_IDS` - ID контактов (множественное)
- `STAGE_ID` - Стадия сделки
- `UTM_*` - UTM метки
- `UF_CRM_1755626160` - Образовательная программа (кастомное поле, ссылка на список 18)
- `UF_CRM_1755626174` - ID Roistat (кастомное поле)

**Пример использования:**
```bash
curl -X POST "https://crmhse.ru/rest/169/3w9qyda4ckgm94zi/crm.deal.fields"
```

### 3. `poll_list_fields.json`
Структура универсального списка "Опросные формы" (IBLOCK_ID=17)

**Поля:**
- `NAME` - Название опросной формы
- `PROPERTY_64` (CODE: POLL_ID) - ID опросной формы
- `PROPERTY_66` (CODE: REPONSIBLE_EMPLOYEE_ID) - Ответственный сотрудник
- `PROPERTY_65` (CODE: POLL_URL) - URL опросной формы
- `PROPERTY_74` (CODE: EDUCATIONAL_PROGRAM_ID) - Образовательная программа (ссылка на список 18)

**Пример использования:**
```bash
curl -X POST "https://crmhse.ru/rest/169/3w9qyda4ckgm94zi/lists.field.get.json" \
  -H "Content-Type: application/json" \
  -d '{
    "IBLOCK_TYPE_ID": "lists",
    "IBLOCK_ID": "17"
  }'
```

### 4. `educational_programs_fields.json`
Структура универсального списка "Образовательные программы" (IBLOCK_ID=18)

**Поля:**
- `NAME` - Название программы
- `PROPERTY_73` (CODE: EDUCATIONAL_PROGRAM_ID) - Внешний ID образовательной программы
- `PROPERTY_67` (CODE: PROGRAM_URL) - Ссылка на программу
- `PROPERTY_68` (CODE: LANGUAGE_ID) - Язык (ссылка на список 19)
- `PROPERTY_69` (CODE: CAMPUS_ID) - Кампус (ссылка на список 20)
- `PROPERTY_70` (CODE: OWNER_ID) - Ответственный сотрудник
- `PROPERTY_71` (CODE: EDUCATION_FORM_ID) - Формат обучения (ссылка на список 21)
- `PROPERTY_72` (CODE: STATUS) - Статус (56=Активная, 57=Неактивная)

**Пример использования:**
```bash
curl -X POST "https://crmhse.ru/rest/169/3w9qyda4ckgm94zi/lists.field.get.json" \
  -H "Content-Type: application/json" \
  -d '{
    "IBLOCK_TYPE_ID": "lists",
    "IBLOCK_ID": "18"
  }'
```

## Маппинг полей

Основной файл с маппингом находится в корне проекта: `../field_mapping.json`

Он содержит:
- Полное описание всех сущностей
- Маппинг полей из форм опросов в Bitrix24
- Бизнес-логику обработки ответов
- Схемы API эндпоинтов `/postPoll` и `/postAnswer`

## Важные замечания

### Множественные поля (multifield)
Поля `EMAIL` и `PHONE` в контактах имеют специальный формат:
```json
{
  "EMAIL": [
    {
      "VALUE": "test@example.com",
      "VALUE_TYPE": "WORK"
    }
  ]
}
```

### Кастомные поля сделок
Кастомные поля начинаются с `UF_CRM_`:
- `UF_CRM_1755626160` - Образовательная программа (тип: iblock_element, IBLOCK_ID=18)
- `UF_CRM_1755626174` - ID Roistat (тип: string)

### Связь между списками
- Опросные формы (17) → Образовательные программы (18) через поле `PROPERTY_74`
- Сделки → Образовательные программы (18) через поле `UF_CRM_1755626160`

## Обновление схем

Для обновления схем выполните:
```bash
# Контакты
curl -s -X POST "https://crmhse.ru/rest/169/3w9qyda4ckgm94zi/crm.contact.fields" | python3 -m json.tool > contact_fields.json

# Сделки
curl -s -X POST "https://crmhse.ru/rest/169/3w9qyda4ckgm94zi/crm.deal.fields" | python3 -m json.tool > deal_fields.json

# Опросные формы
curl -s -X POST "https://crmhse.ru/rest/169/3w9qyda4ckgm94zi/lists.field.get.json" \
  -H "Content-Type: application/json" \
  -d '{"IBLOCK_TYPE_ID": "lists", "IBLOCK_ID": "17"}' | python3 -m json.tool > poll_list_fields.json

# Образовательные программы
curl -s -X POST "https://crmhse.ru/rest/169/3w9qyda4ckgm94zi/lists.field.get.json" \
  -H "Content-Type: application/json" \
  -d '{"IBLOCK_TYPE_ID": "lists", "IBLOCK_ID": "18"}' | python3 -m json.tool > educational_programs_fields.json
```

## Дата получения схем

Все схемы получены: **2025-10-22**
