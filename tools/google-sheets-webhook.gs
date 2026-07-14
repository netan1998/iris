/**
 * ═══════════════════════════════════════════════════════════════
 * חיבור הטפסים לגוגל שיטס - הוראות הקמה (3 דקות, פעם אחת)
 * ═══════════════════════════════════════════════════════════════
 *
 * 1. פותחים גיליון חדש: https://sheets.new
 *    נותנים לו שם, למשל: "לידים - שבוע החוזק"
 *
 * 2. בתפריט הגיליון: תוספים (Extensions) ← Apps Script
 *
 * 3. מוחקים את הקוד שמופיע שם ומדביקים את כל הקובץ הזה במקומו
 *
 * 4. לוחצים "פריסה" (Deploy) ← "פריסה חדשה" (New deployment)
 *    - סוג: "אפליקציית אינטרנט" (Web app)
 *    - Execute as: Me
 *    - Who has access: Anyone   ← חשוב! אחרת הטופס לא יוכל לשלוח
 *    - לוחצים Deploy ומאשרים את ההרשאות
 *
 * 5. מעתיקים את כתובת ה-Web app (מתחילה ב-https://script.google.com/macros/...)
 *    ושולחים לי אותה בצ'אט - אני אחבר אותה לדף ואפרוס
 *
 * מה זה נותן:
 * - כל השארת פרטים נשמרת כשורה בגיליון (תאריך, שם, טלפון, עמוד)
 * - מייל התראה מיידי לאיריס על כל ליד חדש
 * ═══════════════════════════════════════════════════════════════
 */

// ✏️ למי לשלוח מייל על כל ליד חדש (אפשר גם כמה, מופרדים בפסיק):
var NOTIFY_EMAIL = 'irisgabbay@gmail.com';

function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.tryLock(5000);
  try {
    var data = JSON.parse(e.postData.contents);
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];

    // שורת כותרות בפעם הראשונה
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(['תאריך ושעה', 'שם', 'טלפון', 'הגיע מהעמוד']);
      sheet.getRange('A1:D1').setFontWeight('bold');
    }

    // הגרש לפני הטלפון שומר על האפס המוביל
    sheet.appendRow([
      new Date(),
      data.name || '',
      "'" + (data.phone || ''),
      data.page || ''
    ]);

    // מייל התראה
    if (NOTIFY_EMAIL) {
      MailApp.sendEmail(
        NOTIFY_EMAIL,
        '🎉 ליד חדש משבוע החוזק: ' + (data.name || ''),
        'שם: ' + (data.name || '') + '\n' +
        'טלפון: ' + (data.phone || '') + '\n' +
        'זמן: ' + new Date().toLocaleString('he-IL', { timeZone: 'Asia/Jerusalem' }) + '\n\n' +
        'כל הלידים בגיליון: ' + SpreadsheetApp.getActiveSpreadsheet().getUrl()
      );
    }
  } catch (err) {
    // שגיאה לא מפילה את הטופס אצל הלקוחה
  } finally {
    lock.releaseLock();
  }
  return ContentService.createTextOutput('ok');
}
