#!/bin/bash

# 🚀 سكريبت تشغيل مشروع HAZM

echo "🔧 جارِ إعداد البيئة..."

# الانتقال لمجلد المشروع
cd "$(dirname "$0")"

# تفعيل البيئة الافتراضية
if [ -d ".venv" ]; then
    echo "✅ تفعيل البيئة الافتراضية..."
    source .venv/bin/activate
else
    echo "⚠️  البيئة الافتراضية غير موجودة. قم بإنشائها أولاً:"
    echo "   python -m venv .venv"
    echo "   source .venv/bin/activate"
    echo "   pip install -r backend/requirements.txt"
    exit 1
fi

# التحقق من عمل Backend
if pgrep -f "python backend/app.py" > /dev/null; then
    echo "⚠️  Backend يعمل بالفعل!"
    echo "   لإيقافه: pkill -f 'python backend/app.py'"
    echo "   لإعادة التشغيل: pkill -f 'python backend/app.py' && ./start.sh"
    exit 1
fi

echo "🚀 تشغيل Backend..."
nohup python backend/app.py > backend.log 2>&1 &
BACKEND_PID=$!

# الانتظار حتى يبدأ Backend
echo "⏳ انتظار تشغيل Backend..."
for i in {1..10}; do
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
        echo "✅ Backend جاهز على http://localhost:8000"
        break
    fi
    sleep 1
done

# عرض معلومات التشغيل
echo ""
echo "✅ المشروع يعمل الآن!"
echo ""
echo "📍 الروابط:"
echo "   Backend:  http://localhost:8000"
echo "   Frontend: افتح frontend/index.html في المتصفح"
echo ""
echo "📝 السجلات:"
echo "   tail -f backend.log"
echo ""
echo "🛑 لإيقاف Backend:"
echo "   pkill -f 'python backend/app.py'"
echo ""
