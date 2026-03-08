# Smart Irrigation System - Diagrams & Visualizations

## 1. SEQUENCE DIAGRAM

Shows the flow of interactions between components when a farmer requests irrigation recommendations.

```
Farmer/Sensor    Dashboard    Backend API    LSTM Model    Rule Engine    LLM    Twilio
    |                |            |              |             |           |        |
    |--Sensor Data-->|            |              |             |           |        |
    |                |--Request-->|              |             |           |        |
    |                |            |--Forecast-->|             |           |        |
    |                |            |<--Prediction|             |           |        |
    |                |            |--Decision-->|             |           |        |
    |                |            |<--Irrigate?-|             |           |        |
    |                |            |--Explain--->|             |           |        |
    |                |            |<--Explanation|             |           |        |
    |                |<--Response-|             |             |           |        |
    |                |--Display-->|             |             |           |        |
    |                |            |--Alert----->|             |           |        |
    |                |            |             |             |           |--SMS-->|
    |<--Notification-|            |             |             |           |        |
    |                |            |             |             |           |        |
```

**Flow Steps:**
1. Sensor sends soil moisture data
2. Dashboard requests irrigation decision
3. Backend fetches LSTM forecast
4. Rule engine determines if irrigation needed
5. LLM generates farmer-friendly explanation
6. Alert sent via Twilio if action needed
7. Dashboard displays results to farmer

---

## 2. ARCHITECTURE DIAGRAM

Shows the system components and their relationships.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SMART IRRIGATION SYSTEM                      │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│                        FRONTEND LAYER                                 │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │              Streamlit Dashboard                            │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │    │
│  │  │ Soil Insights│  │Weather Data  │  │Irrigation    │      │    │
│  │  │              │  │              │  │Recommendations│      │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘      │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │    │
│  │  │ AI Explanation│ │Language Sel. │  │Voice I/O     │      │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘      │    │
│  └─────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────┘
                                  ↓
┌──────────────────────────────────────────────────────────────────────┐
│                        API LAYER (FastAPI)                            │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  /predict - Get irrigation decision                          │   │
│  │  /forecast - Get soil moisture forecast                      │   │
│  │  /explain - Get AI explanation                               │   │
│  │  /alert - Send notification                                  │   │
│  └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
                                  ↓
┌──────────────────────────────────────────────────────────────────────┐
│                      BUSINESS LOGIC LAYER                             │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │  LSTM Forecaster │  │ Rule-Based Engine│  │ LLM Explainer    │  │
│  │                  │  │ (FAO-56)         │  │ (Groq API)       │  │
│  │ • Soil moisture  │  │ • Threshold: 24% │  │ • Farmer-friendly│  │
│  │   prediction     │  │ • MAD: 40%       │  │   language       │  │
│  │ • 7-day forecast │  │ • FC: 30%        │  │ • Multilingual   │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│                                                                       │
│  ┌──────────────────┐  ┌──────────────────┐                         │
│  │ Alert Generator  │  │ Weather Integrator                         │
│  │                  │  │                  │                         │
│  │ • SMS/WhatsApp   │  │ • API integration│                         │
│  │ • Real-time      │  │ • Rainfall data  │                         │
│  │ • Retry logic    │  │ • Temperature    │                         │
│  └──────────────────┘  └──────────────────┘                         │
└──────────────────────────────────────────────────────────────────────┘
                                  ↓
┌──────────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                                     │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │ PostgreSQL DB    │  │ Timestream       │  │ Model Storage    │  │
│  │ (Decisions)      │  │ (Time-series)    │  │ (LSTM, RL)       │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│                                                                       │
│  ┌──────────────────┐  ┌──────────────────┐                         │
│  │ Sensor Data      │  │ Weather Cache    │                         │
│  │ (CSV/Real-time)  │  │                  │                         │
│  └──────────────────┘  └──────────────────┘                         │
└──────────────────────────────────────────────────────────────────────┘
                                  ↓
┌──────────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                                  │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │ Twilio           │  │ Weather API      │  │ Groq LLM API     │  │
│  │ (SMS/WhatsApp)   │  │ (OpenWeather)    │  │ (llama-3.3-70b)  │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 3. USE CASE DIAGRAM

Shows all actors and their interactions with the system.

