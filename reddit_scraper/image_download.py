#!/usr/bin/python3
# cat pics.txt | xargs -n 100 -I % sh -c " { ./image_download.py --link \"%\" --destination ./pics; } "
# ls -1 *.jpg | xargs -n 1 bash -c 'convert "$0" "${0%.jpg}.png"'
# ls | xargs -n 100 -I % sh -c "{ convert ./% -resize 480x360! ../resized_cats/%; }"

import requests
import argparse
import uuid
import shutil
import hashlib

def main(args):

	save_dir = args.destination
	if( save_dir == None ):
		save_dir = "./"
	if( args.link == None ):
		raise Exception( "Must include link argument" )
	link = args.link

	id_name = hashlib.sha224( link.encode() ).hexdigest()
	response = requests.get( link, stream=True )
	

	if( ( "jpg" in link.lower() ) | ( "jpeg" in link.lower() ) ):
		id_name += ".jpg"
	elif( "png" in link.lower() ):
		id_name += ".png"

	with open( save_dir + "/" + id_name, 'wb') as out_file:
		shutil.copyfileobj(response.raw, out_file)


if __name__ == "__main__":

	parser = argparse.ArgumentParser( description='Download the url, if applicable' )
	parser.add_argument( '--link', type=str, help='a url pointing to a png or jpg to be downloaded' )
	parser.add_argument( '--destination', type=str, help='location to download the file to' )
	args = parser.parse_args()
	main( args )
