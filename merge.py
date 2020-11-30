import fpdf
import json
import requests
import os
import sys
import time
from PIL import Image
# python3 -m pip install --upgrade pip
# python3 -m pip install --upgrade Pillow

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
	
	
def getImage(imageId, count, width):
	url = imageId+'/full/'+width+',/0/default.jpg'
	with open(str(count)+'.jpg', 'wb') as f:
		f.write(requests.get(url).content)


def writeMeta(metadata, pdf):
	pdf.set_font('NotoSans', 'B', 16)
	pdf.cell(40, 10, 'Metadata')
	pdf.ln(h = '10')
	pdf.set_font('NotoSans', '', 12)
	for entry in metadata:
		pdf.multi_cell(180, 10, entry['label']+': '+entry['value'])
	
def makeFrontpage(manifestDict, label):
	pdf = fpdf.FPDF()
	#pdf.set_doc_option('core_fonts_encoding', 'utf-8')
	pdf.add_font('NotoSans', style='', fname='NotoSans-Regular.ttf', uni=True)
	pdf.add_font('NotoSans', style='B', fname='NotoSans-Bold.ttf', uni=True)
	#pdf.add_font('NotoSans', style='I', fname='NotoSans-Italic.ttf', uni=True)
	#pdf.add_font('NotoSans', style='BI', fname='NotoSans-BoldItalic.ttf', uni=True)
	pdf.add_page()
	description = None
	headline = None
	attributionL = None
	lizenz = None
	description = manifestDict['description']
	headline = manifestDict['label']
	#print("headline: "+headline)
	pdf.set_font('NotoSans', '', 16)
	if headline is not None:
		pdf.multi_cell(180, 10, headline)
		#pdf.ln(h = '10')
	if label != '':
		print("label: "+label)
		pdf.set_font('NotoSans', 'B', 16)
		pdf.multi_cell(180, 10, label)
	pdf.set_font('NotoSans', '', 12)
	pdf.cell(40, 10, manifest)
	pdf.ln(h = '10')
	if description is not None:
		pdf.multi_cell(180, 10, description)
	attributionL = manifestDict['attribution'].split('<br/>')
	if attributionL is not None:
		for chunk in attributionL:
			#print("Attribution: "+chunk)
			pdf.multi_cell(180, 10, chunk)
			#pdf.ln(h = '10')
	if lizenz is not None:
		print("Lizenz: "+lizenz)
		pdf.multi_cell(180, 10, manifestDict['license'])
		#pdf.ln(h = '10')
	metadata = None
	try:
		metadata = manifestDict['metadata']
		if metadata is not None:
			writeMeta(metadata, pdf)
	except:
		pass
	finally:
		return pdf

def addImagesToPdf(manifestDict, width):
	f = makeFrontpage(manifestDict, '')
	sequences = manifestDict['sequences']
	canvases = sequences[0]['canvases']
	count = 1
	for canvas in canvases:
		imageId = canvas['images'][0]['resource']['service']['@id']
		getImage(imageId, count, width)
		print('Processing image '+str(count)+' of '+str(len(canvases)))
		imageName = str(count)+'.jpg'
		form = imageSizing(imageName)
		imageWidth = form[0]
		imageHeight = form[1]
		orientation = form[2]
		marginWidth = form[3]
		marginHeight = form[4]
		f.add_page(orientation)
		f.image(imageName, marginWidth, marginHeight, imageWidth, imageHeight)
		os.remove(str(count)+'.jpg')
		count += 1
	title = manifestDict['label']
	#pdf.output(dest='S').encode('latin-1','ignore')
	print('Processing file...')
	f.output(title+'.pdf', 'F')
	
def getImageIdRange(manifestDict, canvasId):
	sequences = manifestDict['sequences']
	canvases = sequences[0]['canvases']
	count = 0
	while canvases[count]['@id'] != canvasId:
		count += 1
		if count > len(canvases):
			print('Canvas-ID could not be found!')
			break
	imageId = canvases[count]['images'][0]['resource']['service']['@id']
	return imageId
	
	
