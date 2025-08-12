# Apollo AI - Demo Guide

## 🚀 Quick Start

### 1. Start Backend Server

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Start Frontend Server

```bash
cd apollo-frontend
npm start
```

## 🌐 Access Points

- **Frontend Application**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

## 🎯 Demo Flow

### 1. Landing Page

- Visit http://localhost:3000
- Beautiful landing page with feature overview
- Click "Get Started" to begin

### 2. File Upload

- Upload a CSV file (sample data provided)
- Supported formats: CSV, Excel (.xls, .xlsx)
- File size limit: 10MB

### 3. Data Analysis

- Automatic comprehensive analysis
- Statistical insights
- Data quality assessment
- Correlation analysis

### 4. Visualizations

- Generate charts automatically
- Multiple chart types available
- Interactive visualizations

### 5. AI Insights

- AI-powered data insights
- Business recommendations
- Trend analysis

## 📊 Sample Data

You can use any CSV file with:

- Multiple columns (numeric and categorical)
- At least 10-20 rows for meaningful analysis
- Common business data (sales, customer data, etc.)

## 🔧 Troubleshooting

### If Backend Won't Start

```bash
pip install -r requirements.txt
```

### If Frontend Won't Start

```bash
cd apollo-frontend
npm install
npm start
```

### If Ports Are Busy

- Backend: Change port in uvicorn command
- Frontend: React will automatically suggest alternative port

## 🎨 Features to Highlight

1. **Modern UI/UX**: Glassmorphism design with smooth animations
2. **Real-time Analysis**: Fast processing with progress indicators
3. **AI Integration**: Multiple AI providers (Groq, OpenAI, Anthropic)
4. **Responsive Design**: Works on desktop and mobile
5. **Error Handling**: Graceful error messages and recovery
6. **Data Visualization**: Interactive charts with Chart.js
7. **Workflow Management**: Step-by-step guided process

## 📝 Notes for Supervisor

- **Authentication**: Currently using demo mode for simplicity
- **Database**: SQLite for demo (can be upgraded to PostgreSQL)
- **AI Providers**: Configured for free tiers where possible
- **Performance**: Optimized for demo scenarios
- **Security**: Basic security measures in place

## 🚨 Demo Tips

1. **Have a CSV file ready** - Any business data works
2. **Show the landing page first** - Impressive design
3. **Walk through the workflow** - Upload → Analysis → Visualization → Insights
4. **Highlight the AI features** - This is the key differentiator
5. **Show the API docs** - Professional backend documentation
6. **Demonstrate responsiveness** - Resize browser window

## 🎉 Success Metrics

- ✅ Modern, professional UI
- ✅ Fast data processing
- ✅ AI-powered insights
- ✅ Interactive visualizations
- ✅ Robust error handling
- ✅ Scalable architecture
- ✅ Production-ready code quality
