# PDfExport
This is a place where I store my scripts to create a pdf from an IIIF resource.
## Prerequisites
Python 3 is required. I'll upload the script to create/crawl the needed jpgs later on.
## Set Up
```pip install requests```  

```pip install fpdf```
## Execute it
Currently, the .jpg files need to be in the same directory as the script. It is supposed to work for every manifest.json, so the value of this variable can be as you like (as long as it is still a valid manifest.json, of course).  
```git clone https://github.com/richaude/PdfExport.git```  

```cd PdfExport/0000028794```  
```python3 merge.py```
