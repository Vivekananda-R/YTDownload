import typer
from typing import Annotated,Optional,List
from pytube import YouTube,Playlist
import os
import concurrent.futures

cli=typer.Typer()

def download(url,folder=os.path.join(os.path.expanduser('~'),'Downloads')):
    try:
        yt_object=YouTube(url.strip('"'))
    except Exception as e:
        return 'ERROR: The link is not recognized as a Youtube Link'
        
    try:
        video=yt_object.streams.get_highest_resolution()
        path=video.download(folder)
        video_name=path.split('\\')[-1].replace('.mp4','')
    except Exception as e:
        return 'ERROR: Could\'nt download the video'
        
    return f'{video_name} is downloaded!!'

@cli.command()
def url_downloads(urls: Annotated[List[str],typer.Argument(help="Provide youtube video url, multiple urls separated by spaces")]=None,
                  playlist:Annotated[Optional[List[str]],typer.Option('--playlist','-p',help="Provide a playlist link for downloading whole playlist")]=None,
                  folder:Annotated[str,typer.Option('--folder','-f',help="Provide a folder path for download")]=os.path.join(os.path.expanduser('~'),'Downloads')):
    print('''
Hi,
Welcome to ytdownload application!!
All in one place to download any youtube video
''')
    
    if not os.path.isdir(folder):
        if "." in folder:
            print("ERROR: Please provide a valid folder path!")
            return
        
        try:
            os.mkdir(folder)
        except Exception as e:
            print("ERROR: Folder could not be created!")
            return  
    
    if playlist is not None:
        # print(playlist)
        
        for p in playlist:
            if "list=PL" not in p:
                print(f"NOTE: The link \"{p}\" is a Normal YouTube video link, please remove -p flag and try again")
                continue
            pl=Playlist(p)
            print("Playlist:",pl.title)
            for u in pl.video_urls:
                urls.append(u)
            
                
    result=[]   
    if urls is not None:
        # print(urls)
        
        if len(urls)==1:
            if "youtube" not in urls[0]:
                print(f"ERROR: {urls[0]} is not a valid youtube link\n\tProvide a vaild url starting with 'http://www.youtube.com/'")
                return 
            if "list=PL" in urls[0]:
                print(f"NOTE: The link is a Playlist, please use -p flag to download a playlist!")
                return
            result.append(download(urls[0],folder))
            
        else:    
            with concurrent.futures.ThreadPoolExecutor(max_workers=(os.cpu_count())//2) as executor:
                    threads=[]
                    for u in urls:
                        if "youtube" not in u:
                            print(f"ERROR: {u} is not a valid youtube link\n\tProvide a vaild url starting with 'http://www.youtube.com/'")
                            continue
                        if "list=PL" in u:
                            print(f"NOTE: The link is a Playlist, please use -p flag to download a playlist!")
                            continue
                        threads.append(executor.submit(download, u,folder))
                        
                    for future in concurrent.futures.as_completed(threads):
                        result.append(future.result())
    


cli()
