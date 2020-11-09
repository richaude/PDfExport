# PDfExport
This is a place where I store my scripts to create a pdf from an IIIF resource.
## Prerequisites
Python 3 is required.
## Set Up
```pip install requests```  
```pip install beautifulsoup4```  
```pip install lxml```  
```pip install fpdf```
## Execute it
Currently, the .jpg files will temporarily be in the same directory as the script. It is supposed to work for every manifest.json that follows the iiif standard, so the value of this variable can be as you like (as long as it is still a valid manifest.json, of course). For utf-8 encoding you need to have the ```fonts``` folder in this repository (as it is here).  
```git clone https://github.com/richaude/PdfExport.git```  

```cd PdfExport```  
### Download the whole document
```python merge.py "manifest.json" "width"```  

where manifest.json is the url to your iiif object and width is a number, ideally between 500, 1000 or 1500 (it's the width of each image in pixels). When not specified, a width of 1000 pixels is used.
### Download a range
```python merge.py "manifest.json" "width" "rangeId"```  
where rangeId is the url to a range (for example ```https://iiif.ub.uni-leipzig.de/0000030884/range/LOG_0006```)
### Download a custom section of pages  
```python merge.py "manifest.json" "width" startpage endpage```  

where startpage and endpage are the equivalent page numbers you want the document to start and to end with (both inclusive). The values for startpage and endpage don't have to be put in quotation marks.  
## Example commands
+ To download the whole pdf of for example https://iiif.ub.uni-leipzig.de/0000030913/manifest.json with an image width of 1000 pixels, do:  
```python merge.py "https://iiif.ub.uni-leipzig.de/0000030913/manifest.json" "1000"```    

+ To download a pdf of the "Einleitung", which is the range with the ID *https://iiif.ub.uni-leipzig.de/0000030913/range/LOG_0004*, with an image width of 1000 pixels, do:  
```python merge.py "https://iiif.ub.uni-leipzig.de/0000030913/manifest.json" "1000" "https://iiif.ub.uni-leipzig.de/0000030913/range/LOG_0004"```  

+ To download a custom section of pages as pdf, say from page 14 to page 21, with an image width of 900 pixels do:  
```python merge.py "https://iiif.ub.uni-leipzig.de/0000030913/manifest.json" "900" 14 21```
