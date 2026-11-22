# Gold helper for pilot test A1

Session events: `Test Scenarios\SiftingChannels\SimulatedDay2\formatted_event_logs.txt` (162 distinct descriptions, dialogue lines excluded).
Reference set `s1_selected` (events): `Test Scenarios\SiftingChannels\SimulatedDay1\selected_reference_logs.txt` (13 lines).

For each reference line, write the codes of the events that continue it into `experiments/pilot/gold_matches_s1_selected.csv` (`expected_event_id`, `/`- or `;`-separated; `[notes]` allowed). The `dialogue_id` column holds the reference line's _ID_ whatever the reference kind. Leave it empty if nothing in this session relates to the line.

## Reference lines

| dialogue_id | tick | line |
|---|---|---|
| J197 | 317824 | A(n) grizzly bear standing. |
| J784 | 319227 | Stench hauling steel x56 to Stockpile zone 1. |
| J6248 | 328956 | Papyrus following Stench. |
| J23595 | 353689 | Stench moving. |
| L0 | 335568 | A group of tribespeople from Confederacy of Loucó have arrived nearby. They are attacking immediately. |
| J11087 | 335779 | Boyd relaxing socially. |
| J11165 | 335810 | Odette watching for targets. |
| b57 | 337794 | Boyd fired timidly at Walrus. |
| b74 | 338170 | Stench hit Walrus with a shot. |
| b81 | 338305 | Walrus died. |
| b88 | 338888 | Boyd's shot hit Anteater. |
| J19592 | 349632 | A(n) gazelle consuming grass. |
| L5 | 351500 | Chunks of a spacecraft have impacted nearby. You can deconstruct them to yield resources. |

## Current-session events (chronological)

