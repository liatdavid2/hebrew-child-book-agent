# Hebrew Book Agent With Images

UI בעברית + FastAPI + LangGraph + OpenAI.

הפרויקט מקבל:
- מלל שער
- כמה עמודים שרוצים
- הוראות בעברית ל-GPT

ואז:
1. יוצר ספר ילדים בעברית
2. יוצר תמונת שער
3. יוצר תמונה לכל עמוד
4. בונה ספר HTML מדפדף
5. יוצר ZIP מוכן ל-GitHub Pages

<img width="1919" height="969" alt="image" src="https://github.com/user-attachments/assets/b603cf59-fb41-4a32-9f8f-44a05d867583" />

<img width="1914" height="865" alt="image" src="https://github.com/user-attachments/assets/6eb90086-34a1-428b-9e0b-1549260e7ad7" />

<img width="1919" height="966" alt="image" src="https://github.com/user-attachments/assets/81b5387f-bd9b-4590-aa6b-7ff0288cd864" />



## התקנה

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scriptsctivate
```

Mac/Linux:

```bash
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
```

## הגדרת API key

בקובץ `.env`:

```env
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4.1-mini
OPENAI_IMAGE_MODEL=gpt-image-1
OPENAI_IMAGE_SIZE=1024x1024
```

## הרצה

```bash
uvicorn app.main:app --reload
```

ולפתוח:

```text
http://127.0.0.1:8000
```

## מה קורה בלחיצה על יצירת ספר

- Agent 1: משפר את טקסט הספר
- Agent 2: מייצר Prompt לתמונת שער
- Agent 3: מייצר Prompt לכל עמוד
- Image Agent: יוצר PNG 
אמיתי לכל דף
- Export Agent: בונה HTML/CSS/JS + assets + ZIP
## מה ה-ZIP שנוצר מכי
- `index.html`
- `style.css`
- `script.js`
- `book.json`
- `assets/cover.png`
- `assets/page-1.png`
- `assets/page-2.png`
- וכו'

## הערה

בגרסה הזו ה-Key נשאר רק בשרת בתוך `.env`.
