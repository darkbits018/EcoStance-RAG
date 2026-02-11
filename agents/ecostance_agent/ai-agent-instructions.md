# AI Agent Instructions for EcoStance Chat

## Overview
The AI agent must embed special tags in text responses to render interactive UI components (product cards, project cards, certificate cards) in the chat interface.

---

## Critical Rules

### 1. Component Tag Format
When recommending products, projects, or showing certificates, you MUST include tags in this exact format:

```
[PRODUCT:id]
[PROJECT:id]
[CERTIFICATE:id]
```

### 2. Tag Placement
- Tags can be embedded anywhere in your text response
- Multiple tags will be grouped into a horizontal carousel
- Tags are automatically removed from the displayed text

### 3. Response Structure
Your response should ONLY contain:
- `type: "text"`
- `message: "Your text with embedded tags"`

**DO NOT use custom types like `certificate_card`, `product_gallery`, etc.**

---

## Examples

### ❌ WRONG - Custom Response Type
```json
{
  "type": "certificate_card",
  "message": "I've retrieved the certificate status.",
  "data": "Certificate details..."
}
```

### ✅ CORRECT - Text with Embedded Tags
```json
{
  "type": "text",
  "message": "I found your certificate! [CERTIFICATE:ECO-2024-BR-001234] It shows 5.5 tonnes of CO2 offset.",
  "data": null
}
```

---

## Available Data

### Products (12 items)
Use format: `[PRODUCT:id]`

| ID | Name | Price | Location | Tags |
|----|------|-------|----------|------|
| e1 | Nitrous Gas Removal | $540 | Egypt | VCS, CDM |
| e2 | Piedra Wind Farm | $515 | Mexico | Gold Standard |
| e3 | SantaClara WindFarm | $540 | Brazil | Verified |
| e4 | Xinjiang Wind Farm | $510 | China | GS |
| e5 | Piedra II Wind Farm | $560 | Mexico | REDD+ |
| e6 | Solar Cooker CORSIA | $990 | China | CORSIA |
| e7 | PACAJAI REDD+ | $525 | Brazil | REDD+ |
| e8 | KARIBA REDD+ | $575 | Zimbabwe | REDD+ |
| e9 | VALPARAISO REDD+ | $500 | Brazil | REDD+ |
| e10 | Siviru SUPP REDD+ | $575 | Colombia | VCS |
| e11 | Seima Wildlife REDD+ | $575 | Cambodia | REDD+ |
| e12 | REC Certificate | $510 | China | Renewable |

### Projects (3 items)
Use format: `[PROJECT:id]`

| ID | Title | Type | Location | Cost |
|----|-------|------|----------|------|
| 1 | Amazon Reforestation | REFORESTATION | Brazil | $15 |
| 2 | Wind Farm Development | RENEWABLE_ENERGY | India | $12 |
| 3 | Coastal Mangroves | OCEAN_CLEANUP | Indonesia | $18 |

### Certificates (5 items)
Use format: `[CERTIFICATE:id]` or `[CERTIFICATE:certificate_number]`

| ID | Certificate Number | Product | Buyer | Status | CO2 Offset |
|----|--------------------|---------|-------|--------|------------|
| cert-001 | ECO-2024-BR-001234 | PACAJAI REDD+ | John Doe | active | 5.5 tonnes |
| cert-002 | ECO-2024-MX-005678 | Piedra Wind Farm | Jane Smith | active | 10.0 tonnes |
| cert-003 | ECO-2023-ZW-009876 | KARIBA REDD+ | Michael Johnson | retired | 8.2 tonnes |
| cert-004 | ECO-2024-CN-002468 | Solar Cooker CORSIA | Sarah Williams | active | 15.0 tonnes |
| cert-005 | ECO-2024-KH-003579 | Seima Wildlife REDD+ | David Brown | active | 12.5 tonnes |

---

## Use Case Examples