| code | first tick | first _ID_ | count | vis | description |
|---|---|---|---|---|---|
| E000 | 357517 | J23858 | 1 | V | Boyd watching for targets. |
| E001 | 357517 | J24202 | 2 | V | Odette tending to Odette. |
| E002 | 357517 | J23800 | 1 | V | Stench watching for targets. |
| E003 | 357521 | J25557 | 849 | V | A(n) rat wandering. |
| E004 | 357522 | J25641 | 851 | V | A(n) rat standing. |
| E005 | 357544 | J25544 | 609 | NV | A(n) buck wandering. |
| E006 | 357545 | J25643 | 612 | NV | A(n) buck standing. |
| E007 | 357557 | J25594 | 850 | V | A(n) gazelle wandering. |
| E008 | 357558 | J25645 | 850 | V | A(n) gazelle standing. |
| E009 | 357559 | J25597 | 275 | V | A(n) ibex ram wandering. |
| E010 | 357560 | J25573 | 166 | V | Papyrus wandering. |
| E011 | 357560 | J25581 | 1425 | V | A(n) squirrel wandering. |
| E012 | 357560 | J25647 | 275 | V | A(n) ibex ram standing. |
| E013 | 357561 | J25648 | 171 | V | Papyrus standing. |
| E014 | 357561 | J25649 | 1430 | V | A(n) squirrel standing. |
| E015 | 357568 | J25508 | 130 | NV | A(n) ibex doe wandering. |
| E016 | 357569 | J25653 | 131 | NV | A(n) ibex doe standing. |
| E017 | 357570 | J25555 | 616 | V | A(n) raccoon wandering. |
| E018 | 357571 | J25655 | 616 | V | A(n) raccoon standing. |
| E019 | 357573 | J25580 | 280 | NV | A(n) alpaca wandering. |
| E020 | 357574 | J25659 | 282 | NV | A(n) alpaca standing. |
| E021 | 357576 | J25571 | 214 | V | A(n) tortoise wandering. |
| E022 | 357576 | J25607 | 621 | V | A(n) hare wandering. |
| E023 | 357577 | J25661 | 214 | V | A(n) tortoise standing. |
| E024 | 357577 | J25662 | 625 | V | A(n) hare standing. |
| E025 | 357592 | J25592 | 300 | NV | A(n) boomrat wandering. |
| E026 | 357593 | J25673 | 302 | NV | A(n) boomrat standing. |
| E027 | 357605 | J25475 | 4 | NV | A(n) rat consuming grass. |
| E028 | 357614 | J25600 | 291 | V | A(n) doe wandering. |
| E029 | 357615 | J25686 | 292 | V | A(n) doe standing. |
| E030 | 357632 | J25613 | 380 | V | A(n) rhinoceros wandering. |
| E031 | 357633 | J25688 | 391 | V | A(n) rhinoceros standing. |
| E032 | 357643 | J25616 | 285 | V | A(n) donkey wandering. |
| E033 | 357644 | J25692 | 287 | V | A(n) donkey standing. |
| E034 | 357716 | J25601 | 145 | NV | A(n) timber wolf wandering. |
| E035 | 357717 | J25706 | 146 | NV | A(n) timber wolf standing. |
| E036 | 357818 | J25621 | 219 | V | A(n) turkey wandering. |
| E037 | 357819 | J25712 | 226 | V | A(n) turkey standing. |
| E038 | 357854 | J25577 | 1 | NV | A(n) hare consuming bush. |
| E039 | 358387 | J25722 | 193 | V | Boyd standing. |
| E040 | 360016 | J25732 | 10 | V | Odette standing. |
| E041 | 360782 | S120 | 1 | V | Stench chatted about fighting tapirs with Odette. |
| E042 | 370572 | L12 | 3 | V | Critical alert (UI notification): Major break risk |
| E043 | 373142 | L13 | 1 | V | Stench, Hunter is fully healed. |
| E044 | 373143 | H83 | 1 | V | Stench healed from (a) bruise (human fist) (right leg) |
| E045 | 373714 | L1 | 1 | V | Boyd is wandering around in a psychotic state. This happened because of poor mood. The final straw was: Awful barracks |
| E046 | 373841 | J25790 | 191 | V | Boyd wandering. |
| E047 | 374927 | J25800 | 20 | V | Stench standing. |
| E048 | 375339 | J25651 | 1 | V | Papyrus resting. |
| E049 | 376217 | J25812 | 1 | V | Papyrus following Stench. |
| E050 | 376276 | J25802 | 1 | V | Stench leading Papyrus to wooden pen marker. |
| E051 | 376379 | b123 | 1 | V | Stench shot at the turkey. |
| E052 | 376411 | b124 | 1 | V | The turkey ducked aside at the last second, Stench's bolt-action rifle bullet blowing offcourse. |
| E053 | 376571 | b125 | 1 | V | Stench fired her bolt-action rifle at the turkey. |
| E054 | 376613 | b126 | 1 | V | Stench hit the turkey with a bolt-action rifle bullet. |
| E055 | 376613 | H96 | 1 | NV | A(n) turkey was afflicted with (a) gunshot (body) |
| E056 | 376651 | H97 | 1 | NV | A(n) turkey was afflicted with (a) blood loss (minor) |
| E057 | 376763 | b127 | 1 | V | Stench fired at the turkey. |
| E058 | 376816 | b128 | 1 | V | Stench's bolt-action rifle bullet missed by a small margin. |
| E059 | 376964 | J25826 | 1 | V | Stench hunting turkey. |
| E060 | 377380 | b129 | 1 | V | Stench fired her bolt-action rifle at the tortoise. |
| E061 | 377430 | J25663 | 1 | V | A(n) tortoise resting. |
| E062 | 377430 | b130 | 1 | V | Stench missed the tortoise. |
| E063 | 377443 | J25848 | 1 | V | Stench hunting tortoise. |
| E064 | 377494 | J25843 | 1 | NV | A(n) turkey fleeing. |
| E065 | 377726 | J25864 | 2 | V | Stench building grave (building). |
| E066 | 378080 | J25866 | 1 | NV | A(n) turkey consuming area. |
| E067 | 378871 | J25905 | 11 | NV | A(n) rhinoceros consuming area. |
| E068 | 379163 | J25918 | 7 | NV | A(n) squirrel consuming grass. |
| E069 | 379332 | J25951 | 152 | V | A(n) grizzly bear wandering. |
| E070 | 379333 | J25992 | 153 | V | A(n) grizzly bear standing. |
| E071 | 379386 | J25937 | 1 | NV | A(n) gazelle consuming grass. |
| E072 | 379504 | J25949 | 2 | NV | A(n) hare consuming grass. |
| E073 | 379623 | J25960 | 2 | NV | A(n) donkey consuming area. |
| E074 | 379759 | J25983 | 1 | NV | A(n) turkey consuming grass. |
| E075 | 379955 | J26015 | 1 | NV | A(n) hare consuming area. |
| E076 | 380149 | J26072 | 3 | NV | A(n) raccoon consuming grass. |
| E077 | 380483 | J26175 | 1 | NV | A(n) raccoon consuming tall grass. |
| E078 | 380979 | J26380 | 1 | NV | A(n) ibex doe consuming area. |
| E079 | 381533 | J26669 | 2 | NV | A(n) boomrat consuming grass. |
| E080 | 382161 | J25876 | 1 | V | Stench cloudwatching. |
| E081 | 382952 | J27282 | 1 | V | Stench milking Papyrus. |
| E082 | 384362 | S131 | 1 | V | Stench shared views on aiding the downtrodden with Boyd. |
| E083 | 384627 | J27707 | 3 | V | Stench building area. |
| E084 | 386827 | J29265 | 1 | V | Stench burying Anteater, Shaman (dead) in grave. |
| E085 | 387699 | J29710 | 1 | V | Stench burying Walrus, Treehouse builder (dead) in grave. |
| E086 | 388538 | J30178 | 1 | V | Stench hauling wooden club to Stockpile zone 1. |
| E087 | 388857 | J30545 | 1 | NV | A(n) squirrel consuming berry bush. |
| E088 | 389107 | J30640 | 1 | V | Stench hauling steel x18 to Stockpile zone 1. |
| E089 | 389488 | J30945 | 1 | V | Stench hauling synthread pants (normal 97%) to Stockpile zone 1. |
| E090 | 389878 | J31142 | 1 | V | Stench hauling silver x500 to Stockpile zone 1. |
| E091 | 390222 | J31345 | 1 | V | Stench hauling component x30 to Stockpile zone 1. |
| E092 | 390510 | J31401 | 1 | NV | A(n) squirrel consuming bush. |
| E093 | 390765 | J31505 | 1 | V | Stench hauling. |
| E094 | 391256 | J31903 | 3 | NV | A(n) buck consuming area. |
| E095 | 392840 | L2 | 1 | NV | A medieval farm oaf named Ackmann is crashing in a transport pod nearby. If he survives the impact, he will be badly wounded. Ackmann is from your enemy Alyona's Rockets. You can capture him for recruitment or slavery purposes. |
| E096 | 392859 | J32029 | 1 | V | Stench harvesting area. |
| E097 | 392969 | J33842 | 1 | V | Stench hauling wood x7 to wooden stool (building). |
| E099 | 393096 | J33977 | 8 | NV | Ackmann standing. |
| E100 | 394302 | b132 | 1 | NV | The timber wolf bit the rat. |
| E101 | 394302 | H109 | 1 | NV | A(n) rat was afflicted with (a) Destroyed (brain) |
| E102 | 394302 | H110 | 1 | NV | A(n) rat was afflicted with (a) Bitten out (left eye) |
| E103 | 394302 | H111 | 1 | NV | A(n) rat was afflicted with (a) Bitten out (right eye) |
| E104 | 394302 | H112 | 1 | NV | A(n) rat was afflicted with (a) Bitten off (left ear) |
| E105 | 394302 | H113 | 1 | NV | A(n) rat was afflicted with (a) Bitten off (right ear) |
| E106 | 394302 | H114 | 1 | NV | A(n) rat was afflicted with (a) Bitten off (nose) |
| E107 | 394302 | H115 | 1 | NV | A(n) rat was afflicted with (a) Bitten off (jaw) |
| E108 | 394302 | b133 | 1 | NV | Missing a neck caused the rat to expire. |
| E109 | 394302 | H116 | 1 | NV | A(n) rat was afflicted with (a) bite (timber wolf teeth) (body) |
| E110 | 394425 | J34409 | 1 | NV | A(n) hare consuming tall grass. |
| E111 | 394516 | L3 | 1 | NV | Odette has fixated her rage on Stench. She will follow Stench around, hurling insults. This happened because of poor mood. The final straw was: Ravenously hungry |
| E112 | 394897 | J34649 | 2 | NV | A(n) rat consuming dandelions. |
| E113 | 394922 | J34349 | 1 | NV | A(n) timber wolf consuming . |
| E114 | 395085 | S134 | 1 | V | Odette flagrantly insulted Stench's leg hair. |
| E115 | 395085 | J34720 | 1 | V | Odette insulting Stench. |
| E116 | 395596 | J33979 | 3 | NV | Ackmann downed. |
| E117 | 396285 | L20 | 1 | V | Stench started a social fight with Odette. |
| E118 | 396285 | L21 | 1 | V | Odette is no longer on an insulting spree against Stench, Hunter. |
| E119 | 396285 | S135 | 1 | V | Odette called Stench a salamander. This drove Stench into a rage and she began a fight! |
| E120 | 396316 | b136 | 1 | V | Odette attempted to bash Stench, but missed. |
| E121 | 396316 | J35621 | 9 | V | Odette fighting with Stench. |
| E122 | 396317 | b137 | 1 | V | Stench smashed Odette with her left fist. |
| E123 | 396317 | H117 | 1 | V | Odette was afflicted with (a) bruise (human fist) (torso) |
| E124 | 396317 | J35623 | 8 | V | Stench fighting with Odette. |
| E125 | 396437 | b138 | 1 | V | Odette flailed at Stench, but stumbled at the last second. |
| E126 | 396438 | b139 | 2 | V | Stench slammed Odette with her left fist. |
| E127 | 396438 | H118 | 1 | V | Odette was afflicted with (a) bruise (human fist) (right leg) |
| E128 | 396558 | b140 | 1 | V | Odette missed Stench with a beat from her left fist. |
| E129 | 396559 | b141 | 1 | V | Stench missed Odette with a smash from her left fist. |
| E130 | 396679 | b142 | 1 | V | Odette stumbled while trying to strike Stench. |
| E131 | 396680 | b143 | 1 | V | Stench tried to smash Odette, but missed. |
| E132 | 396800 | b144 | 1 | V | Odette ineptly bashed Stench with her left fist. |
| E133 | 396800 | H119 | 1 | V | Stench was afflicted with (a) bruise (human fist) (left arm) |
| E134 | 396800 | H120 | 1 | V | Stench was afflicted with (a) crack (human fist) (left radius) |
| E135 | 396801 | b145 | 1 | V | Stench missed Odette with a hit from her left fist. |
| E136 | 396834 | J35648 | 2 | NV | A(n) alpaca consuming area. |
| E137 | 396921 | b146 | 1 | V | Odette attempted to hit Stench, but hesitated at the last second. |
| E138 | 396922 | b147 | 1 | V | Stench flailed at Odette with her left fist, but stumbled at the last second. |
| E139 | 397042 | b148 | 1 | V | Odette tried to use her right fist to hit Stench, but stumbled at the last second. |
| E140 | 397043 | b149 | 1 | V | Stench missed while trying to bash Odette with her left fist. |
| E141 | 397163 | b150 | 1 | V | Odette hit Stench with her left fist. |
| E142 | 397163 | H121 | 1 | V | Stench was afflicted with (a) bruise (human fist) (torso) |
| E143 | 397164 | b151 | 1 | V | Stench tried to hit Odette, but missed. |
| E144 | 397284 | b152 | 1 | V | Odette attempted to use her right fist to beat Stench, but missed. |
| E145 | 397285 | H122 | 1 | V | Odette was afflicted with (a) bruise (human fist) (left leg) |
| E146 | 397285 | L22 | 1 | V | Stench and Odette are no longer social fighting. |
| E147 | 397285 | b154 | 1 | V | Odette collapsed due to a bruise. |
| E148 | 397285 | H123 | 1 | V | Odette was afflicted with (a) crack (human fist) (left femur) |
| E149 | 397287 | L23 | 1 | V | Critical alert (UI notification): Colonist needs rescue |
| E155 | 397650 | B6 | 1 | NV | Battle: The turkey's report |
| E150 | 397651 | b155 | 1 | NV | The turkey dropped. |
| E151 | 397666 | H124 | 1 | V | Odette was afflicted with (a) malnutrition (trivial) |
| E152 | 397690 | J36149 | 1 | V | Odette downed. |
| E153 | 398870 | J36503 | 1 | NV | A(n) grizzly bear consuming area. |
| E154 | 400152 | J36345 | 5 | NV | A(n) turkey downed, unconscious. |
| E156 | 403612 | J38148 | 4 | NV | Ackmann downed, unconscious. |
| E157 | 406163 | J36147 | 1 | V | Stench resting. |
| E158 | 406378 | J41374 | 1 | NV | A(n) doe consuming area. |
| E159 | 406973 | J41760 | 1 | V | Stench hauling packaged survival meal x10 to Stockpile zone 1. |
| E160 | 407736 | J43245 | 1 | V | Stench tending to Odette. |
| E161 | 408004 | H125 | 1 | NV | Ackmann was afflicted with (a) infection (minor) (left leg) |
| E162 | 409137 | J43259 | 1 | V | Stench feeding area to Odette. |
