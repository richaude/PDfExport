import fpdf
import json
import requests
import os
import sys
import time
from bs4 import BeautifulSoup
# pip install beautifulsoup4
# pip install lxml
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
	with open(str(count)+'.jpg', 'wb') as f:
		f.write(requests.get(url).content)
		
def checkHtml(entry):
	soup = BeautifulSoup(entry, 'lxml')
	links = soup.find_all('a')
	if len(links) == 1:
		entry = ''
		for a in links:
			entry += a.text
		return [entry, a['href']] # if there is one link in the entry, we give back the text of the link and the url
	else:
		return [entry]
	# can be expanded for other html tags as well


def writeMeta(metadata, pdf):
	pdf.set_font('NotoSans', 'B', 16)
	pdf.cell(40, 10, 'Metadata')
	pdf.ln(h = '10')
	pdf.set_font('NotoSans', '', 12)
	for entry in metadata:
		checked = checkHtml(entry['value'])
		if len(checked) == 2: # if there is one link, we leave the label as it is, but turn the value into a link, the text of the link shows in the document, but it points to the url 
			pdf.cell(40, 10, entry['label']+': ')
			pdf.set_text_color(0, 0, 255)
			pdf.cell(40, 10, checked[0], link = checked[1])
			pdf.set_text_color(0, 0, 0)
			pdf.ln(h = '10')
		else:
			line = entry['label']+': '+checked[0]
			pdf.multi_cell(180, 10, line)
	
def makeFrontpage(manifestDict, label):
	pdf = fpdf.FPDF()
	pdf.add_font('NotoSans', style='', fname='NotoSans-Regular.ttf', uni=True)
	pdf.add_font('NotoSans', style='B', fname='NotoSans-Bold.ttf', uni=True)
	pdf.add_font('NotoSans', style='I', fname='NotoSans-Italic.ttf', uni=True)
	pdf.add_font('NotoSans', style='BI', fname='NotoSans-BoldItalic.ttf', uni=True)
	#pdf.set_doc_option('core_fonts_encoding', 'utf-8')
	pdf.add_page()
	headline = None
	attributionL = None
	lizenz = None
	headline = manifestDict['label']
	pdf.set_font('NotoSans', '', 16)
	if headline is not None:
		pdf.multi_cell(180, 10, headline)
		#pdf.ln(h = '10')
	if label != '':
		pdf.set_font('NotoSans', 'B', 16)
		pdf.multi_cell(180, 10, label)
	pdf.set_font('NotoSans', '', 12)
	pdf.cell(40, 10, manifest)
	pdf.ln(h = '10')
	attributionL = manifestDict['attribution'].split('<br/>')
	if attributionL is not None:
		for chunk in attributionL:
			pdf.multi_cell(180, 10, chunk)
			#pdf.ln(h = '10')
	if lizenz is not None:
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

def addImagesToPdf(manifestDict):
	f = makeFrontpage(manifestDict, '')
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
	
	
def getRange(manifestDict, rangeId):
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
					getImage(imageId, count)
					print('Processing image '+str(count)+' of '+str(len(structure['canvases'])))
					f.add_page()
					f.image(str(count)+'.jpg', x=0, y=0, w=200) # Mind the parameter w!
					os.remove(str(count)+'.jpg')
					count += 1
				title = manifestDict['label'] + structure['label']
				print('Processing file...')
				f.output(title+'.pdf', 'F')

def customPageNumbers(manifestDict, start, end):
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
			getImage(imageId, count)
			print('Processing image '+str(count)+' of '+str(len(canvasSlice)))
			f.add_page()
			f.image(str(count)+'.jpg', x=0, y=0, w=200) # w might need to get adapted
			os.remove(str(count)+'.jpg')
			count += 1
		title = manifestDict['label']+',pages'+str(start)+'-'+str(end)
		print('Processing file...')
		f.output(title+'.pdf', 'F')
				


start = time.time()

if len(sys.argv) >= 1:
	manifest = sys.argv[1] # the manifest.json url
	manifestDict = getJson(manifest)

	if len(sys.argv) == 2:
		print('No width provided! Using a default width of 1000 pixels.')
		width = '1000'
		addImagesToPdf(manifestDict)
	else:
		width = sys.argv[2] # width of the image in pixels

		if len(sys.argv) == 3:
			addImagesToPdf(manifestDict)


		if len(sys.argv) == 4:
			rangeId = sys.argv[3] # ID of a range like "https://iiif.ub.uni-leipzig.de/0000030884/range/LOG_0011"
			getRange(manifestDict, rangeId)
			
		if len(sys.argv) == 5:
			try:
				startPage = int(sys.argv[3]) # starting page of your custom section
				endPage = int(sys.argv[4]) # ending page
				if startPage > endPage:
					print("The starting page can't have a higher value than the ending page!")
				else:
					customPageNumbers(manifestDict, startPage, endPage)
			except:
				print("No valid numbers for the pages have been entered!")
else:
	print('No Json provided!')
	
end = time.time()
print('Done! Time used: '+str(end - start)+' seconds.')

# Jsons for testing:
# https://iiif.ub.uni-leipzig.de/0000000001/manifest.json (https://papyrusebers.de/)
