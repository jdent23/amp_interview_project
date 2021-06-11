#!/usr/bin/python3

import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

parser = argparse.ArgumentParser()

def main(args):

	if args.sub == None:
		raise Exception("Subreddit name required")

	results_file  = open(args.sub + ".txt", "a")

	binary = FirefoxBinary('/usr/bin/firefox')
	with webdriver.Firefox(firefox_binary=binary) as driver:
		wait = WebDriverWait(driver, 10)
		driver.get( 'https://old.reddit.com/r/' + args.sub + '/top/?t=all&limit=100' )
		catch_up = args.catch_up
		last_link = args.last
		counter = 0

		try:
			while( True ):
				titles = driver.find_elements_by_class_name( 'title' )
				for title in titles:
					link = title.get_attribute( 'href' )

					if( link == None ):
						continue

					if( link in last_link ):
						catch_up = False
						continue

					if( catch_up == True ):
						continue

					last_link = link
					print( link )

					if( ( ".jpg" in link[-4:].lower() ) | ( ".png" in link[-4:].lower() ) ):
						results_file.write( link )
						results_file.write( '\n' )
						counter += 1
					elif( ( '/' in link[-1:] ) & ( 'old.reddit' in link ) ):
						title.click()
						try:
							img = driver.find_element_by_class_name( 'preview' )
							print( img.get_attribute( 'src' ) )
							driver.get( img.get_attribute( 'src' ) )
							results_file.write( driver.current_url )
							results_file.write( '\n' )
						except Exception as e:
							print( e )
							driver.back()
							break

						driver.back()
						driver.back()
						titles = driver.find_elements_by_class_name( 'title' )
						catch_up = True
						counter += 1
						break
					catch_up = False

				if( catch_up == True ):
					continue

				if( counter >= 5000):
					break

				driver.find_element_by_class_name( 'next-button' ).click()
		except Exception as e:
			print( e )
			results_file.close()
			quit()

	results_file.close()

if __name__ == "__main__":
	parser.add_argument('--sub', type=str, default=None, help='Name of subreddit to scrape for images')
	parser.add_argument('--catch_up', action='store_true', help='whether to ignore found pics up to a given pic', default=False)
	parser.add_argument('--last', type=str, default="", help='Last pic visited')
	main(parser.parse_args())
