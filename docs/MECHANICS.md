# Device mechanics and housing design

Status (2026-10-15): **design study, nothing built yet.** This document turns the owner's notes on the box into a reference design with starting dimensions, mechanisms, materials, sensor placement and mounting options, based on published facts about crows and earlier crow machines. Every dimension is a starting value. Check it with a full-size cardboard or plywood mock-up and with real crows before cutting metal. Figures marked *(est.)* are engineering estimates, not measurements.

## Owner's requirements (notes of 2026-10-15)

- Large enough for crows to land and perch comfortably without the unit tipping over.
- An upper food compartment and a lower waste compartment. Between them sit the perch and the intake tray, with the food window just above, at a height where a crow can easily grab the food.
- Big capacity for waste and food, a spacious landing area, and good stability.
- Plastic, aluminium or painted sheet metal. The body could be green to blend with foliage, or a distinct colour may help crows find the box (to be investigated).
- Intake tray light grey, so objects stand out in photos while dirt does not dominate. *Decided 2026-10-15: a square or rectangular tray in plain grey.*
- Electronics and power bank protected from moisture. A solar panel on the roof later.
- Mounted high enough to deter vandalism, yet easy to reach for emptying waste and refilling food. One idea: a vertical pipe on a standard city litter bin (as in Berlin), with the box on top, so collected caps drop into the bin and the existing collection rounds take them away. Open question: how to refill food high up.
- Open questions: do crows prefer to feed high up or near the ground, and what do they eat?
- The design should fit many urban places: metro stations, bus stops, busy streets, small parks.

## What the design has to respect

### The bird

