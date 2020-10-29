from fpdf import FPDF
import requests
import json
import time
import sys
import os

def getJson(manifest):
	myJson = requests.get(manifest).content
	myDict = json.loads(myJson)
	return myDict

def write(manifest):
	myDict = getJson(manifest)
	pdf = FPDF()
	pdf.add_page()
	pdf.set_font('Arial', 'B', 16)
	metadata = myDict['metadata']
	#headline = metadata[0]['value']
	headline = myDict['label']
	pdf.cell(40, 10, headline)
	pdf.ln(h = '10')
	pdf.set_font('Arial', '', 12)
	pdf.cell(40, 10, manifest)
	pdf.ln(h = '10')
	attributionL = myDict['attribution'].split("<br/>")
	for chunk in attributionL:
		pdf.cell(40, 10, chunk)
		pdf.ln(h = '10')
	pdf.cell(40, 10, myDict['license'])
	pdf.ln(h = '10')
	makeMeta(metadata, pdf)
	length = len(myDict['sequences'][0]['canvases'])
	#print(str(length))
	merge(pdf, length)
	# Was dient als prägnanter Dateiname???
	pdf.output(headline+".pdf", 'F')
	
def makeMeta(metadata, pdf):
	pdf.set_font('Arial', 'B', 16)
	pdf.cell(40, 10, "Metadaten")
	pdf.ln(h = '10')
	pdf.set_font('Arial', '', 12)
	for entry in metadata:
		line = entry['label']+": "+entry['value']
		pdf.cell(40, 10, line)
		pdf.ln(h = '10')

def merge(pdf, length):
	slide = '00000001'
	count = 0
	#while slide+".jpg" is not None:
	while count < length:
		pdf.add_page()
		pdf.image(slide+".jpg", x=0, y=0, w=200) # parameter w und h müssen evtl. als Variablen übergeben werden
		os.remove(slide+".jpg")
		print("Verarbeite Bild "+str(count+1)+" von "+str(length))
		slide = str(int(slide) + 1).zfill(len(slide))
		count += 1
		
def getImageLocation(manifest):
	myDict = getJson(manifest)
	sequences = myDict['sequences']
	canvases = sequences[0]['canvases']
	i=1
	for canvas in canvases:
		imageId = canvas['images'][0]['resource']['service']['@id']
		#print(imageId)
		print("Lade Bild "+str(i)+" von "+str(len(canvases)))
		i+=1
		getImage(getImageLink(imageId))
		
def getImageLink(imageId):
	imageLink = namespace+imageId[35:]+'/full/'+pixelbreite+'/0/default.jpg'
	#print(imageLink)
	return imageLink
	
def getSlideNumber(url):
	hinteresEnde = 24+len(pixelbreite)
	slideNumber = url[83:-hinteresEnde]
	return slideNumber
	
def getImage(url):
	slideNumber = getSlideNumber(url)
	with open(slideNumber+".jpg", 'wb') as f:
		f.write(requests.get(url).content)

manifest = sys.argv[1]
pixelbreite = "1000," # wenn w bei 100, dann ist 500 besser, wenn w bei 200, dann 1000
namespace = 'https://iiif.ub.uni-leipzig.de/fcgi-bin/iipsrv.fcgi?iiif='

start = time.time()
getImageLocation(manifest)
write(manifest)
end = time.time()
print("Laufzeit: "+str(end - start)+" Sekunden.")

