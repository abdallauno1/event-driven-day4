Day 4 — Multi-Channel Notifications on Top of DLQ

Today I completed the last step of this mini-series by turning the notification worker into a **multi-channel dispatcher** while keeping all the reliability features (retry, TTL, DLX, DLQ) built in Day 2 and Day 3.

The system can now route notifications to different delivery channels (email, SMS, push) using a clean handler-based design.

---

### ✔ What Was Implemented

#### 1. Multi-Channel Worker
The main worker now supports multiple channels:

- `email` → Email handler  
- `sms` → SMS handler  
- `push` → Push handler  

Each handler is a separate function, and a simple mapping decides which handler to call based on `channel` in the message payload.

#### 2. Channel Routing Logic

The `Notification` payload sent from FastAPI includes:

```json
{
  "user_id": "u1",
  "channel": "email | sms | push",
  "message": "Hello!",
  "force_fail": false
}

The worker inspects channel and routes the message to the proper handler.
On failure, it still uses basic_nack(requeue=True) so retry + DLX + DLQ continue to work exactly as before.

3. End-to-End Flow
The final architecture:
	1.	FastAPI receives /notifications requests
	2.	Publishes messages to notifications queue
	3.	Worker consumes and routes to:
	•	Email handler
	•	SMS handler
	•	Push handler
	4.	On repeated failure/TTL expiry:
	•	Message moves to dlx.notifications
	•	Then to notifications.dlq
	•	DLQ Worker consumes and logs dead messages

A visual diagram is available at:

./docs/event-driven-day4.png

🧪 How to Test Day 4

Run the stack:

docker compose up --build


Send different channel notifications:

# Email
curl -X POST http://localhost:8000/notifications \
-H "Content-Type: application/json" \
-d '{"user_id":"u1","channel":"email","message":"Hello via email!","force_fail": false}'

# SMS
curl -X POST http://localhost:8000/notifications \
-H "Content-Type: application/json" \
-d '{"user_id":"u2","channel":"sms","message":"Hello via SMS!","force_fail": false}'

# Push
curl -X POST http://localhost:8000/notifications \
-H "Content-Type: application/json" \
-d '{"user_id":"u3","channel":"push","message":"Hello via push!","force_fail": false}'


To test DLQ with multi-channel routing:

curl -X POST http://localhost:8000/notifications \
-H "Content-Type: application/json" \
-d '{"user_id":"u4","channel":"sms","message":"This will fail","force_fail": true}'


Expected behavior:
	•	Main worker retries and requeues
	•	After TTL, message is routed to notifications.dlq
	•	DLQ worker logs the dead letter



🎯 What This Final Day Represents

This last step turns the project into a realistic event-driven notification backend that demonstrates:
	•	API decoupled from processing
	•	Message queue as a buffer
	•	Retry logic
	•	TTL + Dead Letter Exchange (DLX)
	•	Dead Letter Queue (DLQ) with a dedicated worker
	•	Multi-channel dispatching (email/sms/push)

It’s now a complete, portfolio-ready example of modern backend + messaging architecture.


✅ Summary of the 4 Days
	•	Day 1 — Minimal event-driven system (FastAPI + RabbitMQ + Worker)
	•	Day 2 — Retry logic, structured logs, TTL, DLX foundation
	•	Day 3 — Full DLQ implementation (DLX → DLQ + DLQ worker)
	•	Day 4 — Multi-channel notification routing with the same reliable core



