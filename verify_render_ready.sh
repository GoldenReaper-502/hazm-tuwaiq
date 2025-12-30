#!/bin/bash
# Final verification before Render deployment

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     RENDER DEPLOYMENT - FINAL VERIFICATION                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASS=0
FAIL=0

check_pass() {
    echo -e "${GREEN}✅ PASS${NC} - $1"
    ((PASS++))
}

check_fail() {
    echo -e "${RED}❌ FAIL${NC} - $1"
    ((FAIL++))
}

check_warn() {
    echo -e "${YELLOW}⚠️  WARN${NC} - $1"
}

echo "1. Checking Dockerfile configuration..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check for correct libgl1 package
if grep -q "libgl1" Dockerfile && ! grep -q "libgl1-mesa-glx" Dockerfile; then
    check_pass "libgl1 (not libgl1-mesa-glx) in Dockerfile"
else
    check_fail "libgl1 package not correctly configured"
fi

# Check for required runtime libs
required_libs=("libglib2.0-0" "libgomp1" "libsm6" "libxrender1" "libxext6")
for lib in "${required_libs[@]}"; do
    if grep -q "$lib" Dockerfile; then
        check_pass "$lib in Dockerfile"
    else
        check_fail "$lib missing from Dockerfile"
    fi
done

echo ""
echo "2. Checking requirements.txt..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check for opencv-python-headless
if grep -q "opencv-python-headless" backend/requirements.txt; then
    check_pass "opencv-python-headless in requirements.txt"
else
    check_fail "opencv-python-headless not in requirements.txt"
fi

# Check for conflicting opencv-python
if grep -q "^opencv-python[^-]" backend/requirements.txt; then
    check_fail "opencv-python (non-headless) found - REMOVE IT"
else
    check_pass "No conflicting opencv-python package"
fi

echo ""
echo "3. Checking lazy cv2 imports..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check for _get_cv2 helper function
files_to_check=(
    "backend/cctv/rtsp_handler.py"
    "backend/ai_core/yolo_engine.py"
    "backend/ai_core/pose_estimation.py"
    "backend/ai_core/fatigue_detection.py"
    "backend/cctv/frame_processor.py"
    "backend/cctv.py"
)

for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        if grep -q "def _get_cv2()" "$file"; then
            check_pass "_get_cv2() found in $file"
        else
            check_warn "_get_cv2() not in $file (might not need it)"
        fi
        
        # Check for top-level cv2 import (bad)
        if grep -E "^import cv2" "$file" > /dev/null 2>&1; then
            check_fail "Top-level 'import cv2' found in $file - MUST BE LAZY"
        fi
    fi
done

echo ""
echo "4. Testing Python imports..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd backend
python3 -c "
import sys
modules = [
    'cctv.rtsp_handler',
    'ai_core.yolo_engine',
    'ai_core.pose_estimation',
    'ai_core.fatigue_detection',
    'cctv.frame_processor'
]
failed = []
for mod in modules:
    try:
        __import__(mod)
    except Exception as e:
        failed.append(f'{mod}: {e}')
        
if failed:
    print('FAIL:', '\n'.join(failed))
    sys.exit(1)
else:
    print('ALL_OK')
" 2>/dev/null

if [ $? -eq 0 ]; then
    check_pass "All Python modules import without crash"
else
    check_fail "Some Python modules failed to import"
fi

cd ..

echo ""
echo "5. Testing cv2 lazy loading..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 test_cv2_import.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    check_pass "cv2 lazy loading works correctly"
else
    check_fail "cv2 lazy loading test failed"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                   VERIFICATION SUMMARY                     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo -e "  ${GREEN}Passed:${NC} $PASS"
echo -e "  ${RED}Failed:${NC} $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║          ✅ READY FOR RENDER DEPLOYMENT ✅                 ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. git add -A"
    echo "  2. git commit -m 'Fix: OpenCV lazy loading for Render'"
    echo "  3. git push origin main"
    echo ""
    echo "Render will auto-deploy with these fixes! 🚀"
    exit 0
else
    echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║           ❌ DEPLOYMENT NOT READY ❌                       ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Please fix the failed checks above before deploying."
    exit 1
fi
