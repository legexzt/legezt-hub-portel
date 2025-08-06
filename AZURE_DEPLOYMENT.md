# Azure Deployment Guide for Legezt Portal

This guide will help you deploy your Legezt Portal Flask application to Azure App Service.

## 🚀 Quick Deployment Steps

### 1. Prerequisites
- Azure subscription
- GitHub account with your repository: [https://github.com/legexzt/legezt-hub-portel.git](https://github.com/legexzt/legezt-hub-portel.git)

### 2. Create Azure App Service

#### Option A: Azure Portal (Recommended)
1. Go to [Azure Portal](https://portal.azure.com)
2. Click "Create a resource"
3. Search for "Web App"
4. Click "Create"
5. Fill in the details:
   - **Resource Group**: Create new or use existing
   - **Name**: `legezt-portal`
   - **Publish**: Code
   - **Runtime stack**: Python 3.11
   - **Operating System**: Linux
   - **Region**: Choose nearest to you
   - **App Service Plan**: Create new (B1 Basic for testing)
6. Click "Review + create" then "Create"

#### Option B: Azure CLI
```bash
# Login to Azure
az login

# Create resource group
az group create --name legezt-portal-rg --location eastus

# Create App Service plan
az appservice plan create --name legezt-portal-plan --resource-group legezt-portal-rg --sku B1 --is-linux

# Create web app
az webapp create --resource-group legezt-portal-rg --plan legezt-portal-plan --name legezt-portal --runtime "PYTHON|3.11"
```

### 3. Configure Environment Variables

In Azure Portal:
1. Go to your App Service
2. Navigate to "Settings" → "Configuration"
3. Add the following Application Settings:

```env
# Flask Configuration
SECRET_KEY=your-super-secret-key-here
FLASK_ENV=production
FLASK_DEBUG=False

# Database Configuration
DB_HOST=localhost
DB_USER=iamlegezt
DB_PASSWORD=mehonjibraan_09
DB_NAME=legezt_portal

# Email Configuration (SMTP - Namecheap Private Email)
MAIL_SERVER=smtp.privateemail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=mohdjibraan@legezthub.me
MAIL_PASSWORD=iamlegezt09

# Google Drive API Configuration
GOOGLE_DRIVE_CLIENT_ID=your-google-client-id
GOOGLE_DRIVE_CLIENT_SECRET=your-google-client-secret
GOOGLE_DRIVE_REDIRECT_URI=https://your-app-name.azurewebsites.net/oauth2callback
GOOGLE_DRIVE_API_KEY=your-google-api-key

# Admin Email
ADMIN_EMAIL=mdjibjibran@gmail.com

# JWT Secret
JWT_SECRET=your-jwt-secret-key

# Azure SQL Database (if using)
DB_SERVER=legexzt-server.database.windows.net
DB_NAME=legezt-app
DB_PORT=1433
```

### 4. Deploy from GitHub

#### Option A: GitHub Actions (Automatic)
1. In Azure Portal, go to "Deployment Center"
2. Choose "GitHub" as source
3. Connect your GitHub account
4. Select repository: `legexzt/legezt-hub-portel`
5. Select branch: `master`
6. Click "Save"

#### Option B: Manual Deployment
```bash
# Clone your repository
git clone https://github.com/legexzt/legezt-hub-portel.git
cd legezt-hub-portel

# Deploy using Azure CLI
az webapp deployment source config-local-git --resource-group legezt-portal-rg --name legezt-portal
git remote add azure <deployment-url>
git push azure master
```

### 5. Configure Custom Domain (Optional)

1. Go to "Custom domains" in your App Service
2. Add your domain
3. Update DNS records as instructed
4. Configure SSL certificate

## 🔧 Configuration Files

The repository includes these Azure-specific files:

- **`web.config`**: IIS configuration for Python
- **`runtime.txt`**: Python version specification
- **`startup.txt`**: Startup command
- **`.github/workflows/azure-deploy.yml`**: GitHub Actions workflow

## 📊 Monitoring and Logs

### View Application Logs
```bash
# Using Azure CLI
az webapp log tail --name legezt-portal --resource-group legezt-portal-rg

# Or in Azure Portal
# Go to App Service → Monitoring → Log stream
```

### Application Insights
1. Enable Application Insights in your App Service
2. Monitor performance, errors, and usage

## 🔒 Security Best Practices

1. **Environment Variables**: Never commit secrets to Git
2. **HTTPS**: Always use HTTPS in production
3. **Firewall**: Configure Azure SQL Database firewall rules
4. **Authentication**: Use Azure AD if needed
5. **Backup**: Set up regular backups

## 🚨 Troubleshooting

### Common Issues

1. **Module not found errors**
   - Check `requirements.txt` is complete
   - Verify Python version in `runtime.txt`

2. **Database connection issues**
   - Verify Azure SQL Database firewall rules
   - Check connection string in environment variables

3. **Static files not loading**
   - Check `web.config` rewrite rules
   - Verify file paths

4. **Email not working**
   - Verify SMTP settings
   - Check firewall rules for SMTP

### Debug Commands
```bash
# Check app status
az webapp show --name legezt-portal --resource-group legezt-portal-rg

# Restart app
az webapp restart --name legezt-portal --resource-group legezt-portal-rg

# View logs
az webapp log download --name legezt-portal --resource-group legezt-portal-rg
```

## 📈 Scaling

### Vertical Scaling (App Service Plan)
- **Basic (B1)**: Good for development
- **Standard (S1)**: Recommended for production
- **Premium (P1)**: For high traffic

### Horizontal Scaling
- Enable auto-scaling in App Service Plan
- Set minimum and maximum instances

## 💰 Cost Optimization

1. **Use Basic plan for development**
2. **Stop app when not in use**
3. **Monitor usage with Azure Cost Management**
4. **Use reserved instances for production**

## 🔄 Continuous Deployment

The repository includes GitHub Actions workflow that automatically deploys on push to master branch.

To enable:
1. Add `AZURE_WEBAPP_PUBLISH_PROFILE` secret to GitHub repository
2. Push to master branch
3. Monitor deployment in GitHub Actions tab

## 📞 Support

For issues:
- Check Azure App Service logs
- Review GitHub Actions deployment logs
- Contact: mdjibjibran@gmail.com

---

**Your app will be available at**: `https://legezt-portal.azurewebsites.net`

**GitHub Repository**: [https://github.com/legexzt/legezt-hub-portel.git](https://github.com/legexzt/legezt-hub-portel.git) 