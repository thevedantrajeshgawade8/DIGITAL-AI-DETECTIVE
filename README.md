🔎 DIGITAL DETECTIVE
AI-Powered Investigation of Suspicious Digital Information
Digital Detective is an AI-powered investigation tool that analyzes suspicious messages, job offers, scholarship announcements, and advertisements using multimodal AI, evidence retrieval, and source-backed analysis. It identifies suspicious indicators, verifies claims against authoritative sources, and explains its findings with traceable evidence.

💡 The Problem
Digital fraud has evolved beyond obvious spelling mistakes and poorly written messages. Scammers increasingly use convincing WhatsApp job offers, counterfeit scholarship portals, misleading advertisements, and phishing campaigns that imitate legitimate institutions.

For students, job seekers, and everyday internet users, distinguishing genuine opportunities from fraudulent ones often requires extensive manual research and technical knowledge.

Digital Detective aims to simplify this process by automating evidence-based investigation and making the reasoning behind its findings understandable to everyone.

🛡️ Our Solution
Digital Detective acts as a skeptical, evidence-driven fact-checker. Rather than relying solely on an AI model's internal knowledge, it retrieves relevant external evidence and compares suspicious claims against information published by authoritative sources.

The system prioritizes verified government portals, official educational institutions, and legitimate corporate websites. Claims about application fees, eligibility criteria, deadlines, recruiters, and contact details are assessed against the available evidence.

When sufficient evidence is unavailable, the system marks a claim as UNVERIFIED instead of inventing facts or presenting assumptions as certainty.

The goal is not merely to label suspicious content, but to explain what appears suspicious, why it matters, and which evidence supports the assessment.

⚙️ Core Capabilities
1. Multimodal Input Processing
Accepts pasted text, suspicious URLs, and uploaded screenshots or images.
Uses Optical Character Recognition (OCR) to extract text from messages, advertisements, and announcements.
Identifies relevant claims, organisation names, deadlines, fees, and contact information for investigation.
Accounts for OCR uncertainty when images are blurry, incomplete, or difficult to read.
2. Evidence-Based Retrieval
Integrates the Tavily Search API to retrieve relevant web evidence.
Prioritizes authoritative sources, including official government portals, educational institutions, and corporate websites.
Uses a configurable domain allowlist to restrict or prioritize eligible sources.
Collects source URLs, page titles, relevant text snippets, and other available metadata.
Flags claims that cannot be adequately verified using the retrieved evidence.
3. Explainable AI Verdicts
Digital Detective produces one of three primary verdicts:

VERIFIED: Available authoritative evidence sufficiently supports the claims assessed.
SCAM: Sufficient evidence indicates deception, impersonation, or fraudulent activity.
UNVERIFIED: Available evidence is insufficient, inaccessible, conflicting, or inconclusive.
Each report aims to include:

The verdict and its reasoning.
Suspicious indicators identified in the submitted content.
Relevant evidence snippets and direct source links.
A distinction between supported claims, contradicted claims, and unresolved claims.
A verdict applies only to the evidence actually assessed. Verification of one detail does not automatically establish the legitimacy of an entire message or offer.

4. Advanced Threat and Edge-Case Detection
Domain spoofing: Detects suspicious lookalike domains, such as myscheme.gov.in.com, which is not a subdomain of gov.in.
Expired announcements: Identifies outdated deadlines and distinguishes historical notices from current opportunities.
Impersonation: Compares organisation names, recruiter details, and contact information against available official records.
Manipulated screenshots: Investigates suspicious phone numbers, payment instructions, and other details that conflict with official announcements.
Insufficient evidence: Avoids declaring content legitimate or fraudulent solely because a search returns no matching results.
🏗️ System Architecture
Digital Detective follows an evidence-driven investigation pipeline.

┌──────────────────────────────────────┐
│             INPUT LAYER              │
│      Text · URL · Image Upload       │
└──────────────────┬───────────────────┘
                   ▼
