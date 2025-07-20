# Compliance Analysis of Poe Search with Poe.com Terms of Service

## **Overview**
This document reviews the potential compliance of the Poe Search project with Poe.com's Terms of Service (ToS). It highlights areas that may conflict with Poe.com's policies and provides guidance to ensure adherence.

---

## **Potential Areas of Concern**
1. **Automated Interaction with Poe.com**:
   - The project uses the `p-b` cookie to authenticate and interact with Poe.com programmatically.
   - If Poe.com does not provide an official API or prohibits automated data extraction, this may violate their ToS.

2. **Data Scraping or Unauthorized Access**:
   - Accessing and downloading user-specific data without explicit permission from Poe.com may breach their policies.
   - The use of tools like SQLite FTS5 for fast search, although local, relies on extracted data that may not be authorized for such processing.

3. **Reverse Engineering**:
   - If the project reverse-engineers Poe.com's systems to interact programmatically, this is likely a breach of their ToS.

4. **Redistribution or Commercialization**:
   - Exporting or redistributing conversations (e.g., in JSON, CSV, or Markdown formats) might conflict with Poe.com's intellectual property rights.
   - Commercial use of this tool could exacerbate potential violations.

5. **User Privacy and Security**:
   - While the project claims to store tokens securely and process data locally, improper handling of sensitive information (e.g., unencrypted storage of `p-b` tokens) could expose users to risks and indirectly violate Poe.com's ToS.

---

## **Recommendations for Compliance**
1. **Seek Explicit Permission**:
   - Contact Poe.com to obtain explicit permission for programmatically accessing user data.
   - Request official API access if available.

2. **Provide Transparency**:
   - Clearly inform users about potential ToS violations and risks when using the tool.
   - Include disclaimers in the documentation.

3. **Avoid Reverse Engineering**:
   - Ensure the tool does not employ reverse engineering to interact with Poe.com's systems.

4. **Respect Rate Limits**:
   - Adhere to Poe.com's rate-limiting policies to avoid excessive server requests.

5. **Secure Data Handling**:
   - Encrypt sensitive user data (e.g., tokens) at rest and during processing.
   - Encourage users to keep their tokens private and never share them publicly.

6. **Limit Redistribution**:
   - Prohibit redistribution of conversation data unless explicitly permitted by Poe.com's ToS.

---

## **Phase: Legal & Compliance Alignment (Required for Growth and Sustainability)**

### **Summary of Poe.com Terms of Service (July 2025) and Project Impact**

- **Automated Access:** Poe.com prohibits scraping, harvesting, or automated data extraction unless explicitly permitted. API use is only allowed under separate Poe API Terms.
- **Reverse Engineering:** Strictly forbidden. Do not attempt to reverse engineer, decompile, or discover Poe's source code, models, or algorithms.
- **Data Export & Redistribution:** You may not redistribute, publish, or commercialize conversation data unless Poe's ToS explicitly allow it. Commercial use to compete with Poe or its bots is forbidden.
- **User Privacy:** Poe anonymizes personal data before sharing with third-party AI providers. Users must not share sensitive personal information with bots.
- **Termination:** Poe may terminate access for any reason, including ToS violations or inactivity.

### **Action Items for Poe Search Project**

1. **Add Compliance Warnings in All User-Facing Interfaces**
   - Display a compliance disclaimer on startup and in the documentation.
   - Warn users about risks of automated access, data export, and redistribution.

2. **Restrict or Disable Non-Compliant Features**
   - Remove or restrict scraping, automated data extraction, and unauthorized export features.
   - Only enable API features if user has explicit Poe API access.

3. **Enhance Security and Privacy**
   - Encrypt all tokens and sensitive data at rest and in transit.
   - Never transmit user data to third-party servers.

4. **Monitor Poe.com ToS for Changes**
   - Assign responsibility for regular ToS review and update compliance.md and tool features as needed.

5. **User Education**
   - Add onboarding steps that explain legal risks and user responsibilities.
   - Provide links to Poe.com ToS and API Terms.

---

## **Extra Documents to Add**

- `LEGAL_NOTICE.md`: Summarize Poe.com ToS, user risks, and project compliance strategy.
- `CHANGELOG_COMPLIANCE.md`: Track all compliance-related changes and ToS updates.
- `USER_GUIDE_COMPLIANCE.md`: Step-by-step instructions for legal, secure, and private use of Poe Search.

---

## **Important Compliance Notice**

> **Disclaimer:**
> Poe Search is an independent tool and is not affiliated with Poe.com. Use of this tool may violate Poe.com's Terms of Service (ToS) if you access, extract, or redistribute data without explicit permission. By using Poe Search, you acknowledge and accept all risks and responsibilities associated with potential ToS violations.

### **User Responsibilities**
- You must obtain explicit permission from Poe.com before programmatically accessing or exporting your data.
- Do not use Poe Search for commercial purposes or redistribute conversation data unless Poe.com's ToS explicitly allow it.
- Never share your authentication tokens publicly. Always keep them encrypted and private.
- Avoid any reverse engineering or automated scraping that is not permitted by Poe.com's policies.
- Respect Poe.com's rate limits and server resources.

### **Security and Privacy**
- Poe Search encrypts sensitive data (such as tokens) at rest and during processing.
- All data processing is performed locally; no user data is sent to third-party servers.
- Users are responsible for maintaining the security of their credentials and exported data.

### **Transparency and Limitations**
- This tool provides full transparency about its operation and potential risks.
- If Poe.com updates its ToS, you must review and comply with all new restrictions.
- The developers of Poe Search are not liable for any misuse or violations of Poe.com's ToS.

---

## **Conclusion**
The Poe Search tool offers significant utility for managing AI conversations, but it may conflict with Poe.com's Terms of Service in its current form. To mitigate risks, the project should:
- Obtain explicit permissions from Poe.com.
- Enhance transparency and security measures.
- Ensure compliance with Poe.com's policies by avoiding unauthorized interaction or redistribution.

---

**Acknowledgment**: This analysis is based on the publicly available description of the Poe Search project as of [date]. For further clarification or updates, review Poe.com's official documentation or contact their support team.