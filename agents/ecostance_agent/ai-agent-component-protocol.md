# AI Agent Component Rendering Protocol

This document describes how the AI agent should format responses to render interactive components (product cards, project cards) within the chat interface.

---

## Overview

The chat component can parse special tags in the AI's text response and render rich UI components inline. This allows the AI to recommend specific products or projects with full visual cards.

---

## Component Tags

### Product Card
To render a product card, include this tag in your response:

```
[PRODUCT:product_id]
```

**Example:**
```
I recommend the [PRODUCT:e1] for carbon offsetting in Egypt.
```

**Renders:**
- Product image
- Product name
- Price (with old price if on sale)
- Rating and reviews
- Location
- Tags
- Sale/New badges

---

### Project Card
To render a project card, include this tag in your response:

```
[PROJECT:project_id]
```

**Example:**
```
Check out this amazing initiative: [PROJECT:1]
```

**Renders:**
- Project image
- Project title
- Description
- Location
- Project type badge
- Offset cost

---

## Available Product IDs

| ID | Name | Price | Location | Tags |
|----|------|-------|----------|------|
| `e1` | Nitrous Gas Removal | $540 | Egypt | VCS, CDM |
| `e2` | Piedra Wind Farm | $515 | Mexico | Gold Standard |
| `e3` | SantaClara WindFarm | $540 | Brazil | Verified |
| `e4` | Xinjiang Wind Farm | $510 | China | GS |
| `e5` | Piedra II Wind Farm | $560 | Mexico | REDD+ |
| `e6` | Solar Cooker CORSIA | $990 | China | CORSIA |
| `e7` | PACAJAI REDD+ | $525 | Brazil | REDD+ |
| `e8` | KARIBA REDD+ | $575 | Zimbabwe | REDD+ |
| `e9` | VALPARAISO REDD+ | $500 | Brazil | REDD+ |
| `e10` | Siviru SUPP REDD+ | $575 | Colombia | VCS |
| `e11` | Seima Wildlife REDD+ | $575 | Cambodia | REDD+ |
| `e12` | REC Certificate | $510 | China | Renewable |

---

## Available Project IDs

| ID | Title | Type | Location | Cost |
|----|-------|------|----------|------|
| `1` | Amazon Reforestation | REFORESTATION | Brazil | $15 |
| `2` | Wind Farm Development | RENEWABLE_ENERGY | India | $12 |
| `3` | Coastal Mangroves | OCEAN_CLEANUP | Indonesia | $18 |

---

## Response Format Examples

### Single Product Recommendation
```
Based on your interest in wind energy, I recommend the [PRODUCT:e2]. 
It's a Gold Standard certified project in Mexico with excellent ratings.
```

### Multiple Products
```
Here are some great options for you:

1. [PRODUCT:e7] - Great for rainforest protection
2. [PRODUCT:e8] - Wildlife conservation in Zimbabwe
3. [PRODUCT:e11] - Biodiversity protection in Cambodia

All of these are REDD+ certified projects.
```

### Product with Project
```
If you're interested in reforestation, check out [PRODUCT:e7] for carbon credits, 
or support [PROJECT:1] directly to help restore the Amazon rainforest.
```

### Text Only (No Components)
```
Carbon offsetting is a way to compensate for your emissions by funding 
environmental projects. Would you like to see some options?
```

---

## Parsing Logic

The chat component uses this regex pattern:
```javascript
/\[(PRODUCT|PROJECT):([^\]]+)\]/g
```

**How it works:**
1. Scans the AI response for `[PRODUCT:id]` or `[PROJECT:id]` tags
2. Extracts the type (PRODUCT or PROJECT) and ID
3. Fetches the corresponding data from the API
4. Renders the appropriate card component inline
5. Displays remaining text normally

---

## Best Practices for AI Responses

### ✅ DO:
- Use tags naturally within conversational text
- Provide context before showing a product/project
- Recommend relevant items based on user queries
- Mix text and components for better UX
- Use multiple tags if showing several options

### ❌ DON'T:
- Send only tags without explanatory text
- Use invalid IDs (component won't render)
- Overload responses with too many cards (max 3-4)
- Use tags in the middle of sentences awkwardly

---

## Example Conversations

### User: "Show me wind farm projects"
**AI Response:**
```
Great choice! Wind energy is one of the most effective renewable solutions. 
Here are our top wind farm projects:

[PRODUCT:e2] - Highly rated project in Mexico
[PRODUCT:e3] - Brazilian wind farm with excellent reviews
[PRODUCT:e4] - Cost-effective option in China

All of these are verified carbon offset projects. Would you like more details on any of them?
```

### User: "I want to help with reforestation"
**AI Response:**
```
Wonderful! Reforestation is crucial for carbon sequestration. I have two great options:

For carbon credits: [PRODUCT:e7] - PACAJAI REDD+ project in Brazil
For direct support: [PROJECT:1] - Amazon Reforestation initiative

Both focus on protecting and restoring critical rainforest habitats. Which interests you more?
```

### User: "What's on sale?"
**AI Response:**
```
We have several carbon offset projects on sale right now:

[PRODUCT:e1] - Save $100 on Nitrous Gas Removal
[PRODUCT:e6] - $165 off Solar Cooker CORSIA
[PRODUCT:e7] - $105 discount on PACAJAI REDD+

These are limited-time offers on verified projects!
```

---

## Technical Implementation

### Frontend (React)
The chat component:
1. Loads all products and projects on mount via API
2. Stores them in state
3. Parses AI responses for tags
4. Looks up products/projects by ID
5. Renders `<ProductCard>` or `<ProjectCard>` components

### Backend (AI Agent)
Your AI agent should:
1. Have access to the product/project catalog
2. Understand user intent (search, filter, recommend)
3. Select relevant items based on query
4. Format response with appropriate tags
5. Provide helpful context around recommendations

---

## Error Handling

**Invalid ID:**
If the AI sends `[PRODUCT:invalid_id]`, the tag is ignored and not rendered.

**Missing Data:**
If products/projects haven't loaded yet, tags won't render until data is available.

**Malformed Tags:**
Tags must exactly match the format `[TYPE:id]` - no spaces, correct brackets.

---

## Future Enhancements

Potential additions to the protocol:
- `[BUNDLE:id]` - Product bundles
- `[CERTIFICATE:id]` - Certificate cards
- `[IMPACT:stats]` - Impact statistics widget
- `[COMPARISON:id1,id2]` - Side-by-side comparison

---

## API Integration

The chat component fetches data from:
- `GET /api/products` - All products
- `GET /api/projects` - All projects

Make sure your AI agent has access to the same data source or catalog to ensure ID consistency.
