# Deployment Guide: Streamlit Cloud Secrets

This guide explains how to securely add your OpenAI API key when deploying to Streamlit Cloud.

## Quick Steps

### 1. Deploy Your App
1. Visit [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **"New app"**
4. Select repository: `rahbarnisa/CapstoneProject2`
5. Main file: `streamlit_app.py`
6. Click **"Deploy"**

### 2. Add Secrets via UI
1. Once deployed, click **⋮** (three dots) → **Settings**
2. Go to **"Secrets"** tab
3. Paste your secrets in TOML format:

```toml
OPENAI_API_KEY = "sk-your-actual-openai-api-key-here"
```

4. Click **"Save"** — app will auto-redeploy

### 3. Verify It Works
- Your app should reload automatically
- Try uploading an audio file
- If you see errors about missing API key, double-check the secret name matches exactly: `OPENAI_API_KEY`

## Visual Guide

After deployment, the Secrets interface looks like this:

```
┌─────────────────────────────────────┐
│ Secrets                             │
├─────────────────────────────────────┤
│                                     │
│ OPENAI_API_KEY = "sk-..."          │
│                                     │
│ [Save]                              │
└─────────────────────────────────────┘
```

## Security Best Practices

✅ **DO:**
- Use Streamlit Secrets for production deployments
- Keep your `.env` file local only
- Use different API keys for dev/prod if possible
- Rotate keys if accidentally exposed

❌ **DON'T:**
- Commit `.env` files or API keys to GitHub
- Share secrets publicly
- Hardcode API keys in your code
- Use the same key for multiple projects (if compromised)

## Local Development vs Deployment

### Local Development
Create a `.env` file in your project root:
```bash
OPENAI_API_KEY=sk-your-key-here
```

### Streamlit Cloud Deployment
Add secrets via the UI (see steps above). The code automatically checks:
1. Streamlit secrets (production)
2. `.env` file (local development)
3. Environment variables (fallback)

## Troubleshooting

**"OPENAI_API_KEY is missing" error:**
- Verify secret name is exactly `OPENAI_API_KEY` (case-sensitive)
- Check for extra spaces in the TOML file
- Make sure you clicked "Save" after adding the secret

**Secret not updating:**
- Wait 30-60 seconds for redeployment
- Refresh your app page
- Check the Streamlit Cloud logs for errors

**Need to update a secret:**
- Go to Settings → Secrets
- Edit the value
- Click "Save"
- App will redeploy automatically

## Alternative: Environment Variables

If you prefer environment variables (advanced), you can also use Streamlit Cloud's environment variables feature, but secrets are recommended for API keys as they're encrypted.

