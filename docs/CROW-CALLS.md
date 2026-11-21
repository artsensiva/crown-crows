# Crow calls: should the box play "crow phrases"? (research, 2026-11-21)

Question: is there research on what crows "say", are there ready phrases in crow language that would help to train them, and should the box get a speaker?

**Short answer: no ready phrases exist, and a speaker with recorded crow calls is not recommended now.** If a sound is wanted at all, the evidence-based use is a plain, neutral sound at the moment of the reward (like a clicker), not crow speech. Method: a web search of papers, preprints and news (not full-text reading of every paper; where only a summary was seen, it is said so).

## What is known about crow calls

- **Calls are being mapped, not translated.** A 2025 field study put 52 lightweight tags (MiniDTAG) on wild, cooperatively breeding carrion crows in northern Spain and collected over 127,000 vocalisations, with a machine-learning classifier sorting them from long-distance calls to quiet murmurs. Many calls are quiet and at close range inside the family; the project states that decoding *meaning* is the goal and still at an early stage ([Earth Species Project, Dec 2025](https://earthspecies.org/2025/12/15/unlocking-avian-secrets-how-tiny-biologgers-are-revealing-the-hidden-communication-of-carrion-crows/); [Animal Cognition](https://link.springer.com/article/10.1007/s10071-025-02018-0); [Mongabay, May 2026](https://news.mongabay.com/2026/05/from-caws-to-code-ai-helps-decrypt-animal-communication/)).
- **Function by context** (2026 preprint, 24 groups): quiet close-range calls seem to coordinate chick care by announcing nest visits ([bioRxiv](https://www.biorxiv.org/content/10.64898/2026.04.02.715916v1.full)). A systematic review of 130 corvid studies finds that calls carry information about predators and food and serve group cohesion ([Animal Behaviour review](https://www.sciencedirect.com/science/article/pii/S0003347224003841)). An older thesis found most carrion crow calls on a continuum of loud calls rather than clearly separate "words" ([University of Leicester](https://figshare.le.ac.uk/articles/thesis/Aspects_of_vocal_communication_in_the_carrion_crow_Corvus_corone_corone_/10162910)).
- **Crows control their voice.** Three carrion crows were trained to produce one to four calls on cue, planning the sequence before calling ([Liao, Brecht, Veit, Nieder, Science 2024](https://uni-tuebingen.de/en/university/news-and-publications/press-release/crows-can-deliberately-plan-how-many-calls-to-make/)). That says something about their minds, not about a vocabulary we could use.
- **Call structure follows regularities** (longer sequences contain shorter calls, Menzerath's law; [Vocal efficiency in crows, 2025](https://pubmed.ncbi.nlm.nih.gov/40742461/)), and the scolding response to a dangerous person or a dead crow is *learned* and spreads between crows (work of the Marzluff lab, American crows: [one](https://pmc.ncbi.nlm.nih.gov/articles/PMC3234554), [two](https://pmc.ncbi.nlm.nih.gov/articles/PMC4417708)); one site saw it spread over at least 1.2 km in five years.

## Does playing crow calls attract or train wild crows? Mixed evidence

| Call played | Result (as far as the sources show) |
|---|---|
| American crow food-area calls (short calls near a big food source) | Playback did not make crows find food more often; a mildly aggressive response ([Animal Behaviour 2019, abstract](https://www.sciencedirect.com/science/article/abs/pii/S0003347219300363)) |
| Crow assembly calls | Wild crows gathered at the speaker in about a quarter of trials (figure quoted in a secondary source, [Corvid Research blog](https://corvidresearch.blog/2019/03/14/crow-vocalizations-part-i-new-science/); original not checked) |
| Raven "haa" food calls | Ravens are drawn strongly, and the response depends on who the caller is ([raven study, PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4289921/)) |
| Alarm or dead-crow related calls | Crows respond with mobbing, avoid the place and learn from one exposure ([Swift and Marzluff](https://pmc.ncbi.nlm.nih.gov/articles/PMC4417708)) |

Nothing found shows that a recorded "phrase" makes crows learn *this box*. A search for other devices found one precedent: the 2008 crow vending machine, whose claims corvid researchers disputed ([NPR](https://www.npr.org/2008/03/04/87878028/inventor-trains-crows-to-find-money); [Kottke](https://kottke.org/09/04/no-vending-machine-for-crows)), so it is no evidence either way.

## What crows do learn quickly: arbitrary sounds tied to rewards

Captive crows learn sound-to-reward and sound-to-picture associations quickly, including a short feedback sound followed by a feeder (Nieder lab studies, for example [Moll and Nieder 2015](https://homepage.uni-tuebingen.de/andreas.nieder/Moll,%20Nieder%20%282015%29%20CurrBiol.pdf), a short sound marking correct trials with a feeder reward in the search summaries; full texts not read). Those were laboratory birds; a neutral chime played when the reward drops is an *inference* for wild crows, not a tested result. It needs no crow recording and cannot be mistaken for an alarm.

## Risks of playing recorded wild-bird calls

- **Alarm, scolding or dead-crow calls could teach crows to avoid the box** (the learned scolding above spreads through a population). Never play them.
- Ethics guidance discourages playback near breeding birds: Audubon and the American Birding Association advise limiting it, BirdLife Australia suggests no more than three 30 s bouts in 5 minutes at one site ([Audubon](https://www.audubon.org/magazine/why-photographers-should-reconsider-using-playback-field); [BirdLife Australia guidelines](https://direct.birdlife.org.au/documents/POL-Ethical-Birding-Guidelines.pdf)). A food box is not a territorial lure, but a call played all day near nests is the situation those guidelines warn about. Neighbours and local rules about noise also apply.
- A speaker is more code, more parts and another current peak on a supply that already shows a dip at every servo stroke. Audio was switched off on the Pi on 21 Nov (`dtparam=audio=off`, [HISTORY](HISTORY.md)); a speaker would need it back on or a small I2S amplifier.

## Recommendation

1. **Do not install a speaker with crow phrases now.** There is no validated vocabulary, the evidence for attraction is mixed, and the risks (alarm calls, noise, stress to nesting birds) and the cost in code and energy are real.
2. **If the owner wants to try a sound, run a small controlled test:** a short neutral chime (not a crow sound) at the moment of the reward, low volume, a very small amount of code, on alternate weeks (sound on / off), and compare the number of visits and returning crows per day from the visit log. Keep it only if visits rise.
3. **Only after that, and only if wanted,** try one recorded food-associated or contact call from the same species, in the same on/off design, never alarm or mobbing calls.
4. Better returns for the training are probably elsewhere: food placement, the 25 mm intake height, and time (the 2008 precedent and the learning literature agree that patient shaping with food matters more than sound).
