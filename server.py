import datetime

from playwright.sync_api import sync_playwright, Playwright
from flask import Flask, request
import time
import json
from pathlib import Path
import os
from urllib.parse import urlparse
import requests
import threading
from bs4 import BeautifulSoup
import sys



'''

# Rederio service for website pre-rendering

# This is not a large website analysis service with or without preliminary rendering for search engines

# Similar to the "Prerender" service only for free

# Also, the "Renderio" service works faster than "Prerender", although it uses python :)

# Two variations can be used (PlayWright | Selenium)


'''

class Server:

	def __init__(self, port):
		self.port = port

	def add_to_catch(self, url, content):

		parsed_url = urlparse(url)

		path_url = Path(parsed_url.netloc)

		if not path_url.exists(): os.mkdir(path_url)

		if path_url.exists():
			name_file = f'{parsed_url.netloc}{parsed_url.path}'.replace('/', '-')
			full_path = f'{parsed_url.netloc}/{name_file}.html'

			with open(full_path, "w", encoding="utf-8") as f:
				f.write(str(content))

	def find_in_cache(self, url):

		try:
			parsed_url = urlparse(url)
			path_url = Path(parsed_url.netloc)

			if path_url.exists():
				name_file = f'{parsed_url.netloc}{parsed_url.path}'.replace('/', '-')
				full_path = f'{parsed_url.netloc}/{name_file}.html'

				if Path(full_path).exists():
					f = open(full_path, "r", encoding="utf-8")
					return f.read()

			return False

		except Exception as e:
			self.write_logs(e)
			return False

	def read_coinf(self):
		try:
			conf = open("config.json", encoding="utf-8").read()
			self.config = json.loads(conf)

			return True

		except Exception as e:
			print(e)
			return False

	def start_server(self, name):

		# conf = self.read_coinf()

		# if conf == False:
		#     print("Config file is not find!")
		#     return

		self.app = Flask(name)

		# ROUTE /{index}
		@self.app.route('/')
		def index():
			return "You can use some api! /renderio/api/v1/getcontent?url=yuorsite.com"

		# ROUTE /getcontent
		@self.app.route('/renderio/api/v1/getcontent', methods=['GET'])
		def getcontent():
			try:

				url = request.args.get("url")
				time_s = request.args.get("t")

				print(url)
				print(time_s)

				if time_s is None:
					time_s = 1

				if url is None:
					return "Url arg in null"
				if len(url) == 0:
					return "Invalid url"
				if url.find("http") == -1:
					return "Error url http"

				ch_url = self.find_in_cache(url)

				if ch_url:
					return ch_url
				else:
					return self.main(url, time_s)

			except Exception as e:
				self.write_logs(e)
				return "Error"

		# ROUTE /renderone
		@self.app.route('/renderio/api/v1/renderone', methods=['GET'])
		def renderone():
			try:

				url = request.args.get("url")
				time_s = request.args.get("t")

				if time_s is None:
					time_s = 1

				if url is None: return "Url arg in null"

				if len(url) == 0: return "Invalid url"

				if url.find("http") == -1: return "Error url http"

				res = self.main(url, time_s)

				if len(res) == 0: return "Error"

				return "Update Done."

			except Exception as e:
				self.write_logs(e)
				return "Error"

		@self.app.route('/renderio/api/v1/renderall', methods=['GET'])
		def renderall():

			try:
				url = request.args.get("url")
				time_s = request.args.get("t")
				if time_s is None: time_s = 1

				if url is None: return "Url arg in null"
				if len(url) == 0: return "Invalid url"
				if url.find("http") == -1: return "Error url http"

				parsed_url = urlparse(url)

				n_url = f'{parsed_url.scheme}://{parsed_url.netloc}'

				if "sitemap".find(url) == -1:
					n_url = f'{n_url}/sitemap.xml'

				try:

					res = requests.get(n_url)

					if res.status_code == 200:
						soup = BeautifulSoup(res.text, "lxml")
						locs = soup.find_all('loc')

						for loc in locs:
							start = datetime.datetime.now()
							self.main(loc.text, time_s)
							end = datetime.datetime.now()

							print(f'Start time: {start}\nEnd time{end}')

						return "Done."

				except Exception as e:
					self.write_logs(e)
					return "Sitemap is not find!"
			except Exception as e:
				self.write_logs(e)
				return 'Error'

		self.run(host='0.0.0.0', port=self.port)
		# self.run(host='0.0.0.0', port=self.config['port'])

	def run_driver(self, playwright: Playwright, url, t):

		try:

			# SELENUIM
			# ============================================================

			start = datetime.datetime.now()
			from selenium import webdriver
			options = webdriver.ChromeOptions()
			options.add_argument('--headless')
			driver = webdriver.Chrome(options=options)
			driver.get(url)
			time.sleep(int(t))
			html = driver.page_source
			self.add_to_catch(url, html)


			# PLAYWRIGHT
			# ============================================================
			# browser = playwright.chromium.launch(headless=True)
			# page = browser.new_page()
			# page.goto(url)
			# time.sleep(int(t))
			# html = page.content()
			# self.add_to_catch(url, html)
			# print(html)
			return html

		except Exception as e:
			self.write_logs(e)
			return False

	def main(self, url, time):

		with sync_playwright() as playwright:
			res = self.run_driver(playwright, url, time)
			if res != False:
				if len(res) != 0: return res

		return 'Null'

	def write_logs(self, txt):

		try:

			path_logs = Path('logs')
			ph = "logs/logs.txt"

			if not path_logs.exists():
				os.mkdir(path_logs)

			if not Path(ph).exists():
				open(ph, "w", encoding="utf-8").write('')

			if Path(ph).exists():
				open(ph, "a", encoding="utf-8").write(str(txt))

		except Exception as e:
			print(e)

	def run(self, host, port):
		self.app.run(host=host, port=port)

# START SERVER
try:
	port = sys.argv[1]
	driver = sys.argv[2]

	if __name__ == '__main__':
		Server(port).start_server(__name__)

except Exception as e:
	print(e)

