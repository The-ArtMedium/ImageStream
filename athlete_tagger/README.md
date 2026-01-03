
# Athlete Tagger

Batch scan a folder → detect famous athletes → append clean names to filename.

Example:  
`DSC_1234.jpg` → `DSC_1234_UsainBolt_LionelMessi.jpg`

## Setup
1. Create `references/` folder here
2. Add one clear face photo per athlete (name file anything)
3. Update KNOWN_ATHLETES dict in `athlete_tagger.py`

## Run
```bash
python athlete_tagger.py /path/to/your/images --dry-run   # Test first!
python athlete_tagger.py /path/to/your/images            # Go live
