# KLMS video downloader
# Requires Python >= 3.2 (maybe)
# USE AT YOUR OWN RISK!

import os
import ffmpeg
import requests
from concurrent.futures import ThreadPoolExecutor
import shutil


MAX_WORKERS = 2
USE_SYSTEM_FFMPEG = True
VERBOSE = False
REMOVE_TEMP = False


def download_video(packet_path, out_path="out.mp4"):
    if not os.path.exists("temp"):
        os.mkdir("temp")

    video_path = packet_path.split("/media_")[0]
    session_param = packet_path.split(".ts?")[1]

    def get_nth_video_path(n):
        return "%s/media_%i.ts?%s" % (video_path, n, session_param)

    def check_video_exists(n):
        try:
            r = requests.head(get_nth_video_path(n))
            return True if r.status_code == 200 else False

        except requests.ConnectionError:
            return False

    # https://math.stackexchange.com/questions/3165121/optimal-algorithm-to-guess-any-random-integer-without-limits
    def get_last_video(n=1):
        if check_video_exists(n):
            return get_last_video(2 * n) if check_video_exists(n + 1) else n

        else:
            # find the index of the last video on [n / 2, n[
            return binary_search(n // 2, n)

    def binary_search(from_, until):  # exclusive right end
        if until - from_ < 2:
            return from_

        mid = (from_ + until) // 2
        return binary_search(mid, until) if check_video_exists(mid) else binary_search(from_, mid)

    last_video_index = get_last_video()
    print("The number of video clips:", last_video_index)

    def download_clip(n):
        print("Downloading the clip #%i" % n)
        if USE_SYSTEM_FFMPEG:
            os.system("ffmpeg -y -i '%s' -map 0 %s -c copy temp/out%i.ts" % (
                get_nth_video_path(n),
                "" if VERBOSE else "-loglevel quiet",
                n
            ))
        else:
            (
                ffmpeg.input(get_nth_video_path(n))
                      .output("temp/out%i.ts" % n, quiet=not VERBOSE)
                      .overwrite_output()
                      .run()
            )

    try:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            executor.map(download_clip, range(1, last_video_index + 1))

        def alt_concat(lst1, lst2):
            return [sub[item] for item in range(len(lst2))
                    for sub in [lst1, lst2]]

        videos = alt_concat(
            [ffmpeg.input("temp/out%i.ts" % i)['v'] for i in range(1, last_video_index + 1)],
            [ffmpeg.input("temp/out%i.ts" % i)['a'] for i in range(1, last_video_index + 1)]
        )

        if USE_SYSTEM_FFMPEG:
            videos_string = "|".join(["temp/out%i.ts" % i for i in range(1, last_video_index + 1)])
            os.system("ffmpeg -y -i 'concat:%s' -safe 0 -map 0 %s -c copy %s" % (
                videos_string,
                "" if VERBOSE else "-loglevel quiet",
                out_path
            ))
        else:
            (
                ffmpeg.concat(*videos, a=1, unsafe=True)
                      .output(out_path, quiet=not VERBOSE)
                      .overwrite_output()
                      .run()
            )

        print("Download finished!")

    finally:
        if REMOVE_TEMP:
            shutil.rmtree("temp")


PACKET_PATH = "http://143.248.2.29:1935/streams/_definst_/d0a6a06a-79ed-4646-ae8b-3a281b5bbff2/2020/03/17/3f822ec9-9779-4855-8562-3bf0ffe1868f/705bd6b3-2b50-4d41-967c-caa5af47f92b.mp4/media_2.ts?wowzasessionid=2003513729"
download_video(PACKET_PATH)