```
                              ┌─────────────────────────────┐
                              │  Smart Irrigation System    │
                              └─────────────────────────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
                    ▼                   ▼                   ▼
            ┌──────────────┐    ┌──────────────┐   ┌──────────────┐
            │   Farmer     │    │   System     │   │   Admin      │
            │              │    │   Admin      │   │              │
            └──────────────┘    └──────────────┘   └──────────────┘
                    │                   │                   │
        ┌───────────┼───────────┐       │       ┌───────────┼───────────┐
        │           │           │       │       │           │           │
        ▼           ▼           ▼       ▼       ▼           ▼           ▼
    ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
    │ View    │ │ Receive │ │ Get AI  │ │ Monitor  │ │ Configure│ │ Manage   │
    │ Soil    │ │ Alerts  │ │Explain- │ │ System   │ │ System   │ │ Users    │
    │ Insights│ │ (SMS/   │ │ations   │ │ Health   │ │ Settings │ │ & Roles  │
    │         │ │WhatsApp)│ │         │ │          │ │          │ │          │
    └─────────┘ └─────────┘ └─────────┘ └──────────┘ └──────────┘ └──────────┘
        │           │           │           │           │           │
        └───────────┼───────────┴───────────┼───────────┴───────────┘
                    │                       │
        ┌───────────┴───────────┐   ┌───────┴───────────┐
        │                       │   │                   │
        ▼                       ▼   ▼                   ▼
    ┌─────────────┐         ┌──────────────┐    ┌──────────────┐
    │ Get Irrig.  │         │ Predict Soil │    │ Integrate    │
    │ Decision    │         │ Moisture     │    │ Weather Data │
    │ (FAO-56)    │         │ (LSTM)       │    │              │
    └─────────────┘         └──────────────┘    └──────────────┘
        │                       │                   │
        └───────────┬───────────┴───────────────────┘
                    │
                    ▼
            ┌──────────────────┐
            │ Generate Farmer- │
            │ Friendly Explain │
            │ (LLM)            │
            └──────────────────┘
```

**Key Actors:**
- **Farmer**: Primary user who views recommendations and receives alerts
- **System Admin**: Manages system configuration and monitoring
- **Admin**: Manages users, roles, and system settings

**Key Use Cases:**
- View soil insights and weather data
- Receive irrigation alerts via SMS/WhatsApp
- Get AI-generated explanations
- Monitor system health
- Configure system parameters
- Manage user access

---

## 4. WIREFRAME DIAGRAM

A wireframe shows the layout and structure of the user interface without detailed design.

### Dashboard Wireframe (Streamlit)

```
┌────────────────────────────────────────────────────────────────────┐
│                    AQUASMART DASHBOARD                             │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ 🌾 Smart Irrigation System                                   │ │
│  │ Language: [English ▼]  |  Farm: [Select Farm ▼]             │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│  ┌──────────────────────────┐  ┌──────────────────────────────┐  │
│  │ 💧 SOIL INSIGHTS         │  │ 🌤️  WEATHER INSIGHTS        │  │
│  ├──────────────────────────┤  ├──────────────────────────────┤  │
│  │ Current Moisture: 28%    │  │ Temperature: 32°C            │  │
│  │ Field Capacity: 30%      │  │ Humidity: 65%                │  │
│  │ Wilting Point: 15%       │  │ Rainfall (24h): 5mm          │  │
│  │ Status: ⚠️ CAUTION       │  │ Wind Speed: 12 km/h          │  │
│  │                          │  │ Forecast: Sunny              │  │
│  │ [Soil Chart]             │  │ [Weather Chart]              │  │
│  └──────────────────────────┘  └──────────────────────────────┘  │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ 🚿 IRRIGATION RECOMMENDATION                                 │ │
│  ├──────────────────────────────────────────────────────────────┤ │
│  │ Decision: ✅ IRRIGATE NOW                                    │ │
│  │ Recommended Water: 25 mm                                     │ │
│  │ Best Time: 6:00 AM - 8:00 AM                                 │ │
│  │ Urgency Level: 🔴 HIGH                                       │ │
│  │ Confidence: 94%                                              │ │
│  │                                                              │ │
│  │ [Irrigation Timeline Chart]                                  │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ 🤖 AI EXPLANATION                                            │ │
│  ├──────────────────────────────────────────────────────────────┤ │
│  │ "Your soil moisture is at 28%, which is below the safe       │ │
│  │  threshold of 24%. Your crops are starting to experience     │ │
│  │  water stress. Irrigate with 25mm of water in the early      │ │
│  │  morning to maximize absorption and minimize evaporation.    │ │
│  │  The forecast shows sunny weather, so water loss will be     │ │
│  │  high. Act within the next 2 hours."                         │ │
│  │                                                              │ │
│  │ [🔊 Play Audio]  [📋 Copy Text]  [🌐 Translate]             │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│  ┌──────────────────────────┐  ┌──────────────────────────────┐  │
│  │ 📊 7-DAY FORECAST        │  │ 📈 WATER SAVINGS             │  │
│  ├──────────────────────────┤  ├──────────────────────────────┤  │
│  │ [Soil Moisture Trend]    │  │ This Month: 1,250 L saved    │  │
│  │ Day 1: 26%               │  │ This Season: 8,500 L saved   │  │
│  │ Day 2: 24%               │  │ Efficiency: +23%             │  │
│  │ Day 3: 22%               │  │ [Savings Chart]              │  │
│  │ Day 4: 20%               │  │                              │  │
│  │ Day 5: 19%               │  │                              │  │
│  │ Day 6: 21%               │  │                              │  │
│  │ Day 7: 25%               │  │                              │  │
│  └──────────────────────────┘  └──────────────────────────────┘  │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ 💬 FARMER CHAT                                               │ │
│  ├──────────────────────────────────────────────────────────────┤ │
│  │ [Chat History]                                               │ │
│  │ Farmer: "Why should I irrigate now?"                         │ │
│  │ System: "Your soil moisture is 28%, below the 24% threshold" │ │
│  │                                                              │ │
│  │ [Input Box: Ask a question...]  [Send]                       │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ 🔔 RECENT ALERTS                                             │ │
│  ├──────────────────────────────────────────────────────────────┤ │
│  │ ✅ 2 hours ago: Irrigation alert sent (SMS)                  │ │
│  │ ⚠️  5 hours ago: High temperature warning                    │ │
│  │ ℹ️  1 day ago: Rainfall detected (5mm)                       │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

**Wireframe Components:**

1. **Header**: Title, language selector, farm selector
2. **Soil Insights Panel**: Current moisture, field capacity, status
3. **Weather Insights Panel**: Temperature, humidity, rainfall, forecast
4. **Irrigation Recommendation Panel**: Decision, water quantity, timing, urgency
5. **AI Explanation Panel**: Farmer-friendly text with audio/translation options
6. **7-Day Forecast Panel**: Soil moisture trend prediction
7. **Water Savings Panel**: Metrics and efficiency gains
8. **Farmer Chat Panel**: Q&A interface with LLM
9. **Recent Alerts Panel**: Alert history

---

## 5. DATA FLOW DIAGRAM

Shows how data moves through the system.

```
┌─────────────────┐
│  Soil Sensors   │
│  (IoT Devices)  │
└────────┬────────┘
         │
         │ Raw Data (Moisture, Temp, pH)
         ▼
