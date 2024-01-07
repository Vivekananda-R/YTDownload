import typer
from enum import Enum
from typing import Annotated,Optional,List
from pytube import YouTube,Playlist
import os
import concurrent.futures

cli=typer.Typer()

class ResolutionTypes(str,Enum):
    low="low"
    high="high"
    p720="720p"
    p480="480p"
    p360="360p"
    p240="240p"
    p144="144p"

def download(url,folder=os.path.join(os.path.expanduser('~'),'Downloads'),resolution:ResolutionTypes=ResolutionTypes.p720
             ,name=None):
    try:
        yt_object=YouTube(url.strip('"'))
        print(yt_object.title)
    except Exception as e:
        return 'ERROR: The link is not recognized as a Youtube Link'
        
    try:
        if resolution=="high":
            video=yt_object.streams.get_highest_resolution()
        elif resolution=="low":
            video=yt_object.streams.get_lowest_resolution()
        else:
            video=yt_object.streams.get_by_resolution(resolution)
            
    except Exception as e:
        return 'ERROR: Provide a valid resolution'
    
    try:
        
        if name is None:
            path=video.download(fr'{folder}')
        else:
            path=video.download(fr'{folder}',filename_prefix=name)
            
        video_name=path.split('\\')[-1].replace('.mp4','')
        
    except Exception as e:
        return 'ERROR: Could\'nt download the video'
        
    return f'{video_name} is downloaded!!'



@cli.command()
def url_downloads(urls: Annotated[List[str],typer.Argument(help="Provide youtube video url, multiple urls separated by spaces")]=None,
                  playlist:Annotated[Optional[List[str]],typer.Option('--playlist','-p',help="Provide a playlist link for downloading whole playlist")]=None,
                  folder:Annotated[str,typer.Option('--folder','-f',help="Provide a folder path for download")]=os.path.join(os.path.expanduser('~'),'Downloads'),
                  resolution:Annotated[ResolutionTypes,typer.Option('--resolution','-r',case_sensitive=False,
                            help="Provide video resolution types from [high,low,p720,p480,p360,p240]")]=ResolutionTypes.p720,
                  name:Annotated[str,typer.Option('--name','-n',help="Provide a prefix name for single YT video download")]=None):
    
    if not urls and not playlist:
        if folder!=os.path.join(os.path.expanduser('~'),'Downloads'):
            print("ERROR: Please provide a YouTube link to download")
        else:
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
    
    result=[] 
      
    if playlist is not None:
        # print(playlist)
        
        for p in playlist:
            if "list=PL" not in p:
                print(f"NOTE: The link \"{p}\" is a Normal YouTube video link, please remove -p flag and try again")
                continue
            pl=Playlist(p)
              
            print("Please wait while downloading the Playlist:",pl.title)
            with concurrent.futures.ThreadPoolExecutor(max_workers=(os.cpu_count())//2) as executor:
                threads=[]
                for i,u in enumerate(pl.video_urls):    
                    if "youtube" not in u:
                        print(f"ERROR: {u} is not a valid youtube link\n\tProvide a vaild url starting with 'http://www.youtube.com/'")
                        continue
                    try:
                        yt_object=YouTube(u.strip('"'))
                        print(yt_object.default_filename)
                    except Exception as e:
                        print(f"ERROR: The link \"{u}\" for {yt_object.title} is not recognized as a Youtube Link")
                        continue 
                    name=fr'{i+1}- '
                    
                    u=u.split("&t")[0]
                
                    threads.append(executor.submit(download, u,folder,resolution,name))
                    
                for future in concurrent.futures.as_completed(threads):
                    result.append(future.result())
                
            
                
    if urls is not None:
        # print(urls)
        if len(urls)==1:
            print('Please wait while downloading the video:')    
            if "youtube" not in urls[0]:
                print(f"ERROR: {urls[0]} is not a valid youtube link\n\tProvide a vaild url starting with 'http://www.youtube.com/'")
                return 
            if "list=PL" in urls[0]:
                print(f"NOTE: The link is a Playlist, please use -p flag to download a playlist!")
                return
            result.append(download(urls[0].split("&t")[0],folder,resolution,fr'{name} - ' if name is not None else None))
            
        else:    
            print('Please wait while downloading videos:')
                
            with concurrent.futures.ThreadPoolExecutor(max_workers=(os.cpu_count())//2) as executor:
                    threads=[]
                    for u in urls:
                        if "youtube" not in u:
                            print(f"ERROR: {u} is not a valid youtube link\n\tProvide a vaild url starting with 'http://www.youtube.com/'")
                            continue
                        if "list=PL" in u:
                            print(f"NOTE: The link is a Playlist, please use -p flag to download a playlist!")
                            continue
                        u=u.split("&t")[0]
                        threads.append(executor.submit(download, u,folder,resolution,None))
                        
                    for future in concurrent.futures.as_completed(threads):
                        result.append(future.result())
    
    if result is not None:
        if len(result)>0:
            for r in result:
                print(r)
                
if __name__=="__main__":
    cli()
