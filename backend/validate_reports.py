#!/usr/bin/env python
"""
Validation script for new Report endpoints.
Tests auto-report generation, listing, and export functions.
"""
import requests
import base64
import json
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"

def test_reports():
    """Test report endpoints."""
    print("\n=== Testing Reports Endpoints ===\n")
    
    # 1. Create a test detection (with objects to trigger auto-report)
    print("1. Creating test detection...")
    sample_png = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100  # Minimal PNG
    frame_b64 = base64.b64encode(sample_png).decode()
    
    det_resp = requests.post(
        f"{BASE_URL}/detect",
        json={"frame_data": frame_b64},
        headers={"Content-Type": "application/json"}
    )
    if det_resp.status_code == 200:
        det_id = det_resp.json()["id"]
        print(f"   ✓ Detection created: {det_id}")
    else:
        print(f"   ✗ Detection failed: {det_resp.status_code} {det_resp.text}")
        return False
    
    # 2. List auto-reports
    print("\n2. Listing auto-generated reports...")
    reports_resp = requests.get(f"{BASE_URL}/reports/auto")
    if reports_resp.status_code == 200:
        reports = reports_resp.json()
        print(f"   ✓ Found {len(reports)} auto-report(s)")
        if reports:
            report = reports[0]
            print(f"   - Report ID: {report.get('id')}")
            print(f"   - Risk Level: {report.get('risk_level')}")
            print(f"   - Risk Score: {report.get('risk_score')}")
            print(f"   - Objects: {report.get('objects_count')}")
    else:
        print(f"   ✗ List reports failed: {reports_resp.status_code}")
        return False
    
    # 3. Get single report (if any exist)
    if reports:
        print("\n3. Getting single report...")
        report_id = reports[0]["id"]
        single_resp = requests.get(f"{BASE_URL}/reports/{report_id}")
        if single_resp.status_code == 200:
            print(f"   ✓ Retrieved report: {report_id}")
        else:
            print(f"   ✗ Get report failed: {single_resp.status_code}")
    
    # 4. Export to CSV
    print("\n4. Testing CSV export...")
    csv_resp = requests.get(f"{BASE_URL}/reports/export?format=csv")
    if csv_resp.status_code == 200:
        csv_len = len(csv_resp.text)
        print(f"   ✓ CSV export successful ({csv_len} bytes)")
    else:
        print(f"   ✗ CSV export failed: {csv_resp.status_code}")
    
    # 5. Export to JSON
    print("\n5. Testing JSON export...")
    json_resp = requests.get(f"{BASE_URL}/reports/export?format=json")
    if json_resp.status_code == 200:
        json_len = len(json_resp.text)
        print(f"   ✓ JSON export successful ({json_len} bytes)")
    else:
        print(f"   ✗ JSON export failed: {json_resp.status_code}")
    
    # 6. Test PDF export (may fail if reportlab not installed)
    print("\n6. Testing PDF export...")
    pdf_resp = requests.get(f"{BASE_URL}/reports/export?format=pdf")
    if pdf_resp.status_code == 200:
        pdf_len = len(pdf_resp.content)
        print(f"   ✓ PDF export successful ({pdf_len} bytes)")
    elif pdf_resp.status_code == 503:
        print(f"   ⚠ PDF export not available (reportlab not installed)")
    else:
        print(f"   ✗ PDF export failed: {pdf_resp.status_code}")
    
    # 7. Test Excel export (may fail if openpyxl not installed)
    print("\n7. Testing Excel export...")
    excel_resp = requests.get(f"{BASE_URL}/reports/export?format=excel")
    if excel_resp.status_code == 200:
        excel_len = len(excel_resp.content)
        print(f"   ✓ Excel export successful ({excel_len} bytes)")
    elif excel_resp.status_code == 503:
        print(f"   ⚠ Excel export not available (openpyxl not installed)")
    else:
        print(f"   ✗ Excel export failed: {excel_resp.status_code}")
    
    print("\n=== Reports Tests Complete ===\n")
    return True

if __name__ == "__main__":
    try:
        success = test_reports()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test error: {e}")
        exit(1)
