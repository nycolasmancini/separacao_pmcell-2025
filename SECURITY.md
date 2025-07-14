# 🔒 Security Policy

## 📧 Reporting Security Vulnerabilities

We take the security of PMCELL seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### ⚠️ Please do NOT report security vulnerabilities through public GitHub issues.

Instead, please report them via email to: [your-security-email@company.com]

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

## 🛡️ Security Measures

### Authentication & Authorization
- PIN-based authentication with bcrypt hashing
- JWT tokens with configurable expiration
- Role-based access control (Separador, Vendedor, Comprador, Admin)
- Admin-level authentication for management functions

### Data Protection
- All passwords are hashed using bcrypt
- JWT tokens are signed with strong secret keys
- Sensitive data is not logged
- Environment variables for all secrets

### Network Security
- HTTPS enforcement in production
- CORS configuration for cross-origin requests
- Security headers (HSTS, CSP, X-Frame-Options, etc.)
- Rate limiting to prevent abuse

### Input Validation
- Pydantic schemas for all API inputs
- SQL injection prevention via SQLAlchemy ORM
- File upload validation for PDFs
- XSS protection through input sanitization

### Infrastructure Security
- Non-root containers for all services
- Multi-stage Docker builds
- Health checks and monitoring
- Regular dependency updates

## 🔍 Security Scanning

This project includes automated security scanning:

- **Dependency Scanning**: Automated checks for known vulnerabilities in dependencies
- **Secret Detection**: Scans for accidentally committed secrets
- **Container Scanning**: Docker image vulnerability scanning
- **Static Code Analysis**: CodeQL analysis for security issues

## 🚨 Security Requirements

### For Development
- Never commit secrets to version control
- Use strong passwords for all accounts
- Keep dependencies updated
- Enable 2FA on GitHub accounts

### For Production
- Use HTTPS for all communications
- Configure strong JWT secret keys (32+ characters)
- Enable database encryption at rest
- Set up monitoring and alerting
- Regular security updates

## 📋 Security Checklist

### Before Deployment
- [ ] Strong JWT secret key configured
- [ ] Database credentials secured
- [ ] HTTPS configured
- [ ] Security headers enabled
- [ ] Rate limiting configured
- [ ] Backup strategy implemented
- [ ] Monitoring configured

### Regular Maintenance
- [ ] Update dependencies monthly
- [ ] Review access logs weekly
- [ ] Rotate secrets quarterly
- [ ] Security audit annually
- [ ] Backup testing quarterly

## ⚡ Incident Response

### In Case of Security Incident

1. **Immediate Actions**
   - Isolate affected systems
   - Preserve evidence
   - Document the incident

2. **Assessment**
   - Determine scope of impact
   - Identify affected data
   - Assess risk level

3. **Response**
   - Implement containment measures
   - Notify relevant parties
   - Begin recovery process

4. **Recovery**
   - Restore systems from clean backups
   - Apply security patches
   - Monitor for further issues

5. **Post-Incident**
   - Conduct lessons learned session
   - Update security measures
   - Document improvements

## 🔧 Security Configuration

### Environment Variables

Ensure these security-related environment variables are properly configured:

```bash
# Strong JWT secret (32+ characters with special characters)
SECRET_KEY=your-super-secure-jwt-secret-key-here

# Strong admin password
ADMIN_PASSWORD=your-strong-admin-password

# Production CORS origins (no localhost)
ALLOWED_ORIGINS=https://your-production-domain.com

# Database with strong credentials
DATABASE_URL=postgresql://user:strong-password@host:5432/db
```

### Security Headers

The application automatically sets these security headers:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Content-Security-Policy: default-src 'self'; ...`

### Rate Limiting

Production deployments include rate limiting:
- 100 requests per hour per IP address
- Configurable limits based on endpoint
- Automatic IP blocking for repeated violations

## 📊 Security Monitoring

### What We Monitor
- Failed authentication attempts
- Unusual access patterns
- SQL injection attempts
- XSS attempts
- Rate limit violations
- File upload anomalies

### Alerts
- Multiple failed login attempts
- Admin panel access
- Database connection failures
- Unusual error rates
- Security header violations

## 🔄 Security Updates

### Dependency Updates
- Automated weekly dependency checks
- Monthly security updates
- Critical patches applied immediately
- Full regression testing after updates

### Security Patches
- Monitor security advisories for all components
- Test patches in staging environment
- Deploy critical patches within 24 hours
- Schedule regular patches during maintenance windows

## 🛠️ Security Tools

### Integrated Tools
- **CodeQL**: Static analysis for security vulnerabilities
- **Trivy**: Container and dependency vulnerability scanning
- **GitLeaks**: Secret detection in code
- **Safety**: Python dependency vulnerability checking

### Recommended External Tools
- **Sentry**: Real-time error tracking and monitoring
- **Cloudflare**: DDoS protection and WAF
- **Let's Encrypt**: Free SSL certificates
- **1Password/Bitwarden**: Secret management

## 🎓 Security Training

### For Developers
- OWASP Top 10 awareness
- Secure coding practices
- Git security best practices
- Password management

### For Operations
- Infrastructure security
- Incident response procedures
- Backup and recovery
- Monitoring and alerting

## 📚 Security Resources

### References
- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)
- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)
- [PostgreSQL Security Guide](https://www.postgresql.org/docs/current/security.html)

### Standards
- ISO 27001 Information Security Management
- NIST Cybersecurity Framework
- SOC 2 Type II compliance considerations

## 📞 Contact

For security-related questions or concerns:
- Security Team: [security@your-company.com]
- Emergency Contact: [emergency@your-company.com]
- General Support: [support@your-company.com]

---

## 📅 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-07-14 | Initial security policy |

This security policy is reviewed and updated quarterly or after significant security incidents.