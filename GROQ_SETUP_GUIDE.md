# 🚀 **GROQ API SETUP GUIDE**

## **Why Groq?**

- ✅ **FREE**: 1000 requests per day
- ✅ **FAST**: Ultra-fast response times
- ✅ **RELIABLE**: High uptime and quality
- ✅ **NO CREDIT CARD**: Required for signup

---

## **📋 STEP-BY-STEP SETUP**

### **1. Get Free Groq API Key**

1. **Visit**: https://console.groq.com/
2. **Sign Up**: Create a free account
3. **Get API Key**: Copy your API key from the dashboard
4. **No Credit Card**: Required for verification

### **2. Set Environment Variable**

#### **Option A: Create .env file**

Create a `.env` file in your project root:

```bash
GROQ_API_KEY=your_groq_api_key_here
```

#### **Option B: Set in PowerShell**

```powershell
$env:GROQ_API_KEY="your_groq_api_key_here"
```

#### **Option C: Set in Windows Environment**

1. Open System Properties → Environment Variables
2. Add new variable: `GROQ_API_KEY`
3. Set value to your API key

### **3. Restart Backend**

After setting the API key, restart your backend server:

```powershell
# Stop current server (Ctrl+C)
# Then restart:
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## **🎯 TESTING THE SETUP**

### **1. Test API Key**

The backend will automatically test the API key when you first use insights.

### **2. Generate Insights**

1. Upload a CSV file
2. Go to Insights page
3. Select "Groq" as AI provider
4. Generate insights

### **3. Expected Results**

- ✅ Fast response times (< 5 seconds)
- ✅ High-quality insights
- ✅ No errors

---

## **🔧 TROUBLESHOOTING**

### **Common Issues:**

#### **"API Key Not Found"**

- Check if `.env` file exists
- Verify API key is correct
- Restart backend server

#### **"Rate Limit Exceeded"**

- Groq allows 1000 requests/day
- Wait for next day or upgrade

#### **"Network Error"**

- Check internet connection
- Verify Groq service status

---

## **📊 GROQ VS OTHER PROVIDERS**

| Provider    | Cost      | Speed  | Quality    | Setup  |
| ----------- | --------- | ------ | ---------- | ------ |
| **Groq**    | FREE      | ⚡⚡⚡ | ⭐⭐⭐⭐   | Easy   |
| Anthropic   | FREE tier | ⚡⚡   | ⭐⭐⭐⭐⭐ | Easy   |
| OpenAI      | Paid      | ⚡⚡   | ⭐⭐⭐⭐⭐ | Easy   |
| HuggingFace | FREE      | ⚡     | ⭐⭐⭐     | Medium |

---

## **🎉 READY TO USE!**

Once you've set up your Groq API key:

1. ✅ **Backend**: Will automatically use Groq
2. ✅ **Frontend**: Groq is pre-selected as default
3. ✅ **Insights**: Will work immediately
4. ✅ **Performance**: Fast and reliable

**No more OpenAI errors!** 🚀
