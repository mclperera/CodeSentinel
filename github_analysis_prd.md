# GitHub Code Analysis and Risk Assessment Workflow - PRD

## Executive Summary

This document outlines the requirements for developing an automated workflow that analyzes GitHub repositories to identify code purpose, assess vulnerabilities, and generate risk scores. The system will integrate GitHub APIs, AWS Bedrock Sonnet LLM, and CodeQL vulnerability data to produce comprehensive risk assessments.

## Objectives

### Primary Goals
- Automate repository analysis and code understanding
- Generate intelligent risk assessments based on code purpose and known vulnerabilities
- Provide actionable insights for security teams and developers
- Create scalable workflow for multiple repository analysis

### Success Metrics
- Accurate file purpose identification (>85% accuracy as validated by human reviewers)
- Complete vulnerability coverage from CodeQL integration
- Risk scoring correlation with actual security incidents
- Processing time under 10 minutes for repositories up to 1000 files

## User Stories

### As a Security Engineer
- I want to automatically analyze new repositories to understand their security risk profile
- I want to prioritize vulnerability remediation based on code criticality and exposure
- I want to generate compliance reports showing risk assessments across projects

### As a Development Team Lead
- I want to understand the purpose and structure of inherited codebases
- I want to identify high-risk components before deploying to production
- I want to track risk reduction over time as vulnerabilities are addressed

## Technical Requirements

### System Architecture

#### Phase 1: GitHub Integration & Manifest Generation
**Inputs:**
- GitHub repository URL or organization/repo identifier
- GitHub Personal Access Token with appropriate permissions
- Target branch (default: main/master)

**Process:**
1. **Repository Discovery**
   - Connect to GitHub REST/GraphQL API
   - Identify default branch using `/repos/{owner}/{repo}` endpoint
   - Retrieve latest commit SHA from default branch

2. **Code Extraction**
   - Use Git Trees API to traverse repository structure
   - Extract blob SHAs for all files
   - Download file contents using Git Blobs API
   - Filter files by extension (configurable whitelist)

3. **Initial Manifest Creation**
   ```json
   {
     "repository": {
       "url": "string",
       "default_branch": "string",
       "commit_sha": "string",
       "analysis_timestamp": "ISO8601"
     },
     "files": [
       {
         "path": "string",
         "blob_sha": "string",
         "size": "number",
         "extension": "string",
         "purpose": null,
         "confidence_score": null,
         "vulnerabilities": [],
         "risk_score": null
       }
     ]
   }
   ```

**Outputs:**
- Base manifest file in JSON format
- File inventory with metadata

#### Phase 2: LLM-Powered Code Analysis
**LLM Integration:**
- AWS Bedrock Sonnet model
- IAM role with Bedrock access permissions
- Local VS Code extension or standalone script

**Process:**
1. **File Analysis Pipeline**
   - Batch files by type and size for efficient processing
   - Send code content to Bedrock Sonnet with purpose identification prompt
   - Parse LLM responses for file purpose and confidence scores
   - Handle rate limiting and error retry logic

2. **Prompt Engineering**
   ```
   Analyze this code file and identify its primary purpose. Consider:
   - Main functionality and business logic
   - Security implications
   - Data handling patterns
   - External dependencies
   
   Respond with:
   - Purpose: [brief description]
   - Category: [authentication/data-processing/api/frontend/config/test/other]
   - Confidence: [0.0-1.0]
   - Security_relevance: [high/medium/low]
   ```

3. **Manifest Enrichment**
   - Update manifest with LLM analysis results
   - Add purpose categorization and confidence metrics
   - Flag high-security relevance files

**Outputs:**
- Enriched manifest with file purposes and classifications

#### Phase 3: Vulnerability Overlay
**CodeQL Integration:**
- GitHub CodeQL API access
- SARIF (Static Analysis Results Interchange Format) parsing
- Vulnerability database correlation

**Process:**
1. **Vulnerability Data Retrieval**
   - Query GitHub Code Scanning API: `GET /repos/{owner}/{repo}/code-scanning/alerts`
   - Retrieve SARIF results from CodeQL analysis
   - Parse vulnerability data including:
     - CWE classifications
     - CVSS scores
     - File locations and line numbers
     - Severity levels

2. **Manifest Integration**
   - Map vulnerabilities to corresponding files in manifest
   - Add vulnerability metadata:
     ```json
     "vulnerabilities": [
       {
         "id": "string",
         "rule_id": "string",
         "severity": "critical|high|medium|low",
         "cwe": "string",
         "cvss_score": "number",
         "description": "string",
         "location": {
           "start_line": "number",
           "end_line": "number"
         }
       }
     ]
     ```

**Outputs:**
- Vulnerability-enriched manifest

#### Phase 4: Risk Scoring Algorithm
**Scoring Methodology:**
- Weighted algorithm considering multiple factors
- Configurable weights for different risk components

**Risk Factors:**
1. **Vulnerability Severity (40% weight)**
   - Critical: 10 points
   - High: 7 points
   - Medium: 4 points
   - Low: 1 point

2. **File Purpose Criticality (30% weight)**
   - Authentication: 10 points
   - Data processing: 8 points
   - API endpoints: 7 points
   - Configuration: 6 points
   - Frontend: 3 points
   - Tests: 1 point

