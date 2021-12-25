import io
import os
import requests
import re
from bs4 import BeautifulSoup
import  io

linkDics = [] #Chứa các đường link thu thập được
linknImageDownloaded = [] # Chứa các đường link của hình ảnh đã download

LevelDownload = 3 #Số cấp web mà chương trình truy cập vào

MinWidth = 200 # Chieu rong toi thieu cua Hinh anh can download
MinHeight = 200 # Chieu cao toi thieu cua Hinh anh can download

MaxnImageDownload = 1000 # So luong hinh anh download toi da


nImageDownload = 1 #Biến đếm Số hình ảnh mà chương trình đã Download

from urllib import request as ulreq
from PIL import ImageFile

#Download file neu thoa man dieu kien
def download_file(uri):
    global nImageDownload
    file = ulreq.urlopen(uri)
    size = file.headers.get("content-length")
    if size: 
        size = int(size)

    buffer = io.BytesIO()

    while True:
        data = file.read(1024)
        if not data:
            break
        buffer.write(data)
    
    p = ImageFile.Parser()
    p.feed(buffer.getbuffer())
    if p.image:
        imgW = p.image.size[0]
        imgH = p.image.size[1]
        if (imgW > MinWidth  and imgH > MinHeight ):                
            nImageDownload = nImageDownload + 1
            local_filename = './image_download/'+uri.split('/')[-1]
            with open(local_filename, "wb") as f:
                f.write(buffer.getbuffer())        
        return size, (imgW, imgH)    
    return (size, (0,0))

#Loc lay cac Url va link hinh anh
def getLinkDics(URL,level):
    if nImageDownload > MaxnImageDownload:
        return
    domain = "";
    endSlat  = 0
    if (URL.startswith("http://")):
        endSlat = URL.index("/", 9)
    else:
        if (URL.startswith("https://")):
            endSlat = URL.index("/", 10)
    
    if endSlat==0: 
        return
    
    domain = URL[0:endSlat]
    
    print("Process:", URL,' Level:' , level)

    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")

    pageLink = []
    aTags = soup.find_all("a")
    for aTag in aTags :
        href = aTag.get('href', '#')
        if (href != "") and (href != "#"):
            if href.startswith("/"):
                link = domain + href
                if link not in linkDics:
                    linkDics.append(link)
                    pageLink.append(link)

    imgTags = soup.find_all("img")
    for imgTag in imgTags :
        if nImageDownload > MaxnImageDownload:
            return
        ImgSrc = imgTag.get('src', '')
        if (ImgSrc!='' and (ImgSrc.startswith("http://") or ImgSrc.startswith("https://")) and ImgSrc not in linknImageDownloaded):
            linknImageDownloaded.append(ImgSrc)
            imginfo  = download_file(ImgSrc)
            if (imginfo[1][0]>200 and imginfo[1][1]>200):
                print("Download:",imginfo,' Url:',ImgSrc)

    if (level<LevelDownload):
        for link in pageLink:
            getLinkDics(link,level + 1)
    

def main():
    url = "https://tuoitre.vn/"
    getLinkDics(url,1)    
main()