# Secrets & Environment Setup

> **NEVER commit credentials to the repository.** This file documents which secrets are needed and where to configure them.

---

## GitHub Actions Secrets

Add these in your GitHub repository:

**Settings → Secrets and variables → Actions → New repository secret**

### Required Secrets

| Secret Name          | Where to Get It                                  | Used By                              |
| -------------------- | ------------------------------------------------ | ------------------------------------ |
| `OPENROUTER_API_KEY` | [openrouter.ai/keys](https://openrouter.ai/keys) | CrewAI code review (AI model access) |

### Optional Secrets (Cloudflare Deployment)

| Secret Name             | Where to Get It                                                                     | Used By                               |
| ----------------------- | ----------------------------------------------------------------------------------- | ------------------------------------- |
| `CLOUDFLARE_API_TOKEN`  | [Cloudflare Dashboard → API Tokens](https://dash.cloudflare.com/profile/api-tokens) | Preview + production deploy workflows |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare Dashboard → Overview (right sidebar)                                     | Preview + production deploy workflows |

### Optional Secrets (Enhanced Memory)

| Secret Name    | Where to Get It                     | Used By                                  |
| -------------- | ----------------------------------- | ---------------------------------------- |
| `MEM0_API_KEY` | [app.mem0.ai](https://app.mem0.ai/) | Persistent AI review memory (mem0 Cloud) |

---

## How to Add a Secret

1. Go to your GitHub repository
2. Click **Settings** (top nav, far right)
3. In the left sidebar, expand **Secrets and variables**
4. Click **Actions**
5. Click **New repository secret**
6. Enter the **Name** exactly as shown in the table above
7. Paste the **Value** (your actual key/token)
8. Click **Add secret**

> Secrets are encrypted and only exposed to workflows at runtime. They are never visible in logs (GitHub masks them automatically).

---

## Local Development (.env)

For running CrewAI locally (outside GitHub Actions):

```bash
# Copy the template
cp .crewai/.env.example .crewai/.env

# Edit with your actual values
nano .crewai/.env
```

The `.env` file is gitignored — it will never be committed.

---

## What Each Secret Does

### `OPENROUTER_API_KEY`

Routes AI model requests through [OpenRouter](https://openrouter.ai/), which provides access to 100+ models from a single API key. The CrewAI review system uses this to run code analysis agents.

- **Free tier**: 20 requests/minute, access to free models (Gemini Flash, etc.)
- **Paid tier**: Higher rate limits, access to premium models (GPT-4o, Claude, etc.)
- **Cost**: The default configuration uses models that cost ~$0.01-0.05 per review

### `CLOUDFLARE_API_TOKEN`

Required only if you're deploying your website to Cloudflare Pages. Create a token with these permissions:

- **Cloudflare Pages**: Edit
- **Zone**: DNS Edit (if using custom preview domains)
- **Account**: Cloudflare Pages Read

### `CLOUDFLARE_ACCOUNT_ID`

Your Cloudflare account identifier. Found on the Overview page of any zone in your Cloudflare dashboard (right sidebar, "Account ID").

### `MEM0_API_KEY`

Optional. Enables [mem0 Cloud](https://mem0.ai/) for persistent semantic memory across CI runs. Without this, the system uses local JSON files in `.crewai/memory/` (which works great — mem0 is an upgrade, not a requirement).

---

## Security Checklist

- [ ] `.env` is in `.gitignore` (**required** — already configured in this template)
- [ ] No API keys, tokens, or passwords in any committed file
- [ ] GitHub secrets are set at the repository level, not organization level (unless intentional)
- [ ] Cloudflare API token uses minimum required permissions
- [ ] Team members each have their own OpenRouter keys (never share keys)
