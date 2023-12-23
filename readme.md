# Sound Manager
#### Video Demo:  https://youtu.be/gM4c-YEF7lQ
#### Description:
A tool for managing audio playback during live events with minimal in-event work. It reduces user involvement to cueing each transition.

#### Features
- Looping - Tracks can loop until the next cue
- Per-track volume - Preconfigure the volume of each track to keep them balanced
- Auto-end - Move to the next track automatically once the specified time has elapsed
- Fade in / Fade out - Total control over the length of fades in and out on a per-track basis
- All tracks are in memory, eliminating read time mid-playback

#### Prerequisites
- Python 3.10-3.12. May work on other versions.
- Pygame 2.5.2. May work on other versions.

#### Use
Songs are stored in the `data` folder in OGG or WAV format.

Song configurations are defined in `data\config.json`. Each configuration is defined as an array of objects.
```json
{
	"demo1": [
		{
			"file": null,
			"name": "Silence",
			"volume": 1.0,
			"loop": true,
			"end_ms": null,
			"fade_in_ms": 0,
			"fade_out_ms": 0
		},
		{
			"file": "BaharuthAmbientLoop.ogg",
			"name": "Ambient Loop - Baharuth",
			"volume": 0.5,
			"loop": true,
			"end_ms": null,
			"fade_in_ms": 1000,
			"fade_out_ms": 10000
		}
	]
}
```

The properties within each object are as follows:

- "file": The filename of the OGG or WAV or `null` if the track is silent
- "name": A string containing the name shown in the UI
- "volume": A float from `0` to `1`. Values less than 1 reduce the volume of the track
- "loop": A boolean (`true`/`false`). If `true`, the track will repeat when it finishes. If `false`, the program will fall silent when the track ends
- "end_ms": An integer or `null`. If an integer is provided, a cue will automatically trigger that many milliseconds after the track starts. If `null`, manually cueing is required
- "fade_in_ms": An integer number of milliseconds the track will fade in over
- "fade_out_ms": An integer number of milliseconds the track will fade out over after a cue is fired. Note that the cue will start the next track immediately, allowing crossfade. If you don't want crossfade, create a silent track in between

Run the program with `python main.py <config name>`. To run one of the demos, use:
```
python main.py demo1
```

#### Licensing
- My code: Entirely free for use, modification, and redistribution
- Demo music:
  - Ambient Loop by Baharuth - Owned by me. Entirely free for use, modification, and redistribution. Check him out on Fiver. He does great work.
  - Everything else (Guzheng City, I Got A Stick, Loping Sting, Space Jazz, Strength of the Titans) - Kevin MacLeod (incompetech.com). Licensed under Creative Commons: By Attribution 4.0