┌─────────────────────────────────────┐
│  Data Ingestion Layer               │
│  • Validation                       │
│  • Preprocessing                    │
│  • Normalization                    │
└────────┬────────────────────────────┘
         │
         ├─────────────────────────────────────┐
         │                                     │
         ▼                                     ▼
┌──────────────────────┐          ┌──────────────────────┐
│  Timestream DB       │          │  PostgreSQL DB       │
│  (Time-series)       │          │  (Decisions)         │
└──────────────────────┘          └──────────────────────┘
         │                                     │
         │                                     │
         ▼                                     ▼
┌──────────────────────────────────────────────────────┐
│  LSTM Model                                          │
│  • Input: Last 30 days of soil data                  │
│  • Output: 7-day moisture forecast                   │
│  • Normalization: [0, 1] range                       │
└────────┬─────────────────────────────────────────────┘
         │
         │ Forecast (Predicted Moisture %)
         ▼
┌──────────────────────────────────────────────────────┐
│  Rule-Based Decision Engine (FAO-56)                 │
│  • Threshold: 24%                                    │
│  • MAD: 40%                                          │
│  • Field Capacity: 30%                               │
│  • Decision: Irrigate / Don't Irrigate               │
└────────┬─────────────────────────────────────────────┘
         │
         ├─────────────────────────────────────┐
         │                                     │
         ▼                                     ▼
┌──────────────────────┐          ┌──────────────────────┐
│  LLM Explainer       │          │  Alert Generator     │
│  (Groq API)          │          │  • SMS/WhatsApp      │
│  • Farmer language   │          │  • Urgency level     │
│  • Context-aware     │          │  • Retry logic       │
└────────┬─────────────┘          └────────┬─────────────┘
         │                                 │
         │ Explanation Text                │ Alert Message
         │                                 │
         ▼                                 ▼
