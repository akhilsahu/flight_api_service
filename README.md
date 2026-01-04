ngrok http --url=star-moderately-penguin.ngrok-free.app 5000


ngrok http 127.0.0.1:5000 --url=star-moderately-penguin.ngrok-free.app

**Note:** The application is configured to handle CORS (Cross-Origin Resource Sharing) headers, so it is not necessary to add them via ngrok.

Here is the full **README.md** file using standard GitHub Markdown. This includes technical badges, code blocks, and a clear explanation of your parallel "Clubbed" architecture.

---

# ✈️ Distributed Flight Scraper API

A high-performance flight aggregator that scrapes multiple travel sources in parallel. It uses **Celery Chords** to synchronize background workers and **Server-Sent Events (SSE)** to stream a "Clubbed Collection" of results directly to the user's browser.

## 🏗️ Architecture Flow

1. **Client** initiates a search via `/api/flight/start`.
2. **Flask** generates a `task_id` and triggers a **Celery Chord**.
3. **Workers** run scrapers (MMT, Ixigo, etc.) in parallel. Each worker publishes its own progress to **Redis Pub/Sub**.
4. **Merge Task** (The Callback) triggers only after all scrapers finish. It clubs data by `flight_no`.
5. **SSE Stream** pushes the updates to the frontend in real-time.

---

## 📡 API Reference

### 1. Initialize Scraping

**Endpoint:** `GET /api/flight/start`

| Parameter | Type | Description |
| --- | --- | --- |
| `from` | `string` | Origin IATA (e.g., DEL) |
| `to` | `string` | Destination IATA (e.g., BOM) |
| `travel_date` | `string` | ISO Date (YYYY-MM-DD) |

**Response:**

```json
{
  "task_id": "a87b6c5d-4e32-11ec-81d3-0242ac130003"
}

```

### 2. Live Results Stream

**Endpoint:** `GET /api/flight/stream/<task_id>`

Connect via `EventSource` in JavaScript to receive real-time updates.

**Stream Event Types:**

* **Progress:** `{"status": "Searching MMT...", "source": "mmt"}`
* **Partial Results:** Individual source data as it finishes.
* **TOTAL Collection:** The final clubbed and sorted dictionary.

---

## 📊 Data Structure

The API returns a **Clubbed Collection** under the `TOTAL` source to prevent duplicate flight listings.

```json
{
  "6E6065": {
    "mmt": [
      {
        Airline: "IndiGo"
        Arrival_City: "Mumbai"
        Arrival_Time: "21:25"
        Departure_City: "New Delhi"
        Departure_Time: "19:00"
        Layover_City: "Non stop"
        Layover_Duration: "02 h 25 m "
        Offers: "FLAT  ₹ 147 OFF using MMTSUPER"
        Price: "₹ 7,214"
        flight_no: "6E 354"
      }
    ],
    "ixigo": [
      {
        "Airline: "IndiGo"
Arrival_City: "BOM"
Arrival_Time: "21:25"
Departure_City: "DEL"
Departure_Time: "19:00"
Duration: "2h 25m"
Layover_City: null
Layover_Duration: null
Offers: "Extra ₹275 Off"
Price: "₹7,214"
extra_badges: null
flight_no: "6E354"
flight_type: "Standard"
source: "ixigo"
      }
    ]
  }
}

```

---

## 🛠️ Installation & Setup

### Prerequisites

* Docker & Docker Compose
* Python 3.9+

### Environment Variables

Create a `.env` file or set in `docker-compose.yml`:

```bash
PYTHONUNBUFFERED=1  # Required for real-time Docker logs
REDIS_URL=redis://localhost:6379/0

```

### Running the System

```bash
# 1. Build and Start Services
docker-compose up --build

# 2. Start Celery Workers (with high concurrency for parallel scraping)
celery -A worker.celery_app worker --loglevel=info --concurrency=4

```

---

## 🧪 Testing

Open `test_parallel.html` in your browser and point it to your Flask instance (`localhost:5001`). Monitor the **Redis Monitor** to see the Pub/Sub messages:

```bash
docker exec -it <redis_container> redis-cli MONITOR

```

---

**Would you like me to add a "Data Normalization" section explaining how you handle the different currency and date formats between MMT and Ixigo?**