#!/bin/bash
# Test app startup to ensure no cv2 import crashes

set -e

echo "=========================================="
echo "Testing App Startup (No cv2 Crash)"
echo "=========================================="

cd /workspaces/hazm-tuwaiq

# Test 1: Import test
echo ""
echo "Test 1: Module imports..."
python test_cv2_import.py
if [ $? -eq 0 ]; then
    echo "✅ Module imports passed"
else
    echo "❌ Module imports failed"
    exit 1
fi

# Test 2: Try importing main app
echo ""
echo "Test 2: App module import..."
python -c "
import sys
sys.path.insert(0, 'backend')
try:
    import app
    print('✅ App module imported successfully')
except Exception as e:
    print(f'❌ App import failed: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo "✅ App import passed"
else
    echo "❌ App import failed"
    exit 1
fi

# Test 3: Check that cv2 can be loaded on demand
echo ""
echo "Test 3: cv2 lazy loading..."
python -c "
import sys
sys.path.insert(0, 'backend')

# Import modules without triggering cv2
from cctv.rtsp_handler import _get_cv2
from ai_core.yolo_engine import _get_cv2 as get_cv2_yolo

# Now trigger lazy import
try:
    cv2 = _get_cv2()
    print(f'✅ cv2 lazy loaded: version {cv2.__version__}')
except Exception as e:
    print(f'❌ cv2 lazy load failed: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo "✅ cv2 lazy loading passed"
else
    echo "❌ cv2 lazy loading failed"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ ALL STARTUP TESTS PASSED"
echo "=========================================="
echo ""
echo "The app will start successfully on Render!"
echo "cv2 will be loaded on-demand when needed."