┌──────────────────────────────────────────────────────┐
│  Dashboard (Streamlit)                               │
│  • Display recommendation                            │
│  • Show explanation                                  │
│  • Visualize trends                                  │
└──────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────┐
│  Farmer                                              │
│  • Views dashboard                                   │
│  • Receives SMS/WhatsApp alert                       │
│  • Takes irrigation action                           │
└──────────────────────────────────────────────────────┘
```

---

## 6. DECISION TREE DIAGRAM

Shows the irrigation decision logic.

```
                    START
                      │
                      ▼
            ┌─────────────────────┐
            │ Get Current Soil    │
            │ Moisture Level      │
            └──────────┬──────────┘
                       │
                       ▼
            ┌─────────────────────┐
            │ Moisture < 24%?     │
            │ (Threshold)         │
            └──────┬──────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
       YES                    NO
        │                     │
        ▼                     ▼
    ┌────────────┐    ┌──────────────────┐
    │ Check      │    │ Moisture < 15%?  │
    │ Rainfall   │    │ (Wilting Point)  │
    │ (24h)      │    └────────┬─────────┘
    └────┬───────┘             │
         │              ┌──────┴──────┐
         ▼              │             │
    ┌─────────────┐    YES           NO
    │ Rain > 5mm? │     │             │
    └──┬──────┬───┘     ▼             ▼
       │      │    ┌─────────┐   ┌──────────┐
      YES    NO    │ CRITICAL│   │ ADEQUATE │
       │      │    │ STRESS  │   │ MOISTURE │
       │      │    │ IRRIGATE│   │ NO ACTION│
       │      │    │ URGENT  │   │          │
       │      │    └─────────┘   └──────────┘
       │      │
       ▼      ▼
    ┌──────────────────┐
    │ Check Weather    │
    │ Forecast         │
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │ Rain Expected    │
    │ in 24h?          │
    └────┬──────┬──────┘
         │      │
        YES    NO
         │      │
         ▼      ▼
    ┌────────┐ ┌──────────────┐
    │ DEFER  │ │ IRRIGATE NOW │
    │ ACTION │ │ Calculate:   │
    │ WAIT   │ │ • Water qty  │
    └────────┘ │ • Best time  │
               │ • Urgency    │
               └──────────────┘
                      │
                      ▼
               ┌──────────────┐
               │ Send Alert   │
               │ & Explain    │
               └──────────────┘
                      │
                      ▼
                    END
```

---

## 7. COMPONENT INTERACTION DIAGRAM

Shows how different components communicate.

```
┌─────────────────────────────────────────────────────────────────┐
│                    COMPONENT INTERACTIONS                        │
└─────────────────────────────────────────────────────────────────┘

Dashboard ◄──────────────────────────────────────────────► Backend API
   │                                                           │
   │ HTTP Requests                                             │
   │ (GET /predict, /forecast, /explain)                       │
   │                                                           │
   └──────────────────────────────────────────────────────────┘
                                                               │
                                                               ▼
                                                    ┌──────────────────┐
                                                    │ Request Router   │
                                                    └────────┬─────────┘
                                                             │
                                    ┌────────────────────────┼────────────────────────┐
                                    │                        │                        │
                                    ▼                        ▼                        ▼
                            ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
                            │ LSTM Model   │      │ Rule Engine  │      │ LLM Service  │
                            │              │      │              │      │              │
                            │ • Load model │      │ • FAO-56     │      │ • Groq API   │
                            │ • Normalize  │      │ • Threshold  │      │ • Prompt     │
                            │ • Predict    │      │ • Decision   │      │ • Generate   │
                            └──────┬───────┘      └──────┬───────┘      └──────┬───────┘
                                   │                     │                     │
                                   └─────────────────────┼─────────────────────┘
                                                         │
                                                         ▼
                                            ┌──────────────────────┐
                                            │ Response Formatter   │
                                            │                      │
                                            │ • Combine results    │
                                            │ • Format JSON        │
                                            │ • Add metadata       │
                                            └──────────┬───────────┘
                                                       │
                                                       ▼
                                            ┌──────────────────────┐
                                            │ Alert Generator      │
                                            │                      │
                                            │ • Check urgency      │
                                            │ • Format message     │
                                            │ • Queue alert        │
                                            └──────────┬───────────┘
                                                       │
                                                       ▼
                                            ┌──────────────────────┐
                                            │ Twilio Service       │
                                            │                      │
                                            │ • Send SMS           │
                                            │ • Send WhatsApp      │
                                            │ • Track delivery     │
                                            └──────────────────────┘
```

---

## Summary

- **Sequence Diagram**: Shows the temporal flow of interactions
- **Architecture Diagram**: Shows system components and layers
- **Use Case Diagram**: Shows actors and their interactions
- **Wireframe Diagram**: Shows UI layout and structure
- **Data Flow Diagram**: Shows how data moves through the system
- **Decision Tree**: Shows irrigation decision logic
- **Component Interaction**: Shows how components communicate

These diagrams are useful for presentations, documentation, and understanding the system design.
