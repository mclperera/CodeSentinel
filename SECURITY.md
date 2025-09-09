# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of CodeSentinel seriously. If you discover a security vulnerability, please follow these steps:

### 🚨 For Security Issues
**DO NOT** create a public GitHub issue for security vulnerabilities.

Instead, please:
1. **Email**: Send details to [your-email@domain.com] with subject "CodeSentinel Security Vulnerability"
2. **Include**: 
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)

### 📋 What to Include
- **Vulnerability Type**: (e.g., API key exposure, injection, etc.)
- **Affected Components**: Which files/modules are affected
- **Attack Scenario**: How could this be exploited
- **Proof of Concept**: Minimal example demonstrating the issue
- **Environment**: OS, Python version, dependencies

### ⏱️ Response Timeline
- **Initial Response**: Within 48 hours
- **Status Update**: Weekly updates on progress
- **Resolution**: Target resolution within 30 days for critical issues

### 🛡️ Security Best Practices

When using CodeSentinel:

#### API Key Management
- **Never commit API keys** to version control
- **Use environment variables** (.env file) for credentials
- **Rotate keys regularly** especially if exposed
- **Use minimum required permissions** for GitHub tokens

#### Cost Protection
- **Review cost estimates** before large repository analysis
- **Set usage limits** with cloud providers
- **Monitor API usage** to prevent unexpected charges

#### Repository Access
- **Use read-only tokens** when possible
- **Audit repository access** permissions
- **Be cautious with private repositories** containing sensitive data

### 🔍 Known Security Considerations

#### API Key Exposure
- CodeSentinel requires API keys for GitHub, OpenAI, and AWS
- Keys are read from environment variables, not stored
- Ensure `.env` files are in `.gitignore`

#### Code Content Processing
- Repository content is sent to LLM providers for analysis
- **Do not analyze repositories with sensitive/proprietary code**
- Consider using private LLM deployments for sensitive analysis

#### Vulnerability Scanning
- Uses external tools (Semgrep, Bandit) for security analysis
- Tools are downloaded and executed locally
- Review tool configurations before enterprise use

### 🚫 Out of Scope

The following are **not** considered security vulnerabilities:
- Cost implications of API usage (covered by cost estimation)
- Rate limiting by external APIs
- Issues with external dependencies (report to respective projects)
- Feature requests or enhancement suggestions

### 🏆 Recognition

We appreciate security researchers who help improve CodeSentinel's security. With your permission, we will:
- Credit you in our security acknowledgments
- Mention the fix in release notes (without sensitive details)
- Consider feature requests for additional security enhancements

### 📞 Contact

For non-security issues, please use the regular GitHub issue tracker.

For security-related questions or concerns:
- **Email**: [security@codesentinel.dev] (update with actual email)
- **Response Time**: 2-3 business days

Thank you for helping keep CodeSentinel secure! 🔒
