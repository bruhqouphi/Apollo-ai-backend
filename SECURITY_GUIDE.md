# 🔐 Security Guide - API Key Management

## 🚨 **IMPORTANT: Never Commit API Keys to Git!**

### **What to do if your API keys were exposed:**

1. **IMMEDIATELY revoke/regenerate your API keys:**

   - **HuggingFace**: https://huggingface.co/settings/tokens
   - **OpenAI**: https://platform.openai.com/api-keys
   - **Anthropic**: https://console.anthropic.com/
   - **Groq**: https://console.groq.com/

2. **Remove API keys from Git history:**

   ```bash
   git filter-branch --force --index-filter \
   "git rm --cached --ignore-unmatch .env" \
   --prune-empty --tag-name-filter cat -- --all
   ```

3. **Force push to remove from remote:**
   ```bash
   git push origin --force --all
   ```

### **Proper API Key Setup:**

1. **Copy the template:**

   ```bash
   cp env_template.txt .env
   ```

2. **Edit .env with your real API keys:**

   ```bash
   # Never commit this file!
   OPENAI_API_KEY=sk-your-actual-key-here
   GROQ_API_KEY=gsk-your-actual-key-here
   ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
   HUGGINGFACE_API_KEY=hf-your-actual-key-here
   ```

3. **Verify .env is in .gitignore:**
   ```bash
   git status
   # .env should NOT appear in the output
   ```

### **Best Practices:**

- ✅ Use `.env` files for local development
- ✅ Use environment variables in production
- ✅ Never hardcode API keys in source code
- ✅ Use placeholder values in documentation
- ✅ Regularly rotate API keys
- ❌ Never commit `.env` files
- ❌ Never share API keys in chat/email
- ❌ Never use API keys in client-side code

### **Free API Key Options:**

- **Groq**: 1000 requests/day free, very fast
- **HuggingFace**: Free tier available
- **Anthropic**: Free tier available
- **OpenAI**: Paid but reliable

### **Testing Without API Keys:**

The backend will work without API keys for basic functionality. AI insights will use fallback methods when no API keys are provided.
