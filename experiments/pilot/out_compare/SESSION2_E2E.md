# Session 2 end to end: selection, narrative and dialogue

Share 0.5, total 12, AC seed 42, CC variant `nearest`, all 162 session-2 events, NCD. Generation: the game's two steps with the existing prompts (`prompts/narrative.txt`, `prompts/dialogue_from_narrative.txt`) and model `gemini-3.5-flash-lite`, no cast block. **original** is what the game does today; **provenance** scores each session-1 dialogue line through the logs it was generated from; **provenance + memory block** uses the same pool and prompt, but gives the earlier-session dialogue lines to the LLM in a separate block labelled as memories.

Things to check (author's judgement):

1. **Selection:** are the RC's events plausibly connected to the session-1 dialogue lines they're linked to?
2. **Narrative:** does it pick up what happened in session 1, and does it read well?
3. **Dialogue:** is it good dialogue, and does it refer back to session 1 naturally?

## Original

### Pool (as the LLM receives it, oldest first)

| channel | link | description |
|---|---|---|
| RC · dialogue line | S110 | Odette 'Odette' O'Neill said 'Stench, I watched the far treeline for more raiders.' |
| AC |  | Boyd watching for targets. |
| AC |  | Stench, Hunter is fully healed. |
| AC |  | Boyd is wandering around in a psychotic state. This happened because of poor mood. The final straw was: Awful barracks |
| AC |  | Stench leading Papyrus to wooden pen marker. |
| AC |  | Stench missed the tortoise. |
| AC |  | Stench hauling silver x500 to Stockpile zone 1. |
| RC · event | linked to S110 | Odette is no longer on an insulting spree against Stench, Hunter. |
| RC · event | linked to S110 | Odette missed Stench with a beat from her left fist. |
| RC · event | linked to S110 | Stench missed Odette with a smash from her left fist. |
| RC · event | linked to S110 | Odette attempted to hit Stench, but hesitated at the last second. |
| RC · event | linked to S110 | Stench flailed at Odette with her left fist, but stumbled at the last second. |

### Narrative

Tensions frayed within the colony as the bitter realities of frontier life set in. Driven to a psychotic break by the squalid, awful conditions of the barracks, the aging civil servant Dillon Boyd began wandering in a daze. Meanwhile, the psychological strain bled into interpersonal conflicts; Odette O’Neill’s frayed nerves culminated in a verbal tirade against the young hunter Lidia 'Stench' Schmitt. 

The heated exchange quickly escalated to physical blows. Odette lashed out at Lidia, sparking a chaotic and clumsy brawl between the two friends. Despite throwing punches, both combatants repeatedly stumbled and hesitated, missing their marks in the disorganized scuffle. Amidst the internal turmoil, routine survival persisted: Lidia secured livestock, hauled silver supplies, and finally returned to hunting once her wounds fully healed.

### Dialogue

```json
[
  {
    "colonist": "Lidia 'Stench' Schmitt",
    "line": "[N], I swear Odette just lost her mind completely back there.",
    "reported": "Stench said I swear Odette just lost her mind completely back there.",
    "reply": "The stress of this place is getting to all of us."
  },
  {
    "colonist": "Lidia 'Stench' Schmitt",
    "line": "[N], at least the silver is hauled and the beasts are fed now.",
    "reported": "Stench said At least the silver is hauled and the beasts are fed now.",
    "reply": "Good work keeping up with chores despite everything."
  },
  {
    "colonist": "Lidia 'Stench' Schmitt",
    "line": "[N], I'm just glad my ribs healed up so I can get back to hunting.",
    "reported": "Stench said I'm just glad my ribs healed up so I can get back to hunting.",
    "reply": "Watch yourself out there in the wilderness alone."
  },
  {
    "colonist": "Dillon Boyd",
    "line": "[N], everything is just falling apart around us in these awful barracks.",
    "reported": "Dillon said Everything is just falling apart around us in these awful barracks.",
    "reply": "Try to get some rest, we can fix things up tomorrow."
  },
  {
    "colonist": "Dillon Boyd",
    "line": "[N], my head is still spinning from wandering around in a daze.",
    "reported": "Dillon said My head is still spinning from wandering around in a daze.",
    "reply": "Drink some water and sit down for a minute."
  },
  {
    "colonist": "Dillon Boyd",
    "line": "[N], I can't even look at anyone without getting nervous lately.",
    "reported": "Dillon said I can't even look at anyone without getting nervous lately.",
    "reply": "Just take a deep breath and ignore the others for now."
  },
  {
    "colonist": "Odette O'Neill",
    "line": "[N], I don't know why I snapped at Lidia like that.",
    "reported": "Odette said I don't know why I snapped at Lidia like that.",
    "reply": "Tempers flare when living in cramped quarters for too long."
  },
  {
    "colonist": "Odette O'Neill",
    "line": "[N], we looked ridiculous stumbling around throwing punches at each other.",
    "reported": "Odette said We looked ridiculous stumbling around throwing punches at each other.",
    "reply": "At least neither of you did any real damage."
  },
  {
    "colonist": "Odette O'Neill",
    "line": "[N], these dark walls are really starting to suffocate me.",
    "reported": "Odette said These dark walls are really starting to suffocate me.",
    "reply": "We can spend some time outside once the weather clears."
  }
]
```

Keyword check (session-1 terms appearing; a crude indicator, not a judgement): narrative: none; dialogue: none.

## Provenance

### Pool (as the LLM receives it, oldest first)

| channel | link | description |
|---|---|---|
| RC · dialogue line | S104 | Lidia 'Stench' Schmitt said 'Boyd, I had those fifty-six steel beams stashed before the grizzly settled in.' |
| RC · dialogue line | S111 | Odette 'Odette' O'Neill said 'Stench, those gazelles were grazing amid the chunks of the downed spacecraft.' |
| RC · dialogue line | S112 | Odette 'Odette' O'Neill said 'Boyd, a grizzly at camp's edge was trouble waiting to happen.' |
| AC |  | Boyd watching for targets. |
| AC |  | Stench, Hunter is fully healed. |
| AC |  | Boyd is wandering around in a psychotic state. This happened because of poor mood. The final straw was: Awful barracks |
| AC |  | Stench leading Papyrus to wooden pen marker. |
| AC |  | Stench missed the tortoise. |
| RC · event | linked to S104 | A(n) grizzly bear standing. |
| RC · event | linked to S111 | A(n) gazelle consuming grass. |
| RC · event | linked to S104 | Stench hauling steel x18 to Stockpile zone 1. |
| AC |  | Stench hauling silver x500 to Stockpile zone 1. |

### Narrative

Life on the frontier tested the colonists' endurance. Amid salvaged spacecraft wreckage and grazing gazelles, the settlement bustled with resource management. Lidia "Stench" Schmitt secured vital steel beams and silver reserves before a dangerous grizzly bear established its territory near the camp's edge. 

The harsh environment and dismal living conditions in the awful barracks took a severe toll on Dillon Boyd, whose nerves finally snapped, driving him into a psychotic wandering state. Meanwhile, Lidia busied herself tending to the local fauna, corralling an animal named Papyrus and hunting unsuccessfully, all while continuing to haul supplies and maintain the colony's fragile routine under the watchful shadow of the local wildlife.

### Dialogue

```json
[
  {
    "colonist": "Lidia 'Stench' Schmitt",
    "line": "[N], that bear's getting way too close to the silver stash.",
    "reported": "Stench said that bear's getting way too close to the silver stash.",
    "reply": "I'll grab my rifle and keep an eye on it."
  },
  {
    "colonist": "Lidia 'Stench' Schmitt",
    "line": "[N], I spent all morning trying to corral Papyrus out in that heat.",
    "reported": "Stench said she spent all morning trying to corral Papyrus out in that heat.",
    "reply": "At least the beast finally went where you wanted."
  },
  {
    "colonist": "Lidia 'Stench' Schmitt",
    "line": "[N], my hunt didn't yield a thing out there today.",
    "reported": "Stench said her hunt didn't yield a thing out there today.",
    "reply": "Don't worry about it, we still have some rations left."
  },
  {
    "colonist": "Dillon Boyd",
    "line": "[N], these awful barracks are driving me completely insane.",
    "reported": "Dillon said these awful barracks are driving him completely insane.",
    "reply": "We are all struggling with the living conditions right now."
  },
  {
    "colonist": "Dillon Boyd",
    "line": "[N], my nerves just finally snapped out in the yard.",
    "reported": "Dillon said his nerves just finally snapped out in the yard.",
    "reply": "Just try to take a deep breath and rest for a bit."
  },
  {
    "colonist": "Dillon Boyd",
    "line": "[N], I don't know how much longer I can handle this frontier life.",
    "reported": "Dillon said he doesn't know how much longer he can handle this frontier life.",
    "reply": "Hang in there, we'll get through this together."
  },
  {
    "colonist": "Odette O'Neill",
    "line": "[N], Dillon's been wandering around in a daze since his breakdown.",
    "reported": "Odette said Dillon's been wandering around in a daze since his breakdown.",
    "reply": "Someone really needs to go make sure he doesn't hurt himself."
  },
  {
    "colonist": "Odette O'Neill",
    "line": "[N], those steel beams from the wreckage took forever to haul back.",
    "reported": "Odette said those steel beams from the wreckage took forever to haul back.",
    "reply": "They'll be useful once we finally start expanding the rooms."
  },
  {
    "colonist": "Odette O'Neill",
    "line": "[N], that grizzly bear is still lingering right by the camp edge.",
    "reported": "Odette said that grizzly bear is still lingering right by the camp edge.",
    "reply": "Stay inside and keep the doors bolted tight until it leaves."
  }
]
```

Keyword check (session-1 terms appearing; a crude indicator, not a judgement): narrative: grizzly, gazelle, spacecraft, steel, papyrus; dialogue: grizzly, steel, papyrus.

## Provenance + memory block

Same pool as *provenance*. What the LLM receives as its input logs:

```
Earlier sessions (things the colonists said in a previous session; these are memories and background, not events happening now):

Lidia 'Stench' Schmitt said 'Boyd, I had those fifty-six steel beams stashed before the grizzly settled in.'[x1][V]

Odette 'Odette' O'Neill said 'Stench, those gazelles were grazing amid the chunks of the downed spacecraft.'[x1][V]

Odette 'Odette' O'Neill said 'Boyd, a grizzly at camp's edge was trouble waiting to happen.'[x1][V]

This session (events in temporal order):

Boyd watching for targets.[x1][V]

Stench, Hunter is fully healed.[x1][V]

Boyd is wandering around in a psychotic state. This happened because of poor mood. The final straw was: Awful barracks[x1][V]

Stench leading Papyrus to wooden pen marker.[x1][V]

Stench missed the tortoise.[x1][V]

A(n) grizzly bear standing.[x153][V]

A(n) gazelle consuming grass.[x1][NV]

Stench hauling steel x18 to Stockpile zone 1.[x1][V]

Stench hauling silver x500 to Stockpile zone 1.[x1][V]
```

### Narrative

Life in the frontier colony remained tense as local wildlife—including grazing gazelles and a persistent grizzly bear—wandered near the settlement. The strain finally broke Dillon Boyd, who slipped into a wandering psychotic state driven by the abysmal conditions of their shared barracks. 

Amid the psychological turmoil, daily survival continued. Lidia 'Stench' Schmitt successfully guided an animal to the wooden pen and secured valuable stockpiles, hauling eighteen steel beams and five hundred silver units to safety. While a recent hunting attempt on a tortoise missed its mark, Hunter made a full recovery, offering the beleaguered colonists a much-needed glimmer of stability.

### Dialogue

```json
[
  {
    "colonist": "Lidia Schmitt",
    "line": "[N], I got those steel beams and silver hauled inside before things got any worse.",
    "reported": "Stench said I got those steel beams and silver hauled inside before things got any worse.",
    "reply": "Thank goodness for that, we really needed the extra funds."
  },
  {
    "colonist": "Lidia Schmitt",
    "line": "[N], that grizzly bear is getting way too close to the barracks for comfort.",
    "reported": "Stench said that grizzly bear is getting way too close to the barracks for comfort.",
    "reply": "Keep your weapon ready then, we don't need any more surprises."
  },
  {
    "colonist": "Lidia Schmitt",
    "line": "[N], at least Hunter made a full recovery after missing that tortoise.",
    "reported": "Stench said at least Hunter made a full recovery after missing that tortoise.",
    "reply": "Animals healing up is the only good news we've had all week."
  },
  {
    "colonist": "Dillon Boyd",
    "line": "[N], living in these dreadful barracks finally pushed me over the edge.",
    "reported": "Dillon said living in these dreadful barracks finally pushed me over the edge.",
    "reply": "Take a breath, everyone's nerves are completely fried right now."
  },
  {
    "colonist": "Dillon Boyd",
    "line": "[N], I couldn't take the tension anymore with those gazelles and bears outside.",
    "reported": "Dillon said I couldn't take the tension anymore with those gazelles and bears outside.",
    "reply": "Just try to stay inside where it's safe until you feel better."
  },
  {
    "colonist": "Dillon Boyd",
    "line": "[N], my head is still spinning from wandering around in that psychotic state.",
    "reported": "Dillon said my head is still spinning from wandering around in that psychotic state.",
    "reply": "Drink some water and sit down for a while, you've had a rough time."
  },
  {
    "colonist": "Odette O'Neill",
    "line": "[N], I've been tending to the herbs while everyone else was losing their minds.",
    "reported": "Odette said I've been tending to the herbs while everyone else was losing their minds.",
    "reply": "Did you manage to grow anything that can calm our nerves?"
  },
  {
    "colonist": "Odette O'Neill",
    "line": "[N], Dillon needed a lot of space after the conditions in the barracks broke him.",
    "reported": "Odette said Dillon needed a lot of space after the conditions in the barracks broke him.",
    "reply": "It's hard not to crack when everything around us is so tense."
  },
  {
    "colonist": "Odette O'Neill",
    "line": "[N], at least Stench managed to secure that pen and the silver supplies.",
    "reported": "Odette said at least Stench managed to secure that pen and the silver supplies.",
    "reply": "That small win is the only thing keeping us afloat today."
  }
]
```

Keyword check (session-1 terms appearing; a crude indicator, not a judgement): narrative: grizzly, gazelle, steel, stockpile; dialogue: grizzly, gazelle, steel.

## Provenance + memory block + memory prompt

Same input as *provenance + memory block*. Narrative prompt: `experiments/pilot/prompts/narrative_memory.txt`, a copy of `prompts/narrative.txt` that says the input may start with memories from earlier sessions, asks to summarise the current-session logs, and adds: *"Memories are not events happening now. Where a current event connects to a memory, refer back to it briefly in the past tense … Do not narrate memories as new events, and do not invent links that the logs and memories don't support."* The dialogue step is unchanged.

### Narrative

Life on the frontier weighed heavily on Dillon Boyd, whose frayed nerves finally snapped beneath the bleak discomfort of the barracks, sending him wandering in a psychotic haze. While Boyd lost himself to despair, the colony pressed on. Lidia "Stench" Schmitt, fully recovered from her wounds, tended to daily survival. She guided a pack animal to its pen, hauled salvaged steel and a substantial cache of silver to safety, and took a clumsy shot at a tortoise, missing entirely. Beyond the camp's perimeter, the local wildlife—including the persistent grizzly bear and grazing gazelles—remained an ever-present fixture of the untamed wilderness.

### Dialogue

```json
[
  {
    "colonist": "Lidia Schmitt",
    "line": "[N], dad just wandered off muttering again, totally lost in his head.",
    "reported": "Stench said that her dad just wandered off muttering again, totally lost in his head.",
    "reply": "He'll come back when he clears his head, just leave him be."
  },
  {
    "colonist": "Lidia Schmitt",
    "line": "[N], I swear I missed that slow tortoise right at our doorstep.",
    "reported": "Stench said she swore she missed that slow tortoise right at their doorstep.",
    "reply": "How do you even manage to miss a target that slow?"
  },
  {
    "colonist": "Lidia Schmitt",
    "line": "[N], got the silver and steel hauled inside before it started raining.",
    "reported": "Stench said she got the silver and steel hauled inside before it started raining.",
    "reply": "Good job securing the supplies, we really needed those stored safely."
  },
  {
    "colonist": "Dillon Boyd",
    "line": "[N], these barracks are driving me completely insane with the noise.",
    "reported": "Dillon said those barracks were driving him completely insane with the noise.",
    "reply": "Take a breath, everyone is dealing with the same cramped quarters."
  },
  {
    "colonist": "Dillon Boyd",
    "line": "[N], my head is pounding and I couldn't take another second inside.",
    "reported": "Dillon said his head was pounding and he couldn't take another second inside.",
    "reply": "Sit down for a minute and drink some water."
  },
  {
    "colonist": "Dillon Boyd",
    "line": "[N], I just needed to walk away from everyone for a while.",
    "reported": "Dillon said he just needed to walk away from everyone for a while.",
    "reply": "Just don't wander too far out near where the grizzly roams."
  },
  {
    "colonist": "Odette O'Neill",
    "line": "[N], Dillon needs to rest instead of pacing around out there.",
    "reported": "Odette said Dillon needed to rest instead of pacing around out there.",
    "reply": "I'll go check on him and see if I can convince him to come back."
  },
  {
    "colonist": "Odette O'Neill",
    "line": "[N], Lidia is keeping us all fed while the men lose their minds.",
    "reported": "Odette said Lidia was keeping them all fed while the men lost their minds.",
    "reply": "She's handling the workload surprisingly well despite everything."
  },
  {
    "colonist": "Odette O'Neill",
    "line": "[N], that bear is still prowling just outside the perimeter fence.",
    "reported": "Odette said that bear was still prowling just outside the perimeter fence.",
    "reply": "I saw it too, we need to keep the doors bolted tight tonight."
  }
]
```

Keyword check (session-1 terms appearing; a crude indicator, not a judgement): narrative: grizzly, gazelle, steel; dialogue: grizzly, steel.

## Provenance + memory block + explicit-callback prompt

Same input as *provenance + memory block*. Narrative prompt: `experiments/pilot/prompts/narrative_memory_explicit.txt`, a copy of `prompts/narrative.txt` that says the input may start with memories from earlier sessions, asks to summarise the current-session logs, and adds: *"If a current event connects to a memory, make that connection once, explicitly, in the past tense, so a reader who remembers the earlier session recognises it … Mention at most one such connection … If no current event connects to a memory, do not mention the memories at all."* The dialogue step is unchanged.

### Narrative

Life at the outpost remained shadowed by the presence of a lingering grizzly bear. Amidst the daily routines—Lidia tending to an animal pen and hauling stockpiles of steel and silver from the debris of a downed spacecraft—tensions frayed. Overwhelmed by the wretched conditions of their makeshift barracks, Dillon suffered a psychological break, wandering the camp in a daze while staring vacantly into the distance for targets. Meanwhile, Lidia had fully recovered from her wounds, though her focus on local wildlife proved imperfect after she missed a passing tortoise.

### Dialogue

```json
[
  {
    "colonist": "Lidia 'Stench' Schmitt",
    "line": "[N], that bear is still prowling around out there and it's creeping me out.",
    "reported": "Stench said that bear is still prowling around out there and it's creeping her out.",
    "reply": "Just keep your distance from it and we'll be fine."
  },
  {
    "colonist": "Lidia 'Stench' Schmitt",
    "line": "[N], I swear that tortoise just moved faster than my aim today.",
    "reported": "Stench said she swears that tortoise just moved faster than her aim today.",
    "reply": "Maybe you need to practice your shooting on something bigger."
  },
  {
    "colonist": "Lidia 'Stench' Schmitt",
    "line": "[N], hauling all that steel and silver scrap is wearing my arms out.",
    "reported": "Stench said hauling all that steel and silver scrap is wearing her arms out.",
    "reply": "We need the materials to fix up the barracks anyway."
  },
  {
    "colonist": "Dillon Boyd",
    "line": "[N], these wretched barracks are driving me completely out of my mind.",
    "reported": "Dillon said those wretched barracks were driving him completely out of his mind.",
    "reply": "We are all dealing with the cramped conditions the best we can."
  },
  {
    "colonist": "Dillon Boyd",
    "line": "[N], I couldn't focus on anything at all earlier today, just walking in circles.",
    "reported": "Dillon said he couldn't focus on anything at all earlier that day, just walking in circles.",
    "reply": "You need to rest more instead of letting the stress get to you."
  },
  {
    "colonist": "Dillon Boyd",
    "line": "[N], having that grizzly lingering near the camp is the last thing we need right now.",
    "reported": "Dillon said having that grizzly lingering near the camp was the last thing they needed right then.",
    "reply": "Let the hunters handle the beast while you stay inside."
  },
  {
    "colonist": "Odette O'Neill",
    "line": "[N], Lidia is back on her feet, though missing that tortoise was pretty funny.",
    "reported": "Odette said Lidia was back on her feet, though missing that tortoise was pretty funny.",
    "reply": "At least she is healing up well after her injuries."
  },
  {
    "colonist": "Odette O'Neill",
    "line": "[N], Dillon looked completely lost earlier while wandering through the camp dazed.",
    "reported": "Odette said Dillon looked completely lost earlier while wandering through the camp dazed.",
    "reply": "The stress of this place is starting to break everyone down."
  },
  {
    "colonist": "Odette O'Neill",
    "line": "[N], we really need to clear out the debris from that downed spacecraft.",
    "reported": "Odette said they really needed to clear out the debris from that downed spacecraft.",
    "reply": "It's a huge eyesore right in the middle of our camp."
  }
]
```

Keyword check (session-1 terms appearing; a crude indicator, not a judgement): narrative: grizzly, spacecraft, steel, stockpile; dialogue: grizzly, spacecraft, steel.

## Provenance + RC links + links prompt

Same pool as *provenance*. The memories are labelled M1, M2, …, and each event the RC picked for a memory is marked with the RC's own pairing, e.g. `(recalls M1)`; the system decides every link. Narrative prompt: `experiments/pilot/prompts/narrative_memory_links.txt`, which explains the marks and adds: *"For an event marked (recalls Mx), you may refer back to memory Mx briefly, in the past tense, where it fits the story … Only link memories to the events marked with them; do not link any other event to a memory, and never narrate memories as new events."* The dialogue step is unchanged. What the LLM receives as its input logs:

```
Earlier sessions (things the colonists said in a previous session; these are memories and background, not events happening now):

M1: Lidia 'Stench' Schmitt said 'Boyd, I had those fifty-six steel beams stashed before the grizzly settled in.'[x1][V]

M2: Odette 'Odette' O'Neill said 'Stench, those gazelles were grazing amid the chunks of the downed spacecraft.'[x1][V]

M3: Odette 'Odette' O'Neill said 'Boyd, a grizzly at camp's edge was trouble waiting to happen.'[x1][V]

This session (events in temporal order):

Boyd watching for targets.[x1][V]

Stench, Hunter is fully healed.[x1][V]

Boyd is wandering around in a psychotic state. This happened because of poor mood. The final straw was: Awful barracks[x1][V]

Stench leading Papyrus to wooden pen marker.[x1][V]

Stench missed the tortoise.[x1][V]

A(n) grizzly bear standing.[x153][V] (recalls M1, M3)

A(n) gazelle consuming grass.[x1][NV] (recalls M2)

Stench hauling steel x18 to Stockpile zone 1.[x1][V] (recalls M1)

Stench hauling silver x500 to Stockpile zone 1.[x1][V]
```

### Narrative

Life at the colony carried on beneath the ever-watchful gaze of the local wildlife. While a grizzly bear prowled near the perimeter and gazelles grazed among distant spacecraft debris, daily routines pressed forward. 

Dillon Boyd scanned the horizons for potential threats, though the strain of poor living conditions in the awful barracks soon took its toll, driving him to wander the camp in a psychotic haze. Meanwhile, Lidia 'Stench' Schmitt focused on domestic and logistical duties. Fully healed from past injuries, she guided a pack animal to its pen, relocated a stash of silver, and hauled fifty-six steel beams back to the stockpile, securing resources previously left vulnerable to the roaming beasts.

### Dialogue

```json
[
  {
    "colonist": "Lidia 'Stench' Schmitt",
    "line": "[N], those steel beams are finally safe from the wildlife.",
    "reported": "Stench said those steel beams were finally safe from the wildlife.",
    "reply": "Thank goodness, we really needed those in the stockpile."
  },
  {
    "colonist": "Lidia 'Stench' Schmitt",
    "line": "[N], I spent all morning dragging fifty-six heavy beams across camp.",
    "reported": "Stench said she spent all morning dragging fifty-six heavy beams across camp.",
    "reply": "You must be exhausted after all that heavy lifting."
  },
  {
    "colonist": "Lidia 'Stench' Schmitt",
    "line": "[N], did you see that huge grizzly bear prowling near the perimeter?",
    "reported": "Stench asked if I saw that huge grizzly bear prowling near the perimeter.",
    "reply": "Yeah, I kept a very close eye on it from a distance."
  },
  {
    "colonist": "Dillon Boyd",
    "line": "[N], these awful barracks are driving me completely insane.",
    "reported": "Dillon said those awful barracks were driving him completely insane.",
    "reply": "We'll try to fix the rooms up soon, just hang in there."
  },
  {
    "colonist": "Dillon Boyd",
    "line": "[N], I couldn't stop wandering around in a haze earlier today.",
    "reported": "Dillon said he couldn't stop wandering around in a haze earlier today.",
    "reply": "The stress is getting to everyone lately, you need some rest."
  },
  {
    "colonist": "Dillon Boyd",
    "line": "[N], I scanned the horizon for threats until my eyes ached.",
    "reported": "Dillon said he scanned the horizon for threats until his eyes ached.",
    "reply": "At least you caught sight of anything moving out there."
  },
  {
    "colonist": "Odette O'Neill",
    "line": "[N], gazelles were just grazing near the spacecraft debris like nothing was wrong.",
    "reported": "Odette said gazelles were just grazing near the spacecraft debris like nothing was wrong.",
    "reply": "Nature doesn't care about our crashed ships at all."
  },
  {
    "colonist": "Odette O'Neill",
    "line": "[N], wildlife is watching us every single second we're out here.",
    "reported": "Odette said wildlife was watching them every single second they were out there.",
    "reply": "It certainly feels like we're being hunted sometimes."
  },
  {
    "colonist": "Odette O'Neill",
    "line": "[N], Dillon needs to take a break before he collapses from stress.",
    "reported": "Odette said Dillon needed to take a break before he collapsed from stress.",
    "reply": "I'll go check on him right now and see if he's calmer."
  }
]
```

Keyword check (session-1 terms appearing; a crude indicator, not a judgement): narrative: grizzly, gazelle, spacecraft, steel, stockpile; dialogue: grizzly, gazelle, spacecraft, steel, stockpile.

## Observations

*Claude's reading of the cached outputs generated on 2026-11-26 (not the author's judgement; regenerating with a different model or prompt would need a fresh read).*

