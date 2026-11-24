---
name: assess-core-knowledge
description: Entry point for assessing or practicing a ClearPath AI student's core knowledge (ידע ליבה) in an oral-exam style session. Use when a teacher or student asks to assess, test, quiz, examine or practice core knowledge, run a שיחת בדיקה / מבחן בעל פה / הערכת ידע ליבה, or check readiness for the project defense (הגנה), and no single topic has been named. Routes to the topic skills (algorithms, computer architecture, networking, database, security, performance, LLM and classifier, AI agent) and writes an evidence report for the teacher.
---

# הערכת ידע ליבה · נקודת כניסה

הכישור מנהל שיחת בדיקה בעל פה על מושגי הליבה של פרויקט ClearPath AI, לפי [מסמך האפיון](../../../docs/specification.md).

## לפני הכול

קרא את [הפרוטוקול המשותף](protocol.md) ופעל לפיו לאורך כל השיחה. הוא קובע את התפקיד שלך (בוחן, לא מורה פרטי), את ההבדל בין מצב הערכה למצב תרגול, את אופן השיפוט ואת מבנה הדוח.

## בחירת נושא

אם המשתמש לא בחר נושא, הצג את הרשימה ובקש לבחור אחד. אפשר גם "סקירה כללית" (סעיף להלן).

| נושא | כישור | סעיפי אפיון |
| --- | --- | --- |
| אלגוריתמים: ניתוב, גל ירוק, Geofencing | [assess-algorithms](../assess-algorithms/SKILL.md) | 3.1, 3.2, 3.3, 6.2 |
| מבנה המחשב | [assess-computer-architecture](../assess-computer-architecture/SKILL.md) | 6.3 |
| תקשורת ואינטרנט | [assess-networking](../assess-networking/SKILL.md) | 6.5, 4 |
| בסיס נתונים | [assess-database](../assess-database/SKILL.md) | 6.4 |
| אבטחת מידע | [assess-security](../assess-security/SKILL.md) | 6.1 |
| ביצועים | [assess-performance](../assess-performance/SKILL.md) | 6.2 |
| מודל שפה ומודל סיווג | [assess-llm-classifier](../assess-llm-classifier/SKILL.md) | 6.6 |
| סוכן AI: עוזר מוקדן | [assess-ai-agent](../assess-ai-agent/SKILL.md) | 6.7 |

אחרי הבחירה, קרא את קובץ ה-`SKILL.md` של הנושא, והשתמש במושגי הליבה ובבנק השאלות שבו.

## סקירה כללית

לבדיקת מוכנות להגנה: שתי שאלות מכל אחד משלושה או ארבעה נושאים. כלול תמיד את הנושא של הרכיב שהתלמיד הוא הבעלים שלו. התחל בשאלת החלטה במערכת, ולא בשאלת הגדרה. הדוח נשמר בשם `<YYYY-MM-DD>_overview.md`, ובטבלת הראיות מופיעה עמודה נוספת לנושא.

## אם התלמיד מבקש ללמוד ולא להיבחן

הסבר שהכישור הזה בודק ידע. במצב תרגול מותר לך לתת רמז ומשוב אחרי כל תשובה, אבל לא שיעור מלא. להסבר מעמיק, הפנה לסעיפי האפיון הרלוונטיים ולמורה.
