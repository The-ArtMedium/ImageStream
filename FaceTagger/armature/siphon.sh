#!/bin/bash
# siphon_equestrian.sh - The Induction of the Equestrian Archive

echo "🏇 Starting Equestrian Archive Siphon..."
echo "========================================="

# Run the Tagger in "Processing Mode"
# This uses your improved python logic to match riders (athletes)
python3 athlete_tagger.py /path/to/your/fresh/equestrian/photos \
    --config armature/config/equestrian.yaml \
    --threshold 0.55 \
    --workers 4

# Push the results to the Filter (Meilisearch)
# This makes the "Fresh Archive" searchable on snowmanview.com
curl -X POST 'http://localhost:7700/indexes/photos/documents' \
     -H 'Content-Type: application/json' \
     -H "Authorization: Bearer ${MEILI_KEY}" \
     --data-binary @processed_metadata.json

echo "✅ Equestrian Induction Complete. The archive is now Resonant."