- **Selection.** *Original*: one dialogue line (S110, the treeline) brings five near-identical fight lines; none relates to the treeline or the raiders. *Provenance*: three lines (S104 steel/grizzly, S111 gazelles/spacecraft, S112 grizzly) bring a grizzly, a grazing gazelle and a steel haul to the stockpile. These are clearly linked to what the lines are about, but they are mostly routine logs.
- **The provenance pool loses session 2's main drama.** The Odette–Stench fistfight and insult spree are the most eventful things in session 2, and in the original pool they came only through the RC's name matching. The AC didn't select them at this share, so with provenance they disappear from the pool and from the story. Continuity now competes with the current session's salient events for the same 12 slots.
- **Narrative.** *Original* is coherent and dramatic, but has no link to session 1 (keyword check: none). *Provenance* picks up session 1 (steel beams, the grizzly at the camp's edge, gazelles among the spacecraft wreckage), but **it narrates the old dialogue as if it were happening now** ("secured vital steel beams … before a dangerous grizzly bear established its territory"). The LLM isn't told which pool lines are memories from an earlier session, so continuity turns into retelling.
- **Dialogue.** Both are fluent. *Provenance* refers back to session 1 naturally ("that grizzly bear is still lingering right by the camp edge", "those steel beams … took forever to haul back"), but also invents a detail ("steel beams from the wreckage": nothing links the steel to the spacecraft).

- **Provenance + memory block** (same pool, same prompt; the earlier-session dialogue lines are given in a separate block labelled as memories, not events happening now):
  - The narrative **no longer retells the old dialogue as current events**.
  - But it **drops the session-1 continuity altogether**: the memories are treated as background and not used. The gazelles and grizzly it mentions are session 2's own wildlife; nothing refers back to session 1.
  - **New errors:** it reads "Stench, Hunter is fully healed" as an animal called Hunter recovering, and calls the 18 steel hauled this session "eighteen steel beams", borrowing "beams" from the session-1 memory.
  - Formatting alone swings the model from retelling to ignoring. The narrative prompt asks for "an objective summary of the provided logs" and says nothing about memories.
- **Provenance + memory block + memory prompt** (the narrative prompt is told what memories are and to refer back to them only where a current event connects):
  - **No retelling:** session-1 content is not narrated as new events.
  - **Implicit continuity:** "the persistent grizzly bear and grazing gazelles remained an ever-present fixture"; in the dialogue, "that bear is still prowling just outside the perimeter fence". There is no explicit past-tense reference (nothing about the steel beams stashed before the grizzly settled in).
  - **Fewer errors:** the "Hunter" misreading is gone (Stench recovers), and the dialogue uses the family tie from the bios ("dad just wandered off"). One slip: "salvaged steel" leaks the wreckage from the memories.
- **Provenance + memory block + explicit-callback prompt** (asks for exactly one explicit past-tense callback when a connection exists, none otherwise):
  - **No explicit callback** ("a lingering grizzly bear").
  - **Memories leak into the present:** Lidia hauls steel and silver "from the debris of a downed spacecraft", and the dialogue says "we really need to clear out the debris from that downed spacecraft". That is retelling plus an invented link, the failure the prompt was meant to prevent.
- **Provenance + RC links + links prompt** (memories labelled M1–M3; each RC event marked with the memories the RC paired it with, e.g. the steel haul `(recalls M1)`; the prompt allows referring back only through the marks):
  - The model **does use the memories**, but **fuses them into the present** rather than referring back: "gazelles grazed among distant spacecraft debris", with no past tense anywhere.
  - **A session-1 fact overwrites a session-2 fact:** Stench "hauled fifty-six steel beams back to the stockpile". This session's log says 18 steel; 56 comes from memory M1. The dialogue repeats it ("dragging fifty-six heavy beams across camp").
- **A contamination check worth recording:** the first versions of both memory prompts used an example sentence about this colony's grizzly, and with it the explicit-callback prompt produced a clean callback ("the grizzly bear—which had settled at the camp's edge in the colony's early days—was still prowling nearby"), nearly word for word from the example. With a neutral example (a well running dry) that callback disappeared. Those outputs are kept in `session2_e2e_contaminated.json`.

| condition | uses session 1? | treats it as past? | errors noticed |
|---|---|---|---|
| original | no | n/a | none major |
| provenance | yes, strongly | no (retold as now) | steel "from the wreckage" |
| + memory block | no | n/a | "Hunter" as an animal; "eighteen steel beams" |
| + memory prompt | implicitly (grizzly as an ever-present fixture) | yes | "salvaged steel" |
| + explicit-callback prompt | yes, as present events | no | steel "from the debris of a downed spacecraft" |
| + RC links + links prompt | yes, fused with present events | no | "fifty-six steel beams" hauled now (log: 18) |

**Reading:** the more the narrative step is pushed to use memories, the more it merges them into the present. Asking softly gives faint but correct continuity. Asking firmly, or handing it the exact links, makes it retell the memories as current events, and with the links it even overwrote a current fact with a remembered one. Within a single summarisation call, this model doesn't keep "then" and "now" apart.

**Suggested follow-ups** (not done):
- **Keep the narrative step on the current session** (the memory-prompt version, or the flat pool without the dialogue lines). Let continuity come from the selection: the RC already puts events that connect to earlier dialogue into the pool.
- **Deliver explicit callbacks separately and constrained:** e.g. a short, dedicated step that receives one RC link (a memory and the current event the RC paired with it) and writes a single past-tense sentence or dialogue line about it, which can be checked against both logs. The system chooses the link; the LLM only words it.
- Check the share: at 0.5 the RC takes 6 of 12 slots, enough to crowd out session 2's own highlights. A lower share (e.g. 0.25) or a quota that counts events only may keep both.
- Read more than one run: this is one AC seed and one generation per condition.