┌──────────────────────────────────────┐
│       PARSING AND EXTRACTION         │
│   OCR · Text Processing · Claims     │
└──────────────────┬───────────────────┘
                   ▼
┌──────────────────────────────────────┐
│        EVIDENCE RETRIEVAL            │
│  Tavily Search API · Domain Rules    │
│   Official Sources · Source Metadata │
└──────────────────┬───────────────────┘
                   ▼
┌──────────────────────────────────────┐
│       CLAIM VALIDATION ENGINE        │
│  Evidence Comparison · URL Checks    │
│   Contradiction · Uncertainty Checks │
└──────────────────┬───────────────────┘
                   ▼
┌──────────────────────────────────────┐
│       VERDICT AND REPORT             │
│ VERIFIED · SCAM · UNVERIFIED         │
│  Reasoning · Evidence · Citations    │
└──────────────────┬───────────────────┘
                   ▼
┌──────────────────────────────────────┐
│       LOGGING AND EVALUATION         │
│   Test Results · Errors · Metrics    │
└──────────────────────────────────────┘
Investigation Workflow
Submit: The user provides a suspicious message, URL, advertisement, or image.
Extract: The system extracts text and identifies the claims that need verification.
Retrieve: Tavily searches for relevant evidence using configured source-selection rules.
Validate: The system compares extracted claims with the retrieved evidence and checks for contradictions.
Assess: The system assigns a verdict based on evidence quality, claim support, and uncertainty.
Report: The user receives an explanation with source citations and relevant evidence snippets.
Evaluate: Test outcomes, errors, and quality metrics are recorded to support iterative improvement.
🛠️ Technology Stack
Component	Technology	Purpose
OCR and text extraction	Tesseract OCR or a compatible vision API	Extract text from screenshots and images
Web search	Tavily Search API	Retrieve relevant external evidence
Source validation	Configurable domain allowlist and URL checks	Prioritize authoritative sources and detect suspicious domains
AI analysis	Compatible Large Language Model (LLM)	Analyse claims and compare them against retrieved evidence
Backend and data storage	Supabase	Store application data, investigation records, and evaluation results
Version control	Git and GitHub	Collaborate on development and manage code changes
The final implementation may vary according to integration requirements and available services.

🧪 Testing and Evaluation
Digital Detective is designed to be evaluated against realistic scenarios, including:

Genuine scholarship announcements and fabricated scholarship offers.
Legitimate recruitment notices and suspicious job offers.
Government schemes with altered benefits or eligibility requirements.
Spoofed domains and impersonated organisations.
Expired announcements and inaccessible URLs.
Blurry screenshots and OCR extraction errors.
Empty search results, API timeouts, and conflicting evidence.
Unsupported claims and citations that do not substantiate a conclusion.
Evaluation Metrics
Metric	Objective
Retrieval relevance	Measure whether retrieved sources are relevant to the investigated claims.
Source quality	Assess whether the evidence comes from appropriate, authoritative sources.
Citation support rate	Measure the proportion of factual claims adequately supported by their citations.
Verdict accuracy	Evaluate classifications against independently established test-case outcomes.
OCR robustness	Measure extraction quality across different image conditions.
Failure handling	Evaluate behaviour when APIs, URLs, or evidence retrieval fail.
Evaluation results will be reported from actual test runs rather than assumed in advance.

⚠️ Limitations and Responsible Use
An official-looking domain or logo does not independently prove that a message is genuine.
A trusted source may establish that an organisation or scheme exists without validating a particular offer.
Search results can be incomplete, outdated, or inconsistent.
OCR may misread numbers, names, URLs, and other critical details.
A lack of evidence is not, by itself, proof of fraud.
AI-generated assessments can be incorrect and should be reviewed carefully before users make consequential decisions.
Digital Detective is intended to support informed decision-making, not replace independent verification or official advice.

🚀 Project Status
Development status: [Update to reflect the current implementation stage]

Planned development milestones include:

 Multimodal input and OCR integration
 Tavily-based evidence retrieval
 Trusted-source selection and URL validation
 Evidence
