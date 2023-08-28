import streamlit as st
from utils import *

# subreddit = 'stories'
# limit = 1
# timeframe = 'month' #hour, day, week, month, year, all
# listing = 'top' # controversial, best, hot, new, random, rising, top
made=False
open_file()
with st.sidebar:
    subreddit=st.text_input('subreddit')
    limit=st.number_input('limit')
    timeframe=st.text_input('timeframe')
    listing=st.text_input('listing')

    # limit=int(limit)

    limit = int(limit) if limit > 0 else 1

    if st.button('generate'):
        make_video(subreddit, listing, limit, timeframe)
        made=True




if made==True:
    video_file = open('output_video.mp4', 'rb')
    video_bytes = video_file.read()
    st.video(video_bytes)
    st.download_button('Download Video', video_bytes, 'reddit_tiktok_video.mp4', mime='video/mp4')
