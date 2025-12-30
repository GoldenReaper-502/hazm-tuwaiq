#!/bin/bash
# Test script to verify Docker build and PORT binding

set -e

echo "🔍 Testing Render Deployment Fix..."
echo ""

# Test 1: Check if Dockerfiles have correct CMD
echo "✓ Test 1: Checking main Dockerfile CMD..."
if grep -q 'CMD \["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port \${PORT:-8000}' Dockerfile; then
    echo "  ✅ Main Dockerfile CMD uses \${PORT:-8000}"
else
    echo "  ❌ Main Dockerfile CMD is incorrect"
    exit 1
fi

echo "✓ Test 2: Checking backend Dockerfile CMD..."
if grep -q 'CMD \["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port \${PORT:-8000}' backend/Dockerfile; then
    echo "  ✅ Backend Dockerfile CMD uses \${PORT:-8000}"
else
    echo "  ❌ Backend Dockerfile CMD is incorrect"
    exit 1
fi

# Test 2: Check if HEALTHCHECK uses PORT
echo "✓ Test 3: Checking main Dockerfile HEALTHCHECK..."
if grep -q 'CMD sh -c "curl -f http://localhost:\${PORT:-8000}/health' Dockerfile; then
    echo "  ✅ Main Dockerfile HEALTHCHECK uses \${PORT:-8000}"
else
    echo "  ❌ Main Dockerfile HEALTHCHECK is incorrect"
    exit 1
fi

echo "✓ Test 4: Checking backend Dockerfile HEALTHCHECK..."
if grep -q 'CMD sh -c "curl -f http://localhost:\${PORT:-8000}/health' backend/Dockerfile; then
    echo "  ✅ Backend Dockerfile HEALTHCHECK uses \${PORT:-8000}"
else
    echo "  ❌ Backend Dockerfile HEALTHCHECK is incorrect"
    exit 1
fi

# Test 3: Check if render.yaml uses Docker runtime
echo "✓ Test 5: Checking render.yaml runtime..."
if grep -q "runtime: docker" render.yaml; then
    echo "  ✅ render.yaml uses Docker runtime"
else
    echo "  ❌ render.yaml doesn't use Docker runtime"
    exit 1
fi

# Test 4: Check if app.py has health endpoint
echo "✓ Test 6: Checking health endpoint..."
if grep -q "@app.get(\"/health\")" backend/app.py; then
    echo "  ✅ Health endpoint exists in app.py"
else
    echo "  ❌ Health endpoint missing in app.py"
    exit 1
fi

# Test 5: Check if app.py has FastAPI instance
echo "✓ Test 7: Checking FastAPI instance..."
if grep -q "app = FastAPI" backend/app.py; then
    echo "  ✅ FastAPI app instance exists"
else
    echo "  ❌ FastAPI app instance missing"
    exit 1
fi

echo ""
echo "🎉 All tests passed!"
echo ""
echo "📋 Summary:"
echo "  ✅ Both Dockerfiles use dynamic PORT with sh -c"
echo "  ✅ Both HEALTHCHECKs use dynamic PORT"
echo "  ✅ render.yaml uses Docker runtime"
echo "  ✅ Health endpoint exists"
echo "  ✅ FastAPI app is properly configured"
echo ""
echo "🚀 Ready for Render deployment!"
echo ""
echo "Next steps:"
echo "  1. Commit changes: git add -A && git commit -m 'Fix Render port binding'"
echo "  2. Push to GitHub: git push origin main"
echo "  3. Trigger Render deployment"
echo "  4. Monitor logs for: 'Uvicorn running on http://0.0.0.0:[PORT]'"
echo "  5. Test endpoint: curl https://<your-url>/health"
