# Website Deployment Guide

This repository includes comprehensive GitHub workflows for deploying the website to GitHub Pages. The deployment system provides both full and quick deployment options.

## 🚀 Available Deployment Workflows

### 1. Full Website Deployment (`deploy-website.yml`)

**Purpose**: Complete website deployment with fresh content generation

**Triggers**:
- ✅ Automatic: On push to `main` or `master` branch
- ✅ Manual: Via GitHub Actions UI with options
- ✅ Scheduled: Daily at 2 AM UTC

**Features**:
- 🧪 Generates fresh test coverage reports
- 📊 Creates new PlantUML diagrams and PNG images
- 🏗️ Builds complete website from scratch
- 📤 Deploys to GitHub Pages
- 📋 Provides detailed deployment summary

**Manual Trigger Options**:
- `force_redeploy`: Force complete redeployment (default: true)
- `clean_deploy`: Clean previous deployment before redeploying (default: true)

### 2. Quick Website Redeploy (`quick-deploy.yml`)

**Purpose**: Fast redeployment using existing content

**Triggers**:
- ✅ Manual: Via GitHub Actions UI
- ✅ Scheduled: Daily at 6 AM UTC

**Features**:
- ⚡ Fast deployment (no content regeneration)
- 📁 Uses existing reports and diagrams
- 🎨 Modern, responsive website design
- 📤 Deploys to GitHub Pages
- 📋 Quick deployment summary

**Manual Trigger Options**:
- `message`: Custom deployment message (default: "Quick website redeploy")

## 🎯 How to Use

### Automatic Deployment

The full deployment workflow runs automatically when you push to the main branch:

```bash
git add .
git commit -m "Update website content"
git push origin main
```

### Manual Deployment

1. **Go to GitHub Actions**: Navigate to your repository's "Actions" tab
2. **Select Workflow**: Choose either "Deploy Website to GitHub Pages" or "Quick Website Redeploy"
3. **Click "Run workflow"**: Use the dropdown button
4. **Configure Options** (if available):
   - For full deployment: Set force_redeploy and clean_deploy options
   - For quick deploy: Add a custom message
5. **Click "Run workflow"**: Start the deployment

### Scheduled Deployment

Both workflows include scheduled deployments:
- **Full deployment**: Daily at 2 AM UTC
- **Quick deployment**: Daily at 6 AM UTC

## 📁 What Gets Deployed

### Full Deployment Includes:
- 📖 README.md as main page
- 📊 Fresh test coverage reports
- 📝 Updated test summaries
- 📊 New PlantUML diagrams and PNG images
- 📋 Project examples
- 🎨 Modern HTML website with navigation

### Quick Deployment Includes:
- 📖 README.md as main page
- 📊 Existing test coverage reports
- 📝 Existing test summaries
- 📊 Existing PlantUML diagrams and PNG images
- 📋 Project examples
- 🎨 Modern HTML website with navigation

## 🌐 Website Structure

After deployment, your website will be available at:
```
https://[username].github.io/[repository-name]/
```

### Main Pages:
- 🏠 **Home**: `index.html` - Main project page
- 📊 **Coverage**: `tests/reports/coverage/index.html` - Test coverage reports
- 📝 **Tests**: `tests/reports/test_summary.html` - Test execution summary
- 📊 **Diagrams**: `output/` - PlantUML diagrams and PNG images
- 📋 **Examples**: `example/` - Project examples

## ⚙️ Configuration

### Required Secrets

For optimal functionality, add these repository secrets:

1. **PERSONAL_ACCESS_TOKEN** (Optional but recommended):
   - Go to GitHub Settings → Developer settings → Personal access tokens
   - Create a token with `repo` scope
   - Add as repository secret named `PERSONAL_ACCESS_TOKEN`

### GitHub Pages Settings

Ensure GitHub Pages is enabled:
1. Go to repository Settings → Pages
2. Source: "GitHub Actions"
3. Branch: Not applicable (uses Actions)

## 🔧 Troubleshooting

### Common Issues

1. **Deployment Fails**:
   - Check Actions tab for error details
   - Ensure GitHub Pages is enabled
   - Verify repository permissions

2. **Content Not Updated**:
   - Wait 5-10 minutes for GitHub Pages to update
   - Check if the workflow completed successfully
   - Verify the correct branch is being deployed

3. **Authentication Issues**:
   - Add PERSONAL_ACCESS_TOKEN secret
   - Check repository permissions
   - Verify workflow permissions

### Debug Information

Both workflows provide detailed summaries in the Actions tab:
- ✅ Deployment status
- 📊 File counts and types
- 🔗 Direct links to deployed content
- ⏰ Deployment timestamps

## 📈 Monitoring

### Check Deployment Status:
1. Go to Actions tab
2. Look for recent workflow runs
3. Click on a run to see detailed logs
4. Check the "Deployment Summary" step for links

### Website Availability:
- Full deployment: 5-10 minutes after completion
- Quick deployment: 2-5 minutes after completion
- GitHub Pages may take additional time to propagate

## 🔄 Workflow Comparison

| Feature | Full Deployment | Quick Deployment |
|---------|----------------|------------------|
| **Speed** | ⏱️ Slower (regenerates content) | ⚡ Fast (uses existing) |
| **Content** | 🆕 Fresh reports & diagrams | 📁 Existing content |
| **Triggers** | Push, Manual, Scheduled | Manual, Scheduled |
| **Use Case** | Major updates, fresh content | Quick fixes, content refresh |

## 📞 Support

If you encounter issues:
1. Check the Actions tab for detailed logs
2. Review this deployment guide
3. Check GitHub Pages documentation
4. Verify repository settings and permissions

---

*Last updated: $(date)*
*Generated by GitHub Actions deployment workflow*