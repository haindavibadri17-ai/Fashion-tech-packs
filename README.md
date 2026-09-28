# Sakhi — Response, together.

A working front-end prototype of a **police-led, drone-assisted women's safety response platform** for India, built as a pilot control-room dashboard with a citizen SOS experience.

> **⚠️ Simulation only.** Nothing here contacts police, emergency services, drones, CCTV, GPS, or any hardware. Every incident, drone, and metric is synthetic demo data. In a real emergency in India, call **112**.

## What's inside

| Area | What it shows |
|---|---|
| **Response overview** | Live (simulated) incident map of an Indiranagar pilot zone, active incidents, response activity, fleet readiness, pilot KPIs |
| **Citizen SOS simulator** | Hold-for-2-seconds SOS button demo — trigger type, indoor/outdoor, inside/outside coverage; creates a real record in the demo queue |
| **Incidents** | Control-room queue with search, status filters, CSV export, and a full operator flow: review → dispatch (drone + ground together) → arrival → resolve, with an indoor-response protocol |
| **Drone fleet** | 6-aircraft demo fleet with battery, station, availability, and maintenance state |
| **Coverage & stations** | The small approved pilot zone, two response stations, and the indoor-support boundary |
| **Analytics** | Illustrative pilot metrics (median drone/ground arrival, dispatch reliability) with an explicit "not evidence of effectiveness" framing |

## The product story

- A woman triggers an **SOS** (button, discreet gesture, or optional safe word — simulated here).
- Her location reaches an **authorized police control room** through an agreed emergency-response integration (not connected in this demo).
- Within approved coverage, the operator dispatches the **nearest drone and ground responders simultaneously**.
- The drone provides **live video and follows her location**; spotlight, speaker, and siren are operator-controlled with confirmations, and it stays until responders arrive.
- **Indoors**, police and participating building security respond; the drone supports from outside. CCTV integration is purpose-limited and not connected.
- Business model: equipment, dispatch software, training, maintenance, and support sold to **police departments and state governments**. Citizens pay nothing.
- Start with **one jurisdiction and a small approved zone**; measure arrival times, reliability, and benefit.

## Run it

```bash
npm install
npm run dev      # development server
npm run build    # production build
npm test         # build + jsdom smoke & flow tests
```

Demo changes persist in your browser's localStorage; **Settings → Reset demo workspace** restores the sample data.

## Before any operational pilot

- Signed emergency-response integration with police; authenticated operators with audit logs
- Applicable aviation / airspace approvals and site surveys for the coverage zone
- Encryption, data-retention controls, and purpose-limited CCTV access
- Validated ground dispatch, indoor handoff, and fallback workflows

The core promise is **earlier awareness and coordinated support** — a drone can deter and document harm, but cannot guarantee prevention or replace physical intervention.
