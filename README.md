# Hebrew Child Book Agent UI

AI Agent עם UI להכנת ספר ילדים בעברית.

כולל:
- UI בעברית
- FastAPI backend
- LangGraph workflow
- OpenAI GPT API דרך קובץ `.env`
- קלט לשער + כמה עמודים שרוצים
- הוראות חופשיות בעברית
- יצירת ספר JSON
- תצוגה מקדימה
- הורדת ZIP של ספר סטטי ל-GitHub Pages

## התקנה

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Mac/Linux:

```bash
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
```

## הגדרת API Key

פתחי את `.env` ושימי:

```env
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4.1-mini
```

## הרצה

```bash
uvicorn app.main:app --reload
```

פתחי:

```text
http://127.0.0.1:8000
```

## הערה

לא שמים OpenAI API key ב-JavaScript. הטוקן נשאר רק בצד שרת בקובץ `.env`.
