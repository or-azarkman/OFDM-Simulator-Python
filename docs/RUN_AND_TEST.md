# הרצת סימולציות ובדיקות

## הרצת סימולציות (Multipath)

**500 סימבולים (הרצה מהירה):**
```
py run_simulation.py --channel multipath --symbols 500
```

**5000 סימבולים (הרצה מלאה):**
```
py run_simulation.py --channel multipath --symbols 5000
```

**שתי ההרצות ברצף (500 ואז 5000):**
```
py run_simulation.py --channel multipath --symbols 500
py run_simulation.py --channel multipath --symbols 5000
```
---

## הרצת בדיקות

**מהשורש של הפרויקט:**

```
py -m pytest tests/ -v
```

**עם פירוט שגיאות מלא:**
```
py -m pytest tests/ -v --tb=long
```

**(coverage):**
```powershell
py -m pip install pytest-cov
py -m pytest tests/ -v --cov=src --cov-report=term-missing
```
