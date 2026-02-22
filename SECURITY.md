# Security Policy for Datana

## 🔐 Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| v1.1.0.9   | ✅ Fully Supported |
| ------- | ------------------ |

---

## 🛡️ Reporting a Vulnerability

We take security seriously at Datana. If you discover a security vulnerability, please follow these steps:

### 📧 Contact Method
**DO NOT** create a public GitHub issue for security vulnerabilities.

Instead, contact us directly at:
- **Email:** ashkanmirgomari@gmail.com
- **GitHub Security Advisory:** [Create a private report](https://github.com/ashkanmirgomari/datana/security/advisories/new)

### 📋 What to Include
When reporting a vulnerability, please include:

1. **Description** - What is the vulnerability?
2. **Impact** - What can an attacker do?
3. **Steps to Reproduce** - How can we verify it?
4. **Affected Versions** - Which versions are affected?
5. **Proposed Fix** (optional) - Do you have a solution?
6. **Your Contact** - How to reach you for questions

### ⏱️ Response Timeline
- **24 hours**: Initial acknowledgment
- **3 days**: Verification and risk assessment
- **7 days**: Patch development (if accepted)
- **14 days**: Public disclosure (if appropriate)

---

## 🔒 Security Features in Datana

### 1. **Encryption**
- **AES-256** for all stored data (records, users)
- **Fernet** symmetric encryption
- Unique encryption key per installation
- Encrypted backup files

### 2. **Authentication**
- **bcrypt** password hashing with salt
- Session management with timeout (15 minutes)
- Role-based access control (RBAC)
- Account lockout after 3 failed attempts

### 3. **Data Validation**
- Iranian National ID validation (algorithm check)
- Iranian phone number validation (+98 format)
- Input sanitization for all fields
- SQL injection prevention (no raw SQL)

### 4. **Logging & Monitoring**
- All security events are logged
- Log integrity checking with HMAC
- Failed login attempts tracking
- Security alerts for suspicious activities

### 5. **Web Panel Security**
- CSRF protection
- Session security (HttpOnly, Secure flags)
- Password visibility toggle
- 2FA ready (coming soon)

---

## 🚨 Known Security Considerations

### Default Credentials
**⚠️ IMPORTANT:** Datana comes with default credentials:
- Username: `root`
- Password: `root`

**You MUST change these immediately after first login!**

### Data Directory
The `data/` directory contains encrypted files:
- `records.enc` - Your encrypted records
- `users.enc` - Encrypted user data
- `logs.txt` - System logs

**Ensure this directory has proper permissions:**
```bash
chmod 700 data/
chmod 600 data/*.enc
