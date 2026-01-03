# Vercel Domain Setup - TODO

## 📋 Configuration Steps (To Be Completed Later)

### 1. Prerequisites
- [ ] Vercel account created and authenticated
- [ ] Domain purchased and DNS accessible
- [ ] Project deployed to Vercel

### 2. Domain Configuration
```bash
# Add domain to Vercel project
vercel domains add yourdomain.com

# Add www subdomain
vercel domains add www.yourdomain.com
```

### 3. DNS Records Required
| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | @ | 76.76.21.21 | 3600 |
| CNAME | www | cname.vercel-dns.com | 3600 |

### 4. SSL/TLS Configuration
- Vercel automatically provisions SSL certificates
- HTTPS enforced by default
- Certificate auto-renewal enabled

### 5. Environment Variables
Set in Vercel Dashboard or via CLI:
```bash
vercel env add DOMAIN_NAME production
vercel env add API_URL production
```

### 6. Custom Domain Script
Located at: [configure-custom-domain.ps1](configure-custom-domain.ps1)

### 7. Verification Steps
- [ ] Domain resolves to Vercel IP
- [ ] HTTPS certificate valid
- [ ] www redirect works
- [ ] API endpoints accessible

## 🔗 Related Files
- [CUSTOM-DOMAIN-SETUP.md](CUSTOM-DOMAIN-SETUP.md)
- [VERCEL-DOMAIN-SETUP-GUIDE.md](VERCEL-DOMAIN-SETUP-GUIDE.md)
- [configure-custom-domain.ps1](configure-custom-domain.ps1)
- [vercel.json](vercel.json)

## 📌 Notes
- Complete this configuration when ready to go live
- Ensure all security configurations are in place first
- Test on staging domain before production
