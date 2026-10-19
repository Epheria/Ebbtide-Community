# Role scripts

One CSV per role. Each row is one file to record.

| Column | Meaning |
| --- | --- |
| `file` | Name your take exactly this, plus `.flac` or `.wav`. Example: `FA18_CheckIn.flac`. |
| `situation` | What is happening in the game when the line plays. |
| `tone` | How the line is delivered today. A starting point, not a rule. |
| `line` | The words to say. |
| `current_voices` | The characters who say this line in the game today, with (M) or (F) for the current voice. |

## Callsigns

`<callsign>` means "say your own callsign here". When you are cast, you get one callsign, for example Dagger Two One, and you record every row with that callsign. Rows without `<callsign>` are the same for everyone in the role.

A row whose `current_voices` lists only some characters is recorded only by those characters. For example, `UH60_FinalEgg` is Raven Six only.

Say numbers in callsigns the radio way: "Dagger One One", not "Dagger Eleven". Say LAV as letters: "L-A-V".

## Lines still to confirm

Six lines are marked *Wording not confirmed* in the `situation` column. Their original scripts were lost, so the text was rebuilt from design notes. A maintainer checks them against the current game clip before you record them.

## Roles

| Role | Lines | Characters |
| --- | ---: | --- |
| **Pilots** | | |
| [carrier_jet_pilot](carrier_jet_pilot.csv) | 15 | F/A-18 pilots on the carrier, call the carrier "Mother": Dagger One One, Two One, Three One, Four One (M); Dagger One Two, Two Two, Three Two, Four Two (F) |
| [marine_jet_pilot](marine_jet_pilot.csv) | 15 | Marine F-35B pilots from a land base: Wraith Three One (M), Wraith Three Two (F) |
| [strike_eagle_pilot](strike_eagle_pilot.csv) | 21 | F-15E pilots: Eagle Two One, Eagle Two Two (F); Eagle Three One, Eagle Three Two (M) |
| [hawg_pilot](hawg_pilot.csv) | 18 | A-10 pilots: Hawg One One, Hawg One Two, Hawg Two One (M) |
| [ac130_pilot](ac130_pilot.csv) | 4 | Spooky Four One, AC-130 pilot: relaxed veteran (M) |
| [ac130_fire_control](ac130_fire_control.csv) | 6 | Spooky Four One, AC-130 fire control officer: dry and clipped (M) |
| [drone_operator](drone_operator.csv) | 7 | Kestrel Two Zero, MQ-9 operator: quiet and analytical (F) |
| **Helicopters** | | |
| [transport_heli_pilot](transport_heli_pilot.csv) | 35 | Black Hawk pilots, also heard on the Chinook: Raven Six, Raven Five (F); Raven Four, Raven Seven (M) |
| [attack_heli_pilot](attack_heli_pilot.csv) | 31 | Cobra pilots: Viper One One, Viper One Two (M) |
| **Ships** | | |
| [carrier_captain](carrier_captain.csv) | 6 | Sovereign Actual, carrier captain: older, very deep, gruff, brisk (M) |
| [carrier_air_boss](carrier_air_boss.csv) | 14 | Tower, the Air Boss on the flight deck speakers: loud and brassy (M) |
| [carrier_lso](carrier_lso.csv) | 2 | Paddles, landing signal officer: relaxed (M) |
| [destroyer_captain](destroyer_captain.csv) | 13 | Destroyer captains: Trident Actual, Mako Actual (M) |
| [cic_gunnery_talker](cic_gunnery_talker.csv) | 5 | Guns, the destroyer's gunfire talker: crisp and procedural (M) |
| **Vehicles** | | |
| [tank_commander](tank_commander.csv) | 16 | Tank commander: older, very deep, slow Texas drawl (M) |
| [bradley_commander](bradley_commander.csv) | 16 | Bradley commander, callsign Warhorse: British exchange officer, brisk (M) |
| [humvee_driver](humvee_driver.csv) | 15 | Humvee driver: young, fast-talking New Yorker (M) |
| [lav_crew](lav_crew.csv) | 18 | LAV crew: rough, low, urgent (M) |
| **Infantry** | | |
| [squad_leader](squad_leader.csv) | 8 | Squad leader |
| [rifleman](rifleman.csv) | 3 | Riflemen calling casualties |
| [hq_dispatcher](hq_dispatcher.csv) | 1 | HQ on the radio net |

The character notes describe the current AI voices. Your own take on a character is welcome.

## For maintainers

[`../clip_map.csv`](../clip_map.csv) lists all 606 voice clips in the game: which take file replaces which game file, and where each line's text came from. A `<callsign>` take replaces one game file per character, so match it by `take_file` and the actor's `callsign`. Clips marked `in_game` = `no` are unused alternate takes and are not in any script.
