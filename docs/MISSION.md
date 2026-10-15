# Mission and research directions

## Mission

**Mutual aid between birds, nature and people: crows help clean the city, and the city rewards them.**

Crows are among the most intelligent animals and live wherever people drop litter. Crown Crows offers them a fair trade: bring a bottle cap or lid, get a small food reward. Every cap that goes into the box is one fewer in the gutter, the park or the river, and every reward is food earned rather than scavenged from waste. The device is meant to be cheap, autonomous, open and humane: it runs on a small battery-powered computer, needs no network, recognises caps with an off-the-shelf model, and puts the birds' well-being first.

The name plays on the *crown cap* (German *Kronkorken*), the steel cap of beer and lemonade bottles, and on crowning the crows for a good deed: an invitation to people to honour the birds that help their city.

## Birds first: why the project changed course

An earlier version of this device was built around a kind of litter that, we later realised, could harm the birds carrying it. We had focused on the technology and underestimated the risk to the birds. That was a significant mistake. We withdrew the design and rebuilt the project around objects that are safe for crows. Their well-being now comes first, followed by nature and people.

Bottle caps and lids were chosen because:
- they are **not toxic**, unlike many other kinds of litter;
- they are **too large to swallow**: a steel crown cap is about 32 mm across and 6 mm high ([crown cap dimensions](https://patents.google.com/patent/US20160107802A1/en)), plastic drink caps fit a 28 mm bottle neck ([Pelliconi](https://www.pelliconi.com/product/plastic-caps-28mm-1881/)), lids are larger still;
- crows can handle flat, round objects: Joshua Klein trained crows to deposit coins ([NPR](https://www.npr.org/2008/03/04/87878028/inventor-trains-crows-to-find-money)).

Remaining risks to watch: broken caps and loose sealing rings, sharp edges of bent crown caps, and drink residue attracting wasps (the waste bin stays closed).

## Why bottle caps and lids

- **Common litter.** Beverage bottles and their caps and lids are among the items most often found polluting Europe's beaches ([Packaging News, on the EU impact assessment](https://www.packagingnews.com.au/sustainability/push-for-tethered-bottle-caps-to-reduce-waste)).
- **Plastic caps** break down into microplastics. Since 3 July 2024, plastic caps on drink containers up to 3 litres must stay attached to the container in the EU ([EU Directive 2019/904, Art. 6](https://www.aimplas.net/blog/eu-mandates-attaching-caps-plasti-bottles-containers)), so loose plastic caps will become rarer.
- **Steel crown caps** from beer and lemonade are unaffected by that rule and very common where people drink outdoors, for example in Berlin's parks. Collected steel is valuable to recycle.

## Prior work

| Project | What it did | Status |
|---|---|---|
| Joshua Klein, *Crow Box* (USA, about 2008) | A vending machine that taught crows in stages to deposit coins for peanuts ([NPR](https://www.npr.org/2008/03/04/87878028/inventor-trains-crows-to-find-money); [thecrowbox.com](https://thecrowbox.com/)) | Open research kit |
| Ruben van der Vleuten and Bob Spikman, *Crowbar* (Netherlands, 2017) | A machine concept that recognised deposited litter with a camera and released food | Design concept |
| Christian Günther-Hanssen, *Corvid Cleaning* (Sweden, 2022) | A pilot in which wild crows deposit litter in a machine that rejects other objects and dispenses food | Pilot; not known to have scaled |

**What Crown Crows adds:** a fully documented, open build on a Raspberry Pi 3; recognition that runs entirely on the device without network, cloud or custom training; measured timings and a self-test on the device; and an explicit focus on battery operation and bird welfare.

## What science says about crows trading

- Ravens and carrion crows learn to exchange tokens for food, and ravens can keep a token and trade it hours later ([PMC3297375](https://pmc.ncbi.nlm.nih.gov/articles/PMC3297375)). Trading an object for food is within their abilities; the open questions are how quickly wild urban crows learn it from a machine, and how the habit spreads.
- Klein's staged training (food freely available → food for a deposited object → objects scattered around) is the established starting point for a training protocol.

## Research directions

Each direction lists why it matters and a concrete first step. They are options, not commitments.

### 1. Recognition
- **Tray and threshold.** Set on photos of the grey tray; whether "jar lid" joins the cap descriptions ([RECOGNITION](RECOGNITION.md)).
- **A fast, small model trained on our own photos**, if the zero-shot model is not enough: a small decision layer on top of the current model, trained on a few hundred labelled photos of our own tray.
- **Visitor identification.** Distinguish crows from pigeons, gulls, magpies or people, to log who uses the box and to study learning.

### 2. Behaviour and learning
- **Training protocol** and a device that trains crows step by step (version 2, [ROADMAP](ROADMAP.md)).
- **Reward schedule.** Fixed reward per cap versus occasional rewards; how much food per cap keeps the trade attractive without making crows dependent.
- **Learning curves from the log.** Visits per day, share of YES, time between visits.

### 3. Animal welfare
- **Food.** A suitable reward (for example unsalted peanuts or dry pet kibble), never bread or salty food; feeding wild crows can change their behaviour and create dependence. *First step:* consult an ornithologist or wildlife vet.
- **Daily reward limit.** Limit rewards per box and day so the box supplements rather than replaces natural foraging.
- **Safe objects.** Watch for broken caps, sealing rings and sharp edges; observe whether crows start tearing caps off bottles in bins and scattering the bin contents.
- **Placement and hygiene.** Away from traffic, easy to clean, no pinch points, food and waste strictly separated; local rules followed ([MECHANICS](MECHANICS.md#rules-in-berlin-to-confirm-before-any-public-installation)).

### 4. Environmental impact
- **Count caps.** Every YES is a cap or lid removed; the log already records them.
- **Recycling.** Steel caps can be separated with a magnet; a later mechanism could sort steel and plastic.

### 5. Energy and autonomy
- Battery life, solar charging, low-power hardware and waking only on motion: see [POWER](POWER.md).

### 6. Connectivity
- Statistics on a phone nearby without draining the battery (Bluetooth Low Energy, or Wi-Fi only on demand): see [POWER](POWER.md#phone-access-to-statistics-feature-to-investigate).

### 7. Mechanics and robustness
- Reference design for the housing, tray, food dispenser, sensors, materials and mounting, with its open questions: [MECHANICS](MECHANICS.md).
- A tighter trigger zone for the PIR ([HARDWARE](HARDWARE.md#limiting-the-trigger-zone-to-about-35-cm)), or a distance sensor or infrared light barrier at the opening, which would also detect cold objects.

### 8. Open hardware and citizen science
- A reproducible kit with parts list and instructions, data sharing between boxes, and pilots with cities and their cleaning services.

## Principles

- Birds first: no object or mechanism that can harm them; welfare questions are settled with specialists before field use.
- No personal data or private photos are published.
- Improved bird health is a hope, not a claim; it has to be studied.