def getRange(manifestDict, rangeId, width):
	sequences = manifestDict['sequences']
	structures = manifestDict['structures']
	for structure in structures:
		if rangeId == structure['@id']:
			# not working for the very first with label: content
			if len(structure['canvases']) > 0:
				f = makeFrontpage(manifestDict, structure['label'])
				count = 1
				for canvas in structure['canvases']:
					imageId = getImageIdRange(manifestDict, canvas)
					getImage(imageId, count, width)
					print('Processing image '+str(count)+' of '+str(len(structure['canvases'])))
					imageName = str(count)+'.jpg'
					form = imageSizing(imageName)
					imageWidth = form[0]
					imageHeight = form[1]
					orientation = form[2]
					marginWidth = form[3]
					marginHeight = form[4]
					f.add_page(orientation)
					f.image(imageName, marginWidth, marginHeight, imageWidth, imageHeight)
					os.remove(str(count)+'.jpg')
					count += 1
				title = manifestDict['label'] + structure['label']
				print('Processing file...')
				f.output(title+'.pdf', 'F')

def customPageNumbers(manifestDict, start, end, width):
	f = makeFrontpage(manifestDict, '- pages '+str(start)+' to '+str(end))
	sequences = manifestDict['sequences']
	canvases = sequences[0]['canvases']
	if start > len(canvases) or end > len(canvases):
		print("The numbers you have entered are too high for the specified document.")
	else:
		canvasSlice = canvases[start-1:end]
		count = 1
		for canvas in canvasSlice:
			imageId = canvas['images'][0]['resource']['service']['@id']
			getImage(imageId, count, width)
			print('Processing image '+str(count)+' of '+str(len(canvasSlice)))
			imageName = str(count)+'.jpg'
			form = imageSizing(imageName)
			imageWidth = form[0]
			imageHeight = form[1]
			orientation = form[2]
			marginWidth = form[3]
			marginHeight = form[4]
			f.add_page(orientation)
			f.image(imageName, marginWidth, marginHeight, imageWidth, imageHeight)
			os.remove(str(count)+'.jpg')
			count += 1
		title = manifestDict['label']+',pages'+str(start)+'-'+str(end)
		print('Processing file...')
		f.output(title+'.pdf', 'F')
		
def imageSizing(imageName):
    # from https://stackoverflow.com/questions/43767328/python-fpdf-not-sizing-correctly
	cover = Image.open(imageName)
	width, height = cover.size

    # convert pixel in mm with 1px=0.264583 mm
	width, height = float(width * 0.264583), float(height * 0.264583)

    # given we are working with A4 format size 
	pdf_size = {'P': {'w': 210, 'h': 297}, 'L': {'w': 297, 'h': 210}}

    # get page orientation from image size 
	orientation = 'P' if width < height else 'L'

    #  make sure image size is not greater than the pdf format size
	width = width if width < pdf_size[orientation]['w'] else pdf_size[orientation]['w']
	height = height if height < pdf_size[orientation]['h'] else pdf_size[orientation]['h']
	
	marginHeight = 0
	marginWidth = 0
	
	# if the height of an image is less than a4, center the image vertically
	if height < pdf_size[orientation]['h']:
		# creating upper and bottom margin
		marginHeight = (pdf_size[orientation]['h'] - height) / 2.0
		
	# same with the width
	if width < pdf_size[orientation]['w']:
		marginWidth = (pdf_size[orientation]['w'] - width) / 2.0
   
	return [width, height, orientation, marginWidth, marginHeight]
   


    
				


start = time.time()

if len(sys.argv) >= 1:
	manifest = sys.argv[1] # the manifest.json url
	manifestDict = getJson(manifest)

	if len(sys.argv) == 2:
		print('No width provided! Using a default width of 1000 pixels.')
		width = '1000'
		addImagesToPdf(manifestDict, width)
	else:
		width = sys.argv[2] # width of the image in pixels

		if len(sys.argv) == 3:
			addImagesToPdf(manifestDict, width)


		if len(sys.argv) == 4:
			rangeId = sys.argv[3] # ID of a range like "https://iiif.ub.uni-leipzig.de/0000030884/range/LOG_0011"
			getRange(manifestDict, rangeId, width)
			
		if len(sys.argv) == 5:
			try:
				startPage = int(sys.argv[3]) # starting page of your custom section
				endPage = int(sys.argv[4]) # ending page
				if startPage > endPage:
					print("The starting page can't have a higher value than the ending page!")
				else:
					customPageNumbers(manifestDict, startPage, endPage, width)
			except:
				print("No valid numbers for the pages have been entered!")
else:
	print('No Json provided!')
	
end = time.time()
print('Done! Time used: '+str(end - start)+' seconds.')

# Jsons for testing:
# https://iiif.ub.uni-leipzig.de/0000000001/manifest.json (https://papyrusebers.de/), wegen Proportionen
# https://iiif.bodleian.ox.ac.uk/iiif/manifest/e800b13a-6699-49ae-9bc2-c9b8c35b7a25.json, wegen Kodierung der Metadaten und den Html Tags
