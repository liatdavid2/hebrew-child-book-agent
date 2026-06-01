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

<img width="1918" height="965" alt="image" src="https://github.com/user-attachments/assets/35597c58-8b81-4688-a346-539c8291228a" />

<img width="1919" height="968" alt="image" src="https://github.com/user-attachments/assets/8c50fdc9-988e-49a0-803a-5487554866d5" />

<img width="1919" height="965" alt="image" src="https://github.com/user-attachments/assets/2caffe8d-0738-4282-a1dd-1809543ead43" />


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
- Image Agent: יוצר PNG אמיתי לכל דף
- Export Agent: בונה HTML/CSS/JS + assets + ZIP

## מה ה-ZIP שנוצר מכיל

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
