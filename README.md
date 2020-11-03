# PDfExport
This is a place where I store my scripts to create a pdf from an IIIF resource.
## Prerequisites
Python 3 is required.
## Set Up
```pip install requests```  

```pip install fpdf```
## Execute it
Currently, the .jpg files will temporarily be in the same directory as the script. It is supposed to work for every manifest.json that follows the iiif standard, so the value of this variable can be as you like (as long as it is still a valid manifest.json, of course).  
```git clone https://github.com/richaude/PdfExport.git```  

```cd PdfExport```  
```python3 merge.py "manifest.json" "width"```  
where manifest.json is the url to your iiif object and width is a number, ideally between 500, 1000 or 1500 (it's the width of each image in pixels).
