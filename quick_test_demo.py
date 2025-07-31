#!/usr/bin/env python3
"""
Apollo AI - Automated Testing Demo
Tests all endpoints programmatically for quick validation
"""

import requests
import json
import time
import os
from pathlib import Path

# API Base URL
BASE_URL = "http://localhost:8000"

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print(f"{'='*60}")

def test_upload():
    """Test file upload"""
    print_header("TESTING FILE UPLOAD")
    
    # Find a sample CSV file
    uploads_dir = Path("uploads")
    if not uploads_dir.exists():
        print("❌ No uploads directory found")
        return None
    
    csv_files = list(uploads_dir.glob("*.csv"))
    if not csv_files:
        print("❌ No CSV files found in uploads directory")
        return None
    
    sample_file = csv_files[0]
    print(f"📁 Using sample file: {sample_file.name}")
    
    try:
        with open(sample_file, 'rb') as f:
            files = {'file': (sample_file.name, f, 'text/csv')}
            response = requests.post(f"{BASE_URL}/upload", files=files)
        
        if response.status_code == 200:
            data = response.json()
            file_id = data.get('file_id')
            print(f"✅ Upload successful! File ID: {file_id}")
            return file_id
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return None

def test_analyze(file_id):
    """Test data analysis"""
    print_header("TESTING DATA ANALYSIS")
    
    try:
        response = requests.post(f"{BASE_URL}/analyze", json={"file_id": file_id})
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Analysis successful!")
            print(f"📊 Dataset: {data['summary']['total_rows']} rows, {data['summary']['total_columns']} columns")
            print(f"⏱️ Analysis time: {data.get('analysis_time', 'N/A')}")
            return True
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return False

def test_insights(file_id):
    """Test AI insights"""
    print_header("TESTING AI INSIGHTS")
    
    try:
        response = requests.post(f"{BASE_URL}/insight", json={
            "file_id": file_id,
            "llm_provider": "groq"
        })
        
        if response.status_code == 200:
            data = response.json()
            print("✅ AI Insights generated!")
            print(f"🤖 Provider: {data.get('provider', 'N/A')}")
            print(f"📝 Summary: {data['insights']['executive_summary'][:100]}...")
            return True
        else:
            print(f"❌ Insights failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Insights error: {e}")
        return False

def test_visualizations(file_id):
    """Test visualization generation"""
    print_header("TESTING VISUALIZATIONS")
    
    try:
        # Get available visualizations
        response = requests.get(f"{BASE_URL}/visualize/{file_id}")
        
        if response.status_code == 200:
            data = response.json()
            available_charts = data.get('available_visualizations', [])
            print(f"✅ Found {len(available_charts)} available chart types")
            
            if available_charts:
                # Test first chart type
                chart_type = available_charts[0]
                print(f"📈 Testing chart type: {chart_type}")
                
                chart_response = requests.post(f"{BASE_URL}/visualize/{file_id}/{chart_type}")
                if chart_response.status_code == 200:
                    chart_data = chart_response.json()
                    print(f"✅ Chart generated: {chart_data.get('chart_type', 'N/A')}")
                    return True
                else:
                    print(f"❌ Chart generation failed: {chart_response.status_code}")
                    return False
            else:
                print("⚠️ No chart types available")
                return False
        else:
            print(f"❌ Visualization check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Visualization error: {e}")
        return False

def test_files():
    """Test file listing"""
    print_header("TESTING FILE MANAGEMENT")
    
    try:
        response = requests.get(f"{BASE_URL}/files")
        
        if response.status_code == 200:
            data = response.json()
            files = data.get('files', [])
            print(f"✅ Found {len(files)} uploaded files")
            for file_info in files:
                print(f"   📁 {file_info.get('filename', 'N/A')} ({file_info.get('size', 'N/A')} bytes)")
            return True
        else:
            print(f"❌ File listing failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ File listing error: {e}")
        return False

def run_full_demo():
    """Run complete demo"""
    print("""
🚀 APOLLO AI - AUTOMATED DEMO
==================================================
🎯 Testing all endpoints automatically...
==================================================
""")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print("❌ Server not running! Please start the server first:")
            print("   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
            return
    except:
        print("❌ Cannot connect to server! Please start the server first:")
        print("   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return
    
    print("✅ Server is running!")
    
    # Run tests
    results = []
    
    # Test file upload
    file_id = test_upload()
    if file_id:
        results.append(("Upload", "✅ PASS"))
        
        # Test analysis
        if test_analyze(file_id):
            results.append(("Analysis", "✅ PASS"))
        else:
            results.append(("Analysis", "❌ FAIL"))
        
        # Test insights
        if test_insights(file_id):
            results.append(("AI Insights", "✅ PASS"))
        else:
            results.append(("AI Insights", "❌ FAIL"))
        
        # Test visualizations
        if test_visualizations(file_id):
            results.append(("Visualizations", "✅ PASS"))
        else:
            results.append(("Visualizations", "❌ FAIL"))
    else:
        results.append(("Upload", "❌ FAIL"))
    
    # Test file management
    if test_files():
        results.append(("File Management", "✅ PASS"))
    else:
        results.append(("File Management", "❌ FAIL"))
    
    # Print results
    print_header("DEMO RESULTS")
    for test, result in results:
        print(f"{test:20} {result}")
    
    passed = sum(1 for _, result in results if "PASS" in result)
    total = len(results)
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Your Apollo AI backend is working perfectly!")
    else:
        print("⚠️ Some tests failed. Check the server logs for details.")

if __name__ == "__main__":
    run_full_demo() 