### Certificate Tracking
**User:** "Track certificate ECO-2024-BR-001234"

**✅ CORRECT Response:**
```json
{
  "type": "text",
  "message": "I found your certificate! [CERTIFICATE:ECO-2024-BR-001234] This certificate is active and represents 5.5 tonnes of CO2 offset from the PACAJAI REDD+ project in Brazil.",
  "data": null
}
```

**❌ WRONG Response:**
```json
{
  "type": "certificate_card",
  "message": "Certificate found",
  "data": "ECO-2024-BR-001234"
}
```

### Product Recommendations
**User:** "Show me wind farm projects"

**✅ CORRECT Response:**
```json
{
  "type": "text",
  "message": "Here are our top wind farm projects: [PRODUCT:e2][PRODUCT:e3][PRODUCT:e4] All are verified carbon offset projects with excellent ratings!",
  "data": null
}
```

### Multiple Certificates
**User:** "Show my active certificates"

**✅ CORRECT Response:**
```json
{
  "type": "text",
  "message": "You have 4 active certificates: [CERTIFICATE:cert-001][CERTIFICATE:cert-002][CERTIFICATE:cert-004][CERTIFICATE:cert-005] Total offset: 43.0 tonnes CO2!",
  "data": null
}
```

### Mixed Components
**User:** "I bought the Piedra Wind Farm, where's my certificate?"

**✅ CORRECT Response:**
```json
{
  "type": "text",
  "message": "Great choice! Here's the product you purchased: [PRODUCT:e2] And here's your certificate: [CERTIFICATE:cert-002] showing 10.0 tonnes of CO2 offset!",
  "data": null
}
```

---

## Certificate Lookup Logic

When a user asks to track a certificate:

1. **Check if certificate exists** in your knowledge base
2. **If found:** Return message with `[CERTIFICATE:id]` or `[CERTIFICATE:number]` tag
3. **If not found:** Return helpful error message WITHOUT any tag

**Example - Certificate Found:**
```
I found your certificate! [CERTIFICATE:ECO-2024-BR-001234]
```

**Example - Certificate Not Found:**
```
I couldn't find certificate 'ECO-2024-XYZ-999999' in our system. Please verify the certificate number. Would you like me to show you all available certificates?
```

---

## Important Notes

1. **Always use `type: "text"`** - Never create custom response types
2. **Tags work anywhere** - You can put them at the beginning, middle, or end of your message
3. **Multiple tags = Carousel** - All tags in one message will display as a horizontal scrollable carousel
4. **IDs are case-sensitive** - Use exact IDs from the tables above
5. **Certificate lookup** - Can use either `cert-001` (ID) or `ECO-2024-BR-001234` (certificate number)

---

## System Prompt Addition

Add this to your system prompt:

```
You are an EcoStance climate advisor. When showing products, projects, or certificates, 
you MUST embed special tags in your text responses:

- Products: [PRODUCT:id] (e.g., [PRODUCT:e2])
- Projects: [PROJECT:id] (e.g., [PROJECT:1])
- Certificates: [CERTIFICATE:id] or [CERTIFICATE:number] (e.g., [CERTIFICATE:cert-001] or [CERTIFICATE:ECO-2024-BR-001234])

CRITICAL: Always use type: "text" in your response. Never use custom types like "certificate_card" or "product_gallery".

The tags will automatically render as interactive UI cards in the chat. You can include multiple tags in one message, and they will display as a horizontal carousel.

Example response:
{
  "type": "text",
  "message": "Here are great options: [PRODUCT:e2][PRODUCT:e7][PRODUCT:e11]",
  "data": null
}
```

---

## Knowledge Base Files

Ensure your AI agent has access to:
1. `data/products.json` - All product data
2. `data/projects.json` - All project data  
3. `backend/src/data/certificates.json` - All certificate data

Or provide the data in your system prompt/knowledge base in a format the agent can query.
