# Git — העלאת השינויים (לפי הנתיב שלך)

## אם PowerShell אומר "git is not recognized"

Git מותקן אבל **לא ב־PATH** של הטרמינל (למשל Cursor/Terminal לא רואה אותו). מה לעשות:

1. **סגור את Cursor לגמרי ופתח מחדש** — לפעמים PATH מתעדכן רק אחרי פתיחה מחדש.
2. אם עדיין לא עובד — **הוסף את Git ל־PATH ב־Windows:**
   - חיפוש ב־Windows: "Environment Variables" → "Edit the system environment variables".
   - "Environment Variables" → תחת "User variables" בחר "Path" → "Edit" → "New".
   - הוסף את הנתיב להתקנת Git, למשל: `C:\Program Files\Git\cmd`
   - אישור בכל החלונות, **סגור Cursor ופתח מחדש**.
3. **אופציה:** הרץ Git מתוך **Git Bash** (אם הותקן עם Git for Windows) — שם `git` תמיד זמין.

---

## חשוב: מאיפה להריץ Git

**Git רץ תמיד מתוך שורש הפרויקט** — התיקייה שבה נמצאים `run_simulation.py`, `src/`, `simulations/`, `tests/` — **לא** מתוך `simulations/`.

- **שורש הפרויקט (נכון):**  
  `C:\Users\oraza\OneDrive\שולחן העבודה\OFDM-Simulator-Python-1`

- **תת־תיקייה (לא להריץ משם):**  
  `C:\Users\oraza\OneDrive\שולחן העבודה\OFDM-Simulator-Python-1\simulations`  
  כאן נמצא `run_ber_and_constellation.py` — אבל את פקודות ה־Git מריצים **מרמה אחת למעלה**, משורש הפרויקט.

אם תריץ `git` מתוך `simulations/`, Git יחפש תיקיית `.git` שם ולא ימצא (הרפו הוא כל הפרויקט), ולכן לא יהיה סנכרון.

---

## שלב 1: מעבר לשורש הפרויקט

ב־PowerShell הרץ:

```powershell
cd "C:\Users\oraza\OneDrive\שולחן העבודה\OFDM-Simulator-Python-1"
```

(או: פתח Cursor עם התיקייה הזו כ־Workspace, ופתח Terminal — אז כבר תהיה בתיקייה הזו.)

---

## שלב 2: בדיקה אם יש כבר רפו Git

```powershell
git status
```

- **אם מופיע משהו כמו "On branch main" או "On branch master"** — יש רפו, עבור לשלב 3.
- **אם מופיע "not a git repository"** — אין עדיין `.git`. עבור לשלב 2א.

### שלב 2א: אם אין רפו (פעם ראשונה)

```powershell
git init
git remote add origin https://github.com/OR-AZARKMAN/OFDM-Simulator-Python-1.git
```

- **OR-AZARKMAN** = שם המשתמש שלך ב־GitHub.  
- **OFDM-Simulator-Python-1** = שם הרפו ב־GitHub (כמו שם התיקייה). אם ב־GitHub יצרת רפו בשם אחר — החלף בהתאם.

---

## שלב 3: בדיקת חיבור ל־GitHub (remote)

```powershell
git remote -v
```

אמור להופיע משהו כמו:

```
origin  https://github.com/OR-AZARKMAN/OFDM-Simulator-Python-1.git (fetch)
origin  https://github.com/OR-AZARKMAN/OFDM-Simulator-Python-1.git (push)
```

אם לא מופיע כלום — הרפו לא מחובר. הרץ:

```powershell
git remote add origin https://github.com/OR-AZARKMAN/OFDM-Simulator-Python-1.git
```

(אם ב־GitHub הרפו נקרא אחרת — החלף את `OFDM-Simulator-Python-1` בשם הרפו.)

---

## שלב 4: העלאת כל השינויים (add → commit → push)

**כל הפקודות האלו רצות מתוך שורש הפרויקט** (אחרי `cd` לנתיב למעלה).

```powershell
git add -A
git status
git commit -m "OFDM simulator: PHY chain, BER validation, tests, CI, docs cleanup"
git push -u origin main
```

אם ב־GitHub הבranch נקרא **master** (ולא main), הרץ במקום:

```powershell
git push -u origin master
```

אם יופיע שגיאה על branch — בדוק ב־GitHub איזה branch קיים (main או master) והשתמש באותו שם.

---

## סיכום — סדר מלא (העתק והרץ)

```powershell
cd "C:\Users\oraza\OneDrive\שולחן העבודה\OFDM-Simulator-Python-1"
git status
git add -A
git status
git commit -m "OFDM simulator: PHY chain, BER validation, tests, CI, docs cleanup"
git push -u origin main
```

(אם `git push -u origin main` נכשל עם "branch not found", נסה `git push -u origin master`.)

---

## אם אתה לא רוצה להעלות את `results/` ל־Git

לפני `git add -A` — פתח את הקובץ `.gitignore` בשורש הפרויקט והוסף שורה:

```
results/
```

שמור, ואז הרץ שוב את הפקודות משלב 4.
