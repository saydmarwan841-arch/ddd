@echo off
REM اختبار الحب الرومانسي - سكريبت التشغيل السريع

echo.
echo ========================================
echo   اختبار الحب الرومانسي - النسخة العربية
echo ========================================
echo.

REM التحقق من وجود Python
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ خطأ: Python غير مثبت!
    echo.
    echo يرجى تثبيت Python من: https://www.python.org
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ تم العثور على Python
echo.

REM التحقق من وجود Flask
python -m pip show flask >nul 2>&1
if errorlevel 1 (
    echo.
    echo 📦 جاري تثبيت المتطلبات...
    echo.
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ❌ فشل تثبيت المتطلبات!
        echo.
        pause
        exit /b 1
    )
)

echo.
echo ✅ جميع المتطلبات موجودة
echo.

REM التحقق من وجود ملف questions_ar.json
if not exist questions_ar.json (
    echo.
    echo ⚠️  تحذير: ملف questions_ar.json غير موجود!
    echo.
)

echo.
echo 🚀 جاري تشغيل التطبيق...
echo.
echo ========================================
echo   تطبيق اختبار الحب الرومانسي
echo   URL: http://localhost:5000
echo ========================================
echo.
echo 💡 نصيحة: افتح متصفحك على:
echo    http://localhost:5000
echo.
echo 🔐 دخول المسؤول:
echo    http://localhost:5000/admin/login
echo    كلمة المرور: love2024
echo.
echo.

python app.py

pause
