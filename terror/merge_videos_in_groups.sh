#/bin/bash
# Loop and pick 10 videos at random from the folder videos and move them to the folder videos_ya_subidos until there are no more videos

while [ $(find videos -type f -name '*.mp4' | wc -l) -gt 0 ]; do
    # Find all video files in the 'videos' directory, shuffle the list, pick the top 10, and move them to videos_ya_subidos
    find videos -type f -name '*.mp4' | shuf -n 10 | while read file; do
        mv "$file" "videos_ya_subidos/${file#videos/}"
    done

    # Merge the videos
    pipenv run python video_merger.py

    # Remove the merged videos
    rm videos_ya_subidos/*.mp4
done