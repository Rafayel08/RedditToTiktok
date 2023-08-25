# import json 
import pandas as pd
import requests
from tiktokvoice import *

  
subreddit = 'stories'
limit = 1
timeframe = 'month' #hour, day, week, month, year, all
listing = 'top' # controversial, best, hot, new, random, rising, top
  
def get_reddit(subreddit,listing,limit,timeframe):
    try:
        base_url = f'https://www.reddit.com/r/{subreddit}/{listing}.json?limit={limit}&t={timeframe}'
        request = requests.get(base_url, headers = {'User-agent': 'yourbot'})
    except:
        print('An Error Occured')
    return request.json()
 
def get_results(r):
    '''
    Create a DataFrame Showing Title, URL, Score and Number of Comments.
    '''
    myDict = {}
    for post in r['data']['children']:
        myDict[post['data']['title']] = {'title': post['data']['title'],'url':post['data']['url'],'score':post['data']['score'],'comments':post['data']['num_comments'], 'text': post['data']['selftext']}
        # print(post['data'])
    df = pd.DataFrame.from_dict(myDict, orient='index')
    return df

def subtitles_srt_creator(path_to_mp3):
    import subprocess
    # import sys

    from vosk import Model, KaldiRecognizer, SetLogLevel

    SAMPLE_RATE = 16000

    SetLogLevel(-1)

    model = Model(lang="en-us")
    rec = KaldiRecognizer(model, SAMPLE_RATE)
    rec.SetWords(True)

    with subprocess.Popen(["ffmpeg", "-loglevel", "quiet", "-i",
                                path_to_mp3,
                                "-ar", str(SAMPLE_RATE) , "-ac", "1", "-f", "s16le", "-"],
                                stdout=subprocess.PIPE).stdout as stream:
        result=rec.SrtResult(stream, words_per_line=1)

    srt_blocks = result.split('\n\n')

    with open('output.srt', 'w') as srt_file:
        for i, srt_block in enumerate(srt_blocks):
            if srt_blocks[i]==srt_blocks[-1]:
                pass
            else:
                lines = srt_block.strip().split('\n')
                # print(lines)
                sequence_number = lines[0]
                # print(sequence_number)
                time_range = lines[1]
                # print(time_range)
                subtitle_text = "\n".join(lines[2:])
                
                srt_file.write(f"{sequence_number}\n{time_range}\n{subtitle_text}\n\n")
                # print(srt_block)
    print("Subtitle file generated successfully.")

def get_background_video(youtube_url='https://www.youtube.com/watch?v=Pt5_GSKIWQM'):
    from pytube import YouTube

    youtube_url = youtube_url
    yt = YouTube(youtube_url)
    video_url = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().url

    # import requests

    response = requests.get(video_url)
    if response.status_code == 200:
        with open("background.mp4", "wb") as f:
            f.write(response.content)
        print("Video downloaded successfully.")
    else:
        print("Failed to download video.")



def make_video(subreddit, listing, limit, timeframe):

    get_background_video('https://www.youtube.com/watch?v=Pt5_GSKIWQM')

    # import os
    # os.environ["IMAGEIO_FFMPEG_EXE"] = "ffmpeg"
    from moviepy.editor import AudioFileClip, TextClip, VideoFileClip, CompositeVideoClip
    # import speech_recognition as sr
    # import datetime
    # from pydub import AudioSegment
    import random
    import string
    r = get_reddit(subreddit, listing, limit, timeframe)
    df = get_results(r)

    text = df['text'].iloc[0]

    # text=text[0:100]

    voice = "en_us_010"

    text = text.replace("’", "'")

    tts(text, voice, "output.mp3", play_sound=False)

    new_audio_path = "output.mp3"
    new_audio_clip = AudioFileClip(new_audio_path)

    background_video_path = "background.mp4"
    background_video_clip = VideoFileClip(background_video_path)

    snippet_duration = new_audio_clip.duration
    max_start_time = background_video_clip.duration - snippet_duration
    start_time = random.uniform(0, max_start_time)
    random_snippet = background_video_clip.subclip(start_time, start_time + snippet_duration)

    duration_of_audio_clip = new_audio_clip.duration
    random_snippet_without_audio = random_snippet.without_audio()
    random_snippet_with_new_audio = random_snippet_without_audio.set_audio(new_audio_clip)

    font = 'RedditToTiktok/Helvetica-Font/helvetica-rounded-bold-5871d05ead8de.otf'

    list_of_words_in_text = text.split()

    current_time = 0

    subtitles_srt_creator('output.mp3')

    srt_filename = 'output.srt'
    word_subtitles = open(srt_filename, "r").readlines()

    def get_seconds_from_srt_time(srt_time):
        # Split the SRT time into hours, minutes, seconds, and milliseconds
        parts = srt_time.split(':')
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds, milliseconds = map(int, parts[2].split(','))

        # Calculate the total time in seconds
        total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000
        return total_seconds
    
    def has_alphabet_letters(input_string):
        alphabet = set(string.ascii_lowercase)  # Set of lowercase letters

        for char in input_string:
            if char.lower() in alphabet:
                return True  # Found an alphabet letter in the string
        return False  # No alphabet letters found in the string

    def generate_subtitle_clips(subtitle_lines):
        clips = []
        current_time = 0
        for line in subtitle_lines:
            # print(line)
            # line_divided=line.strip().split('\n')
            # print(line_divided)
            if "-->" in line:  
                start, end = line.strip().split(" --> ")
                start_time = get_seconds_from_srt_time(start)
                end_time = get_seconds_from_srt_time(end)

                start_time = float(start_time)
                end_time = float(end_time)
                start_time=round(start_time, 3)
                end_time=round(end_time, 3)
                # print(line.strip())
                
                # Calculate the duration and start time for the text clip
                duration = end_time - start_time
            elif has_alphabet_letters(line):
                word_clip = TextClip(line, fontsize=24, color='white').set_duration(duration).set_position(('center', 'center'))
                word_clip=word_clip.set_start(start_time)
                clips.append(word_clip)
                # print(start_time)
                # print(end_time)
                # print(line)
            else:
                # Update current_time based on the audio duration of the previous text clip
                # current_time += new_audio_clip.duration
                pass
        return clips

    word_subtitle_clips = generate_subtitle_clips(word_subtitles)

    # print(word_subtitle_clips)

    final_clip = CompositeVideoClip([random_snippet_with_new_audio] + word_subtitle_clips)
    final_clip = final_clip.resize(height=1920)
    final_clip = final_clip.crop(x1=1166.6, y1=0, x2=2246.6, y2=1920)

    output_file = "output_video.mp4"
    final_clip.write_videofile(output_file, codec="libx264")

    background_video_clip.reader.close()
    background_video_clip.audio.reader.close_proc()
    new_audio_clip.reader.close_proc()
