# Website Deployment Guide

This repository includes a streamlined GitHub workflow for deploying the website to GitHub Pages. The deployment system provides efficient website deployment with automatic triggering from test coverage runs.

## 🚀 Deployment Workflow

### Website Deployment (`deploy-website.yml`)

**Purpose**: Deploy website with existing content to GitHub Pages

**Triggers**:
- ✅ Manual: Via GitHub Actions UI
- ✅ Automatic: Called by test-coverage workflow after successful completion

**Features**:
- ⚡ Fast deployment using existing content
- 📁 Deploys test coverage reports, PlantUML diagrams, and project files
- 🎨 Modern, responsive website design
- 📤 Deploys to GitHub Pages
- 📋 Provides detailed deployment summary

**Manual Trigger Options**:
- `message`: Custom deployment message (default: "Website deployment")

## 🎯 How to Use

### Automatic Deployment

The website deployment workflow is automatically triggered after successful test coverage runs:

1. **Run Test Coverage**: The test-coverage workflow runs (manually or on PR merge)
2. **Auto-Deploy**: After successful completion, the deploy-website workflow is automatically called
3. **Website Updated**: Your website is deployed with the latest test reports and content

### Manual Deployment

1. **Go to GitHub Actions**: Navigate to your repository's "Actions" tab
2. **Select Workflow**: Choose "Deploy Website"
3. **Click "Run workflow"**: Use the dropdown button
4. **Add Message** (optional): Custom deployment message
5. **Click "Run workflow"**: Start the deployment

### Workflow Integration

The deployment workflow is integrated with the test coverage workflow:
- **Test Coverage Runs**: Generates reports and commits them to the repository
- **Auto-Deploy**: Automatically triggers website deployment after successful test coverage
- **Website Updated**: Fresh content is deployed to GitHub Pages

## 📁 What Gets Deployed

The deployment workflow includes:
- 📖 README.md as main page
- 📊 Test coverage reports (from tests/reports/)
- 📝 Test execution summaries
- 📊 PlantUML diagrams and PNG images (from output/)
- 📋 Project examples (from example/)
- 🎨 Modern HTML website with navigation
- 📚 Project documentation and specification

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

## 🔄 Workflow Integration

The deployment workflow is designed to work seamlessly with the test coverage workflow:

| Workflow | Purpose | Trigger | Result |
|----------|---------|---------|--------|
| **Test Coverage** | Generate reports and diagrams | Manual, PR merge | Fresh content in repository |
| **Deploy Website** | Deploy to GitHub Pages | Manual, Auto (after test coverage) | Website updated with latest content |

### Benefits:
- ✅ **Automated**: Website deploys automatically after test coverage runs
- ✅ **Efficient**: Uses existing content, no regeneration needed
- ✅ **Reliable**: Only deploys after successful test coverage completion
- ✅ **Flexible**: Can also be triggered manually when needed

## 📞 Support

If you encounter issues:
1. Check the Actions tab for detailed logs
2. Review this deployment guide
3. Check GitHub Pages documentation
4. Verify repository settings and permissions

---

*Last updated: $(date)*
*Generated by GitHub Actions deployment workflow*