# klms-video-downloader
KLMS video downloader in Python 3 (USE AT YOUR OWN RISK!)


## Requirements
Refer main.py to see the full list of required packages.


## How-to
`download_video(packet_path, out_path)` requires two arguments:

* `packet_path`: the URL of the network request for the video file.
You can get it via, for example, the app named 'HttpCanary' on Android.
Click the 'Watch VOD' button with the packet capturing enabled.
And copy the URL, of some request, 
which starts with `http://143.248.2.29:1935/streams/`.
* `out_path`: the (relative or absolute) path of the output file.


