import fpdf
import json
import requests
import os
import sys
import time
fpdf.set_global("SYSTEM_TTFONTS", os.path.join(os.path.dirname(__file__),'fonts'))
# using NotoSans from https://www.google.com/get/noto/
# solution from here: https://stackoverflow.com/a/57360249/12616125 (otherwise there could be a UnicodeEncoding Error, fpdf uses latin-1


def getJson(manifest):
	try:
		myJson = requests.get(manifest).content
		#myJson.encode('utf-8')
		#myJson = myJson.encode('latin-1', 'replace').decode('latin-1')
		#print(myJson)
		myDict = json.loads(myJson)
		return myDict
	except:
		print('No valid input.')
		return None
	
	
def getImage(imageId, count):
	url = imageId+'/full/'+width+',/0/default.jpg'
	with open(str(count)+".jpg", 'wb') as f:
		f.write(requests.get(url).content)

def writeMeta(metadata, pdf):
	pdf.set_font('NotoSans', 'B', 16)
	pdf.cell(40, 10, "Metadata")
	pdf.ln(h = '10')
	pdf.set_font('NotoSans', '', 12)
	for entry in metadata:
		line = entry['label']+": "+entry['value']
		pdf.cell(40, 10, line)
		pdf.ln(h = '10')
	
def makeFrontpage(manifestDict):
	pdf = fpdf.FPDF()
	pdf.add_font("NotoSans", style="", fname="NotoSans-Regular.ttf", uni=True)
	pdf.add_font("NotoSans", style="B", fname="NotoSans-Bold.ttf", uni=True)
	pdf.add_font("NotoSans", style="I", fname="NotoSans-Italic.ttf", uni=True)
	pdf.add_font("NotoSans", style="BI", fname="NotoSans-BoldItalic.ttf", uni=True)
	#pdf.set_doc_option('core_fonts_encoding', 'utf-8')
	pdf.add_page()
	headline = None
	attributionL = None
	lizenz = None
	headline = manifestDict['label']
	pdf.set_font('NotoSans', 'B', 16)
	if headline is not None:
		pdf.multi_cell(180, 10, headline)
		pdf.ln(h = '10')
	pdf.set_font('NotoSans', '', 12)
	pdf.cell(40, 10, manifest)
	pdf.ln(h = '10')
	attributionL = manifestDict['attribution'].split("<br/>")
	if attributionL is not None:
		for chunk in attributionL:
			pdf.cell(40, 10, chunk)
			pdf.ln(h = '10')
	if lizenz is not None:
		pdf.cell(40, 10, manifestDict['license'])
		pdf.ln(h = '10')
	metadata = None
	try:
		metadata = manifestDict['metadata']
		if metadata is not None:
			writeMeta(metadata, pdf)
	except:
		#if metadata is not None:
			#writeMeta(metadata, pdf)
		pass
	finally:
		return pdf

def addImagesToPdf(manifestDict):
	f = makeFrontpage(manifestDict)
	sequences = manifestDict['sequences']
	canvases = sequences[0]['canvases']
	count = 1
	for canvas in canvases:
		imageId = canvas['images'][0]['resource']['service']['@id']
		getImage(imageId, count)
		print('Processing image '+str(count)+' of '+str(len(canvases)))
		f.add_page()
		f.image(str(count)+'.jpg', x=0, y=0, w=200) # w might need to get adapted
		os.remove(str(count)+'.jpg')
		count += 1
	title = manifestDict['label']
	#pdf.output(dest='S').encode('latin-1','ignore')
	f.output(title+".pdf", 'F')


start = time.time()
manifest = None
width = None
manifest = sys.argv[1] # the manifest.json url
width = sys.argv[2] # width of the image in pixels
if manifest is not None: 
	manifestDict = getJson(manifest)
	#print(manifestDict)
	if width is not None:
		addImagesToPdf(manifestDict)
	else:
		print('No width provided! Using a default width of 1000 pixels.')
		width = "1000"
		addImagesToPdf(manifestDict)
else:
	print('No Json-Manifest provided!')
end = time.time()
print('Time used: '+str(end - start)+' seconds.')

	
