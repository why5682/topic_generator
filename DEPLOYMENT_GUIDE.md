# 🚀 Streamlit Cloud Deployment Guide

## 📋 Pre-Deployment Checklist

### 1. **Replace Files for Cloud Deployment**

Before deploying to Streamlit Cloud, you need to use the cloud-ready versions:

```bash
# In your trend folder:
# 1. Backup original files (optional)
cp app.py app_local.py
cp pubmed_client.py pubmed_client_local.py
cp requirements.txt requirements_local.txt

# 2. Replace with cloud versions
cp app_cloud.py app.py
cp pubmed_client_cloud.py pubmed_client.py
cp requirements_cloud.txt requirements.txt
```

### 2. **Get NCBI API Credentials**

1. **Create NCBI Account**: [https://www.ncbi.nlm.nih.gov/account/](https://www.ncbi.nlm.nih.gov/account/)
2. **Generate API Key**:
   - Log in → Settings → API Key Management
   - Click "Create an API Key"
   - Copy the generated key

### 3. **Prepare Your GitHub Repository**

```bash
# Initialize git (if not already done)
git init

# Add files
git add app.py pubmed_client.py analyzer.py main.py requirements.txt
git add .streamlit/secrets.toml.example

# Commit
git commit -m "Prepare for Streamlit Cloud deployment"

# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

**⚠️ IMPORTANT**: Make sure `.env` and any actual `secrets.toml` are in `.gitignore`!

---

## 🌐 Deploy to Streamlit Cloud

### Step 1: Go to Streamlit Cloud
Visit: [https://share.streamlit.io/](https://share.streamlit.io/)

### Step 2: Deploy New App
1. Click **"New app"**
2. Select your **GitHub repository**
3. Choose **branch** (usually `main`)
4. Set **Main file path**: `app.py`
5. Click **"Deploy"**

### Step 3: Configure Secrets
1. In your app dashboard, click **"Settings"** (⚙️)
2. Go to **"Secrets"** tab
3. Paste your secrets in TOML format:

```toml
ENTREZ_EMAIL = "your_actual_email@example.com"
ENTREZ_API_KEY = "your_actual_ncbi_api_key"
OLLAMA_MODEL = "gptoss-120b:cloud"
OLLAMA_HOST = "https://your-ollama-endpoint.com"
```

4. Click **"Save"**

### Step 4: Verify Deployment
- Your app will automatically restart
- Check the sidebar: "✅ NCBI Credentials Configured" should appear
- Test with a sample query (e.g., "GLP-1 Agonists")

---

## 🔧 Troubleshooting

### Issue: "ENTREZ_EMAIL not configured"
**Solution**: Double-check secrets are correctly set in Streamlit Cloud dashboard.

### Issue: "Module not found"
**Solution**: Verify all dependencies are in `requirements.txt` with correct versions.

### Issue: SQLite database errors
**Solution**: The app creates `pubmed_cache.db` automatically in Streamlit Cloud's temporary storage. This is normal and expected.

### Issue: Ollama connection failed
**Solution**: 
- Ensure `OLLAMA_HOST` points to a publicly accessible endpoint
- Local `localhost:11434` won't work in the cloud
- You need a cloud-hosted Ollama instance or API

---

## 📊 Key Differences: Local vs Cloud

| Feature | Local (`app.py`) | Cloud (`app_cloud.py`) |
|---------|------------------|------------------------|
| **Secrets** | `.env` file | `st.secrets` |
| **Database** | Local SQLite | Temporary SQLite (resets) |
| **Ollama** | localhost:11434 | Cloud API endpoint |
| **Dependencies** | `python-dotenv` | No dotenv needed |

---

## 🎯 Next Steps

1. **Monitor Usage**: Check Streamlit Cloud analytics
2. **Share Link**: Get shareable URL from dashboard
3. **Custom Domain** (Optional): Configure in Settings
4. **Set Up CI/CD**: Auto-deploy on GitHub push

---

## 📝 Notes

- **Free Tier Limits**: Streamlit Cloud free tier has resource limits
- **Database Persistence**: SQLite cache resets on app restart (consider external DB for production)
- **API Rate Limits**: NCBI allows 10 requests/second with API key
- **Ollama Hosting**: Consider deploying Ollama to a cloud service (AWS, GCP, etc.)

---

## 🆘 Need Help?

- **Streamlit Docs**: [https://docs.streamlit.io/](https://docs.streamlit.io/)
- **Community Forum**: [https://discuss.streamlit.io/](https://discuss.streamlit.io/)
- **NCBI API Docs**: [https://www.ncbi.nlm.nih.gov/books/NBK25500/](https://www.ncbi.nlm.nih.gov/books/NBK25500/)
