#!/bin/bash

# 🛑 سكريبت إيقاف مشروع HAZM

echo "🛑 جارِ إيقاف Backend..."

if pgrep -f "python backend/app.py" > /dev/null; then
    pkill -f "python backend/app.py"
    echo "✅ تم إيقاف Backend"
else
    echo "⚠️  Backend ليس قيد التشغيل"
fi

echo ""
echo "✅ تم!"
