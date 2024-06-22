#!/bin/bash
echo "Starting video merge in groups process..."

# Loop and pick 10 videos at random from the folder videos and move them to the folder videos_ya_subidos until there are no more videos
while [ $(find videos -type f -name '*.mp4' | wc -l) -gt 0 ]; do
    echo "************************************************************"
    echo "Finding and moving 10 random videos..."
    # Find all video files in the 'videos' directory, shuffle the list, pick the top 10, and move them to videos_ya_subidos
    find videos -type f -name '*.mp4' | shuf -n 10 | while read file; do
        mv "$file" "videos_ya_subidos/${file#videos/}" && echo "Moved $file to videos_ya_subidos/" || { echo "Failed to move file $file"; exit 1; }
    done

    echo "Attempting to merge videos..."
    # Merge the videos and check if the command succeeds
    if pipenv run python video_merger.py; then
        echo "Video merge successful. Moving the original files to videos_discarded..."
        # Move the merged videos to videos_discarded
        mv videos_ya_subidos/*.mp4 videos_discarded/ && echo "Merged videos moved to videos_discarded successfully." || { echo "Failed to move merged videos to videos_discarded"; exit 1; }
    else
        echo "Video merge failed. Exiting."
        exit 1
    fi
done

echo "Video merge in groups process completed."