| Fact | Value | Design consequence |
|---|---|---|
| Hooded crow (*Corvus cornix*, the crow of Berlin and eastern Europe) | 48–54 cm long, wingspan 84–100 cm, 400–600 g ([BTO](https://ociweb.bto.org/learn/about-birds/birdfacts/hooded-crow); [Songbird Survival](https://songbird-survival.org.uk/songbirds/hooded-crow)) | Keep about 50 cm clear on both sides of and above the landing ledge so a crow can land and take off with open wings. Carrion crows are the same size. |
| Load of a landing crow | about 0.6 kg × 3 (landing impact) ≈ 18 N *(est.)* | Negligible for stability. Wind and people matter far more (see "Stability"). |
| Perch grip | Toes should wrap about 2/3–3/4 round a perch; birds of crow size use perches of about 25–40 mm ([VCA](https://vcahospitals.com/noyes/know-your-pet/perches-for-birds); [Windy City Parrot](https://windycityparrot.com/perch-size-recommendations)) | A flat ledge with a round front edge or bar of about 30 mm, with a rough, non-slip surface |
| Foraging style | Mostly on the ground by surface pecking ([Avocetta](https://avocetta.org/articles/vol-22-12-vkb-foraging-behaviour-and-habitat-use-in-corvids-wintering-on-farmlands-in-northern-italy)), but they readily use raised platform feeders ([Bob Vila](https://www.bobvila.com/articles/how-to-attract-crows.md)) and check litter bins; hooded crows were seen diving into bins in a study of Finnish cities ([summary](https://windycityparrot.com/we-studied-the-trash-bin-strategies-of-birds-and-found-this-out/)). Berlin's hooded crows open bins and rip open bags ([Berliner Zeitung](https://www.berliner-zeitung.de/article/88080)). | Height is not a hard limit for the crow. Choose it for safety, service and vandalism (see "Height"). |
| Wariness of new objects | Crows are among the most neophobic corvids. Urban crows approach familiar litter faster than rural ones but are just as wary of truly new objects ([Corvid Research](https://corvidresearch.blog/2016/08/01/hate-new-things-so-do-corvids/)). American crows approached new objects and human food faster near trash cans ([Merz et al. 2025, *Behavioral Ecology*](https://ideas.repec.org/a/oup/beheco/v36y2025i1p1-48..html)). One city feeder took a few weeks before the first crows used it (reader report, same Corvid Research article). | Expect weeks of free feeding before training. Placing the box next to a litter bin may shorten that. Avoid anything that looks like a cage. |
| Vision | Tetrachromatic, of the violet-sensitive type: four colour channels, but not particularly sensitive to UV ([Corvid Research](https://corvidresearch.blog/2020/12/02/crow-curiosities-can-crows-see-uv/)) | Crows see colours at least as well as we do. Colour choice is about recognition and contrast, not about hiding from the crow (see "Colour"). |
| Food | Omnivores: invertebrates, seeds, fruit, carrion, eggs and human scraps ([t-online](https://www.t-online.de/leben/familie/id_71083368/nebelkraehe-steckbrief-des-aasvogels.html)). In one urban crow study about a third of food items were of human origin ([JCU](https://researchonline.jcu.edu.au/88569/)). | See "Food" |

### Lessons from earlier machines

- **Joshua Klein's Crow Box:**
  - Built from 3 mm laser-cut acrylic, with a perch, a food tray and a coin funnel.
  - The food window opens for about 15 s and the bird takes what it can.
  - Training runs in four stages (free food → food on landing → food on deposit with coins provided → food only on deposit). "Training can take a very long time."
  - Recommended food: roasted unsalted peanuts.
  - Sources: [thecrowbox.com](https://thecrowbox.com/); [FAQ](https://thecrowbox.com/wiki/doku.php?id=kit:faq).
- **A bird vending machine for magpies and jackdaws** ([hackaday.io](https://hackaday.io/project/184754/logs)):
  - Screw feeders were abandoned because the dispenser "must never get stuck". A vibrating platform with a 15–30° baffle dispenses 1–2 in-shell peanuts.
  - Steeper baffles and larger peanuts jammed. Tilting the feeder a few degrees off vertical made it less reliable.
  - Moving the food outlet next to the deposit hole helped the birds link deposit and reward.
  - Magpies were reluctant to step onto the platform.
- **Corvid Cleaning (Södertälje, 2022):** a hooded crow puts a piece of litter into a slot and the machine rejects leaves or stones and gives a peanut. The pilot was not scaled up ([case study](https://journals.sagepub.com/doi/10.1177/25166042241296275); [My Modern Met](https://mymodernmet.com/crows-tidy-litter-sweden/)).

## Reference design

A vertical column, from top to bottom: roof, food section, electronics deck, intake chamber with tray, waste section. The crow stands on a ledge at the front, at the level of the intake chamber. Side section, the crow stands on the right:

```
             roof: light-coloured top, 10–15 cm overhang, lookout perch at the back,
             later a solar panel ──────────────────────────────────────────┐
  ┌────────────────────────────────────────────┐                           │
  │ FOOD HOPPER 2–3 L, lockable lid             │═══════════ hood ══════════╗
  │      │ portioner (servo 2)                  │                     PIR in a short tube,
  │      └──► food chute ───────────────────────►  food dish  ◄─ H0+18 cm   looking down
  ├────────────────────────────────────────────┤                           ║
  │ ELECTRONICS DECK, sealed: Pi, power bank,   │                           ║
  │ camera + light looking down through a window│                           ║
  ├────────────────────────────────────────────┤                           ║
  │ dark INTAKE CHAMBER   ◄── inner chute ──────◄  intake slot  ◄─ H0+8 cm  ║
  │       ══╤══  grey tray on servo 1 axle      │                           ║
  │      ╲   V-funnel   ╱                       │══════ landing ledge (H0), 15 cm deep ═══●
  ├────────────────────────────────────────────┤                                   round edge
  │ WASTE BIN 8–10 L, metal, locked door        │
  │ (or a drop pipe into a city litter bin)     │
  └────────────────────────────────────────────┘
          mounting: pole clamp / wall plate / bin adapter / ballast base
```

### Starting dimensions

| Part | Starting value | Reason |
|---|---|---|
| Body | 40 cm wide × 30 cm deep × about 90 cm high, plus the ledge | Room for a 2–3 L hopper, the electronics, a 10 L waste bin and the 18–20 cm camera distance |
| Landing ledge (height H0) | Full width (40 cm) × 15 cm deep, 2–3° forward slope for drainage, non-slip surface, round front edge or bar of about 30 mm | Enough for one crow to walk and turn, or two side by side; nothing around it that looks like a cage |
| Free space round the ledge | About 50 cm to each side and above; no walls or branches right next to it | A wingspan of up to 1 m |
| Intake slot | Centre about 8 cm above the ledge; an opening about 7 × 7 cm behind a tapering outer funnel, sized to the largest object accepted (owner, 2026-10-15: caps and lids up to about 60 mm) | The slot itself turns away larger objects, so no size rule in software is needed. A crow's head (*est.* 4–5 cm wide) fits through such an opening, so the inner chute must keep the beak away from the tray (next row). The funnel tapers, so a head that goes in can always come out. |
| Inner chute | From the slot down at 50–60° to the tray, about 12–15 cm long, smooth | The object lands in the camera view. The chute is longer than a crow can reach with beak and head (*est.* about 10 cm), so the beak cannot reach the tray. |
| Tray | Square or rectangular, plain matte medium grey (owner, 2026-10-15), flat, no rim on the tipping sides; for example a slightly V-shaped trough about 10 × 7 cm that tips about its long axis, so caps roll to its middle line | Seen from above, a round floor in a round tube looked like a cap to the model (empty trays up to 0.99 "bottle cap", [RECOGNITION](RECOGNITION.md)); a plain grey rectangle does not, and caps of every colour stand out on neutral grey. The camera sees only the tray floor, analysed as a fixed area. |
| Camera height above the tray | 18–20 cm, lens focused to that distance | The Camera V2 sees 62.2° × 48.8° ([spec](https://www.thingbits.in/products/raspberry-pi-camera-v2-8mp)). At 19 cm a 12 cm tray fills about 70 % of the frame height. The lens can be refocused down to about 10 cm; an earlier test at 15 cm without refocusing was out of focus. |
| Food dish | Floor about 18 cm above the ledge (to be checked on the mock-up); window 10 × 8 cm; shallow recessed dish 8 × 8 cm sloping to the front, with drain holes | Within easy reach of a standing crow (*est.*) and right above the slot, so deposit and reward sit together, as the magpie machine found |
| Roof overhang | 10–15 cm over the ledge, slot and dish | Keeps rain off the slot, the dish and the PIR, and shades the sensor |
| Food hopper | 2–3 L | About 650 rewards of two peanut kernels *(est.)*; 1–2 weeks at a cap of 50–100 rewards a day |
| Waste bin | 8–10 L, metal | A crown cap takes about 3 cm³ in bulk, a plastic cap 10–15 cm³ *(est.)*: roughly 700–3000 caps |

**The service interval is set by the battery, not by food or waste.** A 20 000 mAh power bank lasts about 1.5 days ([POWER](POWER.md)), food lasts 1–2 weeks and the waste bin months. Until solar power or a lower-power computer arrives, the battery must be quick to swap: put it in a locked drawer, not behind screws.

## Mechanisms

### Intake tray

- Same principle as the bench prototype: a servo tips the tray 85° one way for a reward (YES) or 85° the other way (NO), holds it there for 0.5 s and returns to the level centre ([SERVO](SERVO.md)). **Both sides drop into the same V-shaped funnel and the same waste bin.** Other objects are litter too, and only the food differs.
- **The servo stays outside the wet, dirty chamber:** the axle passes through the chamber wall in a bushing (a plain bearing, stainless steel axle) and connects to the servo with a short coupling.
- **Objects must slide off:**
  - Bench tests showed light objects staying on the tray at 85° with a short pause; caps roll and slide more easily.
  - Use a smooth, low-friction surface (stainless steel, anodised aluminium or a PTFE film) with no rim on the tipping edges.
  - Give the tray an end stop with a hard rubber buffer: hitting it jolts the tray, which shakes a stuck object free.
  - If that is not enough, gear the linkage for 100–110°.
- **Pinch safety:** moving parts sit behind the inner chute, out of a crow's reach.
- **Non-combustible waste path:** people may put anything into an opening in the street, including hot or smouldering items. The tray, funnel and waste bin are metal, and a closed bin starves anything smouldering of air. A metal wall separates the waste from the electronics.

### Food dispenser

The magpie machine's lesson is that the dispenser must never jam. The design therefore uses a **slide portioner**, which shears off one portion and clears itself:

1. A hopper with steep, smooth walls (at least 60° from horizontal) and an outlet at least 3–4 times the size of a food piece, so the food does not bridge (Ø ≥ 50 mm for peanut kernels or kibble).
2. Under the outlet, a flat slide plate (stainless steel or food-safe HDPE) with a pocket the size of one portion (for example Ø 30 mm × 10 mm ≈ 7 cm³). At rest the pocket fills under the outlet.
3. The servo pushes the slide about 40–50 mm. The pocket passes a soft rubber or brush wiper at the shearing edge (a stiff edge would pinch a peanut and jam), then a drop hole, and the portion falls down the chute into the dish.
4. The slide returns and the pocket refills. Food has no other way out of the hopper.

Peanuts are irregular, so test the chosen food for 500 cycles on the bench, counting jams and weighing portions, before field use.

### Food window: open dish, flap optional

**Start with an open, recessed dish under the roof:** it gets food only after a YES. Free feeding in the first training stage also needs an open dish.

**A shutter or flap is worth adding only if leftovers attract pigeons, rats or other birds.** Pigeons and rats cannot deposit caps, so they get food only when a crow leaves some behind. If a shutter is needed:
- It closes only after the PIR has been quiet for several seconds.
- It is slow and low-force, with a soft edge.
- It sits on the same slide as the portioner: it opens as the portion drops and stays open 10–15 s, as Klein's window does.

A part that closes in front of a beak is a welfare risk and must be tested on the bench first. Crows cache food and usually carry rewards away, which keeps the dish empty.

### One servo or two

[HARDWARE](HARDWARE.md) has assumed that one servo drives both routes. With food above the tray that becomes awkward. **Recommendation: two servos.** Servo 1 tips the tray and servo 2 drives the portioner.

| | Two servos (recommended) | One servo with a linkage |
|---|---|---|
| How | Servo 2 on the second hardware PWM channel, GPIO19 (physical pin 35), with `dtoverlay=pwm-2chan,pin=18,func=2,pin2=19,func2=2` instead of today's overlay | A pull cable (Bowden cable, stainless inner, sealed sleeve) from a crank on the tray axle to the slide. At rest the crank arm is at right angles to the cable, so the CCW (reward) stroke pulls about 4 cm with a 4 cm crank, and the CW stroke only slackens the cable. A return spring resets the slide. A spring in the cable end lets a jammed slide give way, so the tray still completes its stroke. |
| Independence | A food jam never stops the tray, and a tray problem never dispenses food | Coupled: needs the spring link above |
| Training stages | Can dispense on landing or freely, without moving the tray | Has to tip the empty tray to dispense (harmless, but odd) |
| Energy | Servo 2 can switch its pulses off between visits, because the slide rests against its stop under the spring, unlike the tray. Practically no extra standby power. | One servo, but it needs more torque, because it also pulls the slide and spring |
| Software | Small change: a second output and a `dispense()` step | None |
| Parts | One more servo and cable | Cable, crank, spring; fiddly to adjust; a cable can freeze |

**Servo choice for the field:**
- Use a standard-size, metal-gear, sealed servo (IP66/67 class) for both. The bench JAMARA micro servo is too weak and not weatherproof.
- Power both from the servo supply, never from the Pi ([POWER](POWER.md)).
- Size the supply for both servos starting at once, or start them one after the other in software.

## Sensors and light

| Sensor | Where | Why |
|---|---|---|
| PIR (HC-SR501) | In the ceiling of the hood above the ledge, in a 3–5 cm tube, looking down at the zone in front of the slot and dish | Fires only when a head is at the slot, not for passers-by. Rain and direct sun stay off the dome ([HARDWARE](HARDWARE.md#limiting-the-trigger-zone-to-about-35-cm)). |
| Camera V2 | In the sealed electronics deck, looking straight down through a glass window at the tray, 18–20 cm below | Inside the dry deck. The Pi's warmth keeps the window from fogging. |
| Light (RGB module or white LEDs) | In the deck next to the camera, angled or behind its own window, so its reflection in the camera window misses the lens | Avoids glare. The chamber must be **dark inside and light-tight except for the slot**: room light reaching the tray changed scores drastically in bench tests ([ALGORITHM](ALGORITHM.md)). |
| Status LED | Visible from below at the back or underside, not from the ledge | For the operator only. A light facing the crow may scare it or attract attention. |

**Later options:**
- A load cell under the ledge (HX711 class), which would detect presence reliably and weigh visitors (crow 400–600 g, pigeon about 300–350 g, magpie and jackdaw lighter), useful for research.
- A distance (time-of-flight) sensor at the slot.
- Fill-level sensors for the waste and food sections.
- A temperature and humidity sensor in the electronics deck.
- Battery voltage and current measurement.

## Weather, heat and cold

**Electronics deck:**
- An IP65 box with cable glands and a pressure-equalising membrane vent, which lets air move without water and prevents condensation from breathing ([Sixfab](https://sixfab.com/product/raspberry-pi-ip65-outdoor-iot-project-enclosure/); [Entaniya camera housing](https://e-products.entaniya.co.jp/en/list/cube-case/waterproof-camera-cases-items/housing-set-for-raspberry-pi-cameras/)).
- A pack of desiccant inside.
- Every opening faces down.

**Sun:**
- A light-coloured roof top with an air gap underneath (a double roof). A dark green roof in summer sun gets much hotter.
- Lithium batteries age fast when hot, and charging is usually limited to about 5–45 °C ([summary](https://backuppowerhub.com/power-station-freezing-temperatures-charging-storage/)).

**Cold:**
- Batteries lose capacity in the cold.
- **Charging a lithium battery below 0 °C damages it** (lithium plating) ([REDARC](https://us.support.redarcelectronics.com/hc/en-us/articles/13856244101007-Why-you-should-not-charge-a-lithium-battery-below-0-C-or-32-F)). A solar charger must therefore cut off below about 0–5 °C, or the battery needs a heated, temperature-aware charging circuit.
- Most power banks have no such protection.

**Rain and snow:**
- The ledge slopes forward and drains.
- The dish has drain holes.
- The slot sits under the overhang, and the chute slopes towards the tray, so water ends up in the waste bin.
- **Keep the waste dry:** wet waste smells and corrodes, and drink residue attracts wasps; the bin stays closed and must not drain onto the ground.

## Food

- **What to give:** unsalted peanuts (kernels or in shell) and dry dog or cat kibble are nutritious and easy for crows to take. Klein's Crow Box recommends roasted unsalted peanuts and lists nuts, eggs, meat scraps and pet kibble ([FAQ](https://thecrowbox.com/wiki/doku.php?id=kit:faq)). Do not give bread (little nutrition) or anything salty (salt harms birds).
- **For the dispenser,** uniform, dry, free-flowing pieces work best: kibble, or peanut kernels. In-shell peanuts need a much larger outlet and jam more easily. Use human-grade peanuts, because low-grade bird peanuts can carry mould toxins.
- **Hygiene:** a sealed metal hopper, food kept dry, and old food replaced at each service. Rats chew through plastic, so the hopper sits inside the metal housing.
- **Welfare:** a daily reward limit and a choice of food reviewed with an ornithologist or wildlife vet ([MISSION](MISSION.md#3-animal-welfare)).

## Colour and surfaces

- **Body:** dark green (for example RAL 6005 moss green or RAL 6009 fir green, common for park furniture) blends in and makes the box less of a target. No study was found on whether a feeder's colour helps crows find it. Crows find food sites by learning places and by watching other crows and people, so a familiar location (next to a bin) probably matters more than colour.
- **A recognisable mark:** use the same high-contrast mark on every box, such as a white band round the ledge, so crows that know one box may recognise another. This is a research question ([MISSION](MISSION.md#2-behaviour-and-learning)).
- **No mirror-like surfaces:** crows are often reported pecking at their own reflection in car mirrors and windows. Use matte finishes and keep the camera window out of view.
- **Tray: plain matte medium grey** (owner, 2026-10-15). Caps come in every colour (red, blue, green, yellow, white, metallic), so a neutral grey gives all of them contrast; a coloured tray would hide caps of its own colour. Matte, or the light reflects off it. The final check is the grey-card test on the bench ([ROADMAP](ROADMAP.md)).
  - Whatever the colour, the finish must be matte, or the LED will reflect off it.

## Materials

| Use | Recommended | Notes |
|---|---|---|
| First mock-up and bird trials | Plywood (painted) or HDPE sheet, with a metal waste insert from day one | Cheap and easy to change. HDPE is UV-stabilised, food-safe and needs no paint. |
| Field body | Powder-coated aluminium, 2–3 mm, a seawater-resistant grade such as EN AW-5754 | Light, does not rust, recyclable |
| Alternative field body | Hot-dip galvanised and powder-coated steel ("duplex"), the usual finish for city furniture | Heavy (harder to steal and more stable) and robust. Painted steel without galvanising rusts at the first scratch. |
| Tray, funnel, waste bin | Stainless steel or aluminium | Must not burn; smooth so objects slide off |
| Food hopper and slide | Stainless steel or food-safe HDPE | Food contact |
| Small internal parts (chute, camera mount, portioner prototype) | 3D-printed ASA or PETG | Not PLA: it softens in the sun |
| Fasteners and locks | Stainless security screws (pin-Torx), one key for all service doors | Vandalism |
| Coating | Anti-graffiti clear coat on the body | Easy cleaning |

## Stability and mounting

The finished box weighs about 10–14 kg *(est.: 1.5–2 m² of 2 mm aluminium plus electronics, food and waste)*.

**Wind, not crows, decides the mounting.** At 25 m/s (a storm), the wind on the front (0.36 m²) is about 170 N. Acting about 0.45 m above the base, that tips the box with about 76 N·m. A free-standing 12 kg box only resists about 18 N·m, so it would already tip in a strong breeze *(est.)*. **The box must be bolted or clamped down, or stand on a heavy base.**

The ledge must also survive a person leaning on it or a child climbing it (design for about 1 kN).

| Mounting | Where | Notes |
|---|---|---|
| Pole clamp (60.3 or 76.1 mm posts, as used for road signs) | Bus stops, streets, parks | Most flexible. On a 60 mm post the storm load is no problem *(est.)*. A smooth pole or a cone baffle below the box stops rats from climbing. |
| Wall plate | Station entrances, walls in courtyards | Keep the free space round the ledge |
| Adapter on a city litter bin | Next to bins in parks and squares | See below |
| Ballast or anchored base | Temporary pilots, private ground | Needs about 50 kg ballast or ground anchors *(est.)* |

### Height

- Crows feed on the ground and on raised platforms, so the choice of height is about **safety, service and vandalism**.
- **Recommendation: ledge at 1.6–1.9 m.**
  - An adult can reach the food lid, the waste door and the battery drawer from the ground (reach about 2.1–2.3 m).
  - The box is above the reach of children and dogs, and the crow stands above most passers-by.
  - At this height the box still must be vandal-proof, because adults can reach it.
- **Above about 2.5 m,** use a tilting (hinged) mast that is lowered for service, as is done for some street lights and cameras. Every visit then needs a key and a few minutes, but casual vandalism is almost impossible.

### The litter-bin idea (Berlin)

**For:**
- Berlin's city cleaning service (BSR) looks after roughly 21 000–24 000 orange litter bins of about 70 L ([Berlin parliament, 2023](https://pardok.parlament-berlin.de/starweb/adis/citat/VT/19/SchrAnfr/S19-15593.pdf); [Berliner Mieterverein](https://www.berliner-mieterverein.de/?p=13633)).
- Caps dropping into a bin join the existing collection rounds, so no new waste route is needed.
- Bins are places where crows already search for food and where people drink outdoors.
- Crows approach new things faster near trash cans (Merz et al. 2025).

**Against:**
- The bin belongs to the BSR, so this needs their consent. Do not weld onto city property: use a clamp on the bin's post.
- The pipe (≥ 75 mm, straight, smooth, closed at the top by the box) must end over the bin opening without getting in the way of the bag change.
- Rain must not run down the pipe into the electronics.
- Food and battery still need a service visit: either the BSR crew does it on their rounds (a change to their work), or a separate route.

**Recommendation:** propose it to the BSR as a pilot partnership once the box works in a private courtyard. Mount it on a post clamp at the bin, ledge at 1.6–1.9 m, with a short drop pipe into the bin.

## Rules in Berlin (to confirm before any public installation)

- **Feeding:**
  - Berlin's hunting law forbids feeding huntable species (§ 34(4) Landesjagdgesetz, [berlin.de](https://www.berlin.de/lb/tierschutz/wildtiere/artikel.1379720.php)).
  - Crows are **not** huntable in Berlin. The federal list (§ 2 Bundesjagdgesetz) includes the raven but no crows, and Berlin adds only mink, raccoon dog, nutria and raccoon ([Berlin regulation, 22 August 2025](https://www.parlament-berlin.de/ados/19/IIIPlen/vorgang/verordnungen/vo19-280.pdf)).
  - The federal list does include gulls, wild pigeons (such as wood pigeons) and wild ducks. Another reason to give food only after a YES with the crow present.
  - Some districts ban feeding any wild animal in certain parks: in Mitte, the Großer Tiergarten, the park at Plötzensee, the Volkspark Rehberge and parts of the Luisenstädtischer Kanal ([berlin.de](https://www.berlin.de/ba-mitte/nicht-fuettern)). Avoid such parks.
- **Public space:** placing an object on public land needs a special-use permit (Sondernutzungserlaubnis) from the district office. Unauthorised use can be fined up to €10 000 ([berlin.de, Mitte](https://www.berlin.de/ba-mitte/politik-und-verwaltung/aemter/strassen-und-gruenflaechenamt/strassenverwaltung/artikel.936761.php); [LTO](https://www.lto.de/recht/nachrichten/n/vg1k34218-vg1k9819-vg-berlin-geldautomat-sondernutzung-gemeingebrauch-strassenrecht)). The first trials therefore belong on private ground (a courtyard or garden, with the owner's consent).
- Crows are protected as European wild birds under nature-conservation law: nothing may capture, hold or harm them.
- This is research, not legal advice. Confirm with the district office and the Berlin hunting authority before a public pilot.

## Fitting into different places

| Place | Caps | Crows | Risks | Fit |
|---|---|---|---|---|
| Bus and tram stops | Some | Often nearby | Crowds, vandalism, people "feeding" the box with caps | Pole clamp on the stop's post; ledge facing away from the waiting area |
| Metro entrances | Some | Fewer in covered areas | Crowds, little space | Wall plate outside the entrance, under open sky |
| Busy streets | Many | Present | Traffic noise, little space | On a litter bin or lamp post |
| Small parks | Many (people drinking outdoors) | Many | Feeding bans in some parks; dogs | Pole at 1.6–1.9 m near a bench or bin, outside banned parks |

**People will use it too.** People carry caps and may drop them into the slot themselves. That is still litter removed, but food is then dispensed with no crow present. The daily reward limit keeps this in check. A small sign explains the project.

## Training stages and what the mechanics must allow

| Stage (after Klein) | Mechanical need | Software need (not yet implemented) |
|---|---|---|
| 1. Free food | The dish can be filled by hand, or the dispenser runs on a timer | Reward mode `free` |
| 2. Food on landing | Dispense when the PIR fires, without a cap | Reward mode `landing` |
| 3. Caps placed on the ledge to give the idea | A small, shallow tray on the ledge so placed caps don't blow away | |
| 4. Food only for a cap | Today's production logic | Reward mode `cap` (current), with a daily reward limit |

## Build and test plan

1. **Full-size mock-up** in cardboard or plywood: check the reach to the slot and dish, the ledge size and the free space. Then free feeding with a camera in a private courtyard, with two ledge heights to compare.
2. **Intake bench:** chamber, grey tray, V-funnel and metal bin. Set the camera height and focus, run the grey-card test, and check that objects slide off with the end-stop buffer.
3. **Dispenser bench:** hopper and slide portioner with the chosen food, 500 cycles, counting jams and weighing portions. Then the second servo channel and a `dispense()` step in software.
4. **Weather tests:** a hose test of the electronics deck; dispenser and servo in a freezer overnight; temperature in the deck under summer sun.
5. **Private field pilot** through the four training stages, with visit logs and photos; then the BSR or district conversation.

## Open questions

- How high do crows actually prefer the ledge? (Test two heights in step 1.)
- Which threshold works best on the grey tray, indoors and outdoors? (Grey-card test.)
- Does a standard mark help crows recognise other boxes?
- Peanut kernels or kibble: which jams less and is taken faster?
- Is a food shutter needed, or do crows always take the whole portion?
- Solar: a 60 W panel for Berlin winters ([POWER](POWER.md)) is bigger than the 40 × 30 cm roof. Either use a separate panel on the pole, or first cut the consumption (night shutdown, Raspberry Pi Zero 2 W).