3. **Code Exposure (20% weight)**
   - Public-facing: 10 points
   - Internal API: 6 points
   - Internal logic: 3 points
   - Test/build: 1 point

4. **File Complexity (10% weight)**
   - Lines of code, dependencies, external connections

**Risk Score Calculation:**
```
file_risk_score = (
  (vulnerability_score * 0.4) +
  (purpose_criticality * 0.3) +
  (exposure_level * 0.2) +
  (complexity_score * 0.1)
)

repository_risk_score = weighted_average(all_file_scores)
```

**Outputs:**
- Final manifest with individual file risk scores
- Repository-level risk assessment
- Risk categorization (Critical/High/Medium/Low)

## Implementation Details

### Technology Stack
- **Programming Language:** Python 3.9+
- **GitHub API:** REST API v4 / GraphQL API v4
- **AWS SDK:** boto3 for Bedrock integration
- **Data Format:** JSON for manifests, SARIF for vulnerabilities
- **Development Environment:** VS Code with custom extension

### Key Dependencies
```python
# requirements.txt
requests>=2.28.0
boto3>=1.26.0
pygithub>=1.58.0
sarif-parser>=0.1.0
pydantic>=1.10.0
click>=8.0.0
python-dotenv>=0.19.0
```

### Configuration Management
```yaml
# config.yaml
github:
  token: "${GITHUB_TOKEN}"
  api_base_url: "https://api.github.com"
  
aws:
  region: "us-east-1"
  bedrock_model: "anthropic.sonnet-3-5"
  
analysis:
  file_extensions: [".py", ".js", ".java", ".go", ".rb", ".php"]
  max_file_size: 1048576  # 1MB
  batch_size: 10
  
risk_scoring:
  weights:
    vulnerability: 0.4
    purpose: 0.3
    exposure: 0.2
    complexity: 0.1
```

### Error Handling & Resilience
- Exponential backoff for API rate limiting
- Graceful degradation when LLM or CodeQL unavailable
- Comprehensive logging and monitoring
- Partial result recovery and resume capability

### Security Considerations
- Secure token storage and rotation
- IAM least-privilege access
- Code content handling and temporary storage cleanup
- Audit logging for compliance

## Deliverables

### Phase 1 Deliverables
- GitHub API integration module
- Repository discovery and branch detection
- Blob extraction and file inventory system
- Initial manifest generation

### Phase 2 Deliverables
- AWS Bedrock integration
- LLM prompt optimization
- File purpose analysis engine
- Manifest enrichment pipeline

### Phase 3 Deliverables
- CodeQL API integration
- SARIF parsing capabilities
- Vulnerability mapping system
- Enhanced manifest with security data

### Phase 4 Deliverables
- Risk scoring algorithm implementation
- Configurable weight system
- Final manifest with risk assessments
- Reporting and visualization components

### Additional Deliverables
- VS Code extension (optional)
- CLI tool for batch processing
- Documentation and usage guides
- Unit and integration tests (>80% coverage)

## Testing Strategy

### Unit Testing
- Individual component testing for each phase
- Mock GitHub and AWS API responses
- Risk scoring algorithm validation

### Integration Testing
- End-to-end workflow testing with sample repositories
- API integration verification
- Error condition handling

### Performance Testing
- Large repository processing (1000+ files)
- Concurrent analysis capabilities
- Memory and resource utilization

### Security Testing
- Token handling and storage
- Code content exposure minimization
- Access control validation

## Risk Assessment & Mitigation

### Technical Risks
- **API Rate Limiting:** Implement exponential backoff and request batching
- **LLM Response Quality:** Develop prompt validation and confidence scoring
- **Large Repository Handling:** Implement streaming and chunking strategies

### Business Risks
- **Cost Management:** Monitor AWS Bedrock usage and implement budgets
- **Compliance:** Ensure code analysis meets security and privacy requirements
- **Scalability:** Design for horizontal scaling and load distribution

## Success Criteria

### Functional Requirements
- ✅ Successfully identify default branch for 100% of valid repositories
- ✅ Extract and analyze all supported file types
- ✅ Generate accurate file purpose classifications (>85% accuracy)
- ✅ Integrate vulnerability data from CodeQL
- ✅ Produce consistent risk scores

### Non-Functional Requirements
- **Performance:** Process repositories under 10 minutes (up to 1000 files)
- **Reliability:** 99% uptime for batch processing
- **Scalability:** Handle concurrent analysis of multiple repositories
- **Maintainability:** Modular architecture with clear interfaces

## Timeline & Milestones

### Phase 1: GitHub Integration (Weeks 1-2)
- Week 1: API integration and authentication
- Week 2: Repository analysis and manifest generation

### Phase 2: LLM Integration (Weeks 3-4)
- Week 3: Bedrock integration and prompt development
- Week 4: File analysis pipeline and manifest enrichment

### Phase 3: Vulnerability Integration (Weeks 5-6)
- Week 5: CodeQL API integration and SARIF parsing
- Week 6: Vulnerability mapping and manifest enhancement

### Phase 4: Risk Scoring (Weeks 7-8)
- Week 7: Risk algorithm implementation
- Week 8: Testing, optimization, and documentation

## Conclusion

This workflow represents a comprehensive approach to automated code analysis and risk assessment. By combining GitHub's repository access, LLM-powered code understanding, and vulnerability intelligence, the system will provide valuable insights for security and development teams to make informed decisions about code risk management.