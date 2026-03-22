# בריף סטטוס הפרויקט — OFDM Simulator (לפי השלבים שהוגדרו)

מסמך קצר לפורטפוליו / סיכום עבודה. הקוד המלא ב־GitHub; להרצה ב־Windows מומלץ `py` (ראו README).

---

## מה הפרויקט עושה

סימולטור **OFDM בבייסבנד** (QPSK, 16-QAM): משדר → ערוץ (AWGN / מולטיפאת) → מקלט עם שוויון ZF/MMSE, **EVM**, **פיילוטים** להערכת ערוץ, ובדיקות יחידה.

מעל זה נבנתה שכבת **RF Validation**: ליקויים (כולל CFO) → מדידות (EVM, BER, הספק ממוצע) → ספי YAML → **PASS/FAIL** ודוחות JSON/CSV.

---

## שלבים לפי התכנון (ומה בוצע)

### שלב 0 — תהליך עבודה עם Git

- ענפי פיצ’רים, קומיטים, PR — **מתועדים** ב־README / תכנון.
- ענף `rf-validation-layer` פותח את שכבת ה־validation; התוכן **מוזג ל־`main`** (קומיט כולל מטריצה, מסמכי TEST_PLAN וכו’).

### שלבים 1–5 (ליבת הסימולטור)

| שלב | נושא | סטטוס |
|-----|--------|--------|
| 1 | ערוץ מולטיפאת | **בוצע** |
| 2 | שוויון ZF / MMSE | **בוצע** |
| 3 | סקריפטי סימולציה (`--channel`, `--equalize`) | **בוצע** |
| 4 | קונפיג ותיעוד | **בוצע** |
| 5 | Lessons learned | **בוצע** (`docs/lessons_learned.md`) |

### הרחבות ליבה (PHY)

| נושא | סטטוס |
|------|--------|
| EVM | **בוצע** (`src/evm.py`, סיכומי תוצאות) |
| פיילוטים + LS channel estimation | **בוצע** (`src/pilots.py`) |

### שכבת RF Validation (מסלול “בדיקות / תיקוף”)

| פריט | סטטוס |
|------|--------|
| מודול `src/rf_impairments/` (CFO, שרשרת ליקויים) | **בוצע** |
| מדידות `src/measurements/` (כולל הספק ממוצע) | **בוצע** |
| `src/validation/` — YAML, ספים, margins, מטריצת מקרים | **בוצע** |
| קונפיגים: smoke + `test_matrix_default.yaml` | **בוצע** |
| הרצות: `run_validation_smoke.py`, `run_validation_matrix.py` | **בוצע** |
| מסמכים: `VALIDATION_OVERVIEW`, `TEST_PLAN`, דוגמת דוח | **בוצע** |
| בדיקות pytest לשכבה | **בוצע** |

---

## מה רץ אצלך מקומית (תקין)

- **`py -m pytest`** — כל הבדיקות עוברות.
- **Smoke validation** — בדרך כלל **PASS**.
- **מטריצה** — במקרה `cfo_mild_qpsk` מוגדר `cfo_correction_mode: cp` (אומד CFO מ־CP, לא oracle). אפשר גם `genie` או `none`; ראה `docs/TEST_PLAN.md`.

---

## השלב הבא במסלול RF (פיתוח)

1. **אומד CFO מ־CP** — **בוצע** (`cfo_correction_mode: cp`). אופציונלי: פיילוטים / מעקב שיורי.  
2. **רעש פאזה** → **סנכרון זמן (STO)** → (אופציונלי) PA, CI.  
3. פירוט מסודר: `docs/RF_ROADMAP.md`.

---

## קבצים מרכזיים להמשך

- תכנון המשך (אנגלית): `docs/next_phase_plan.md`
- תוכנית בדיקות: `docs/TEST_PLAN.md`
- סקירת validation: `docs/VALIDATION_OVERVIEW.md`

*עודכן בהתאם למצב הריפו לאחר מיזוג שכבת ה־validation ל־`main`.*
