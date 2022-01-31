"""BSD 3-Clause License

Copyright (c) 2022, Danil Napad
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."""

import os
import requests
from bs4 import BeautifulSoup
from pickle import dump, load


FILM_DICTIONARY = {
	'2015':'https://ru.wikipedia.org/wiki/%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F:%D0%A4%D0%B8%D0%BB%D1%8C%D0%BC%D1%8B_2015_%D0%B3%D0%BE%D0%B4%D0%B0',
	'2016':'https://ru.wikipedia.org/w/index.php?title=%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F:%D0%A4%D0%B8%D0%BB%D1%8C%D0%BC%D1%8B_2016_%D0%B3%D0%BE%D0%B4%D0%B0',
	'2017':'https://ru.wikipedia.org/wiki/%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F:%D0%A4%D0%B8%D0%BB%D1%8C%D0%BC%D1%8B_2017_%D0%B3%D0%BE%D0%B4%D0%B0',
	'2018':'https://ru.wikipedia.org/w/index.php?title=Категория:Фильмы_2018_года',
	'2019':'https://ru.wikipedia.org/wiki/%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F:%D0%A4%D0%B8%D0%BB%D1%8C%D0%BC%D1%8B_2019_%D0%B3%D0%BE%D0%B4%D0%B0',
	'2020':'https://ru.wikipedia.org/wiki/%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F:%D0%A4%D0%B8%D0%BB%D1%8C%D0%BC%D1%8B_2020_%D0%B3%D0%BE%D0%B4%D0%B0'
}
"""
На одной странице отображаются не все фильмы. Можно увидеть больше
при нажатии 'Следующая страница'.

Такие пункты не нужны*
	Список лидеров кинопроката России ... года
	Список лидеров кинопроката США ... года

* если существует файл с проделанными первыми 5 этапами, то их пропустить
	и загрузить результаты из файла
1. Переданная ссылка содержит несколько страниц с фильмами. Нужно получить все
	- через переход с использованием 'Следующая страница'
2. Оставить только div с id 'mw-pages' - только там содержатся фильмы
	- применяется к каждой найденной странице
3. Извлечь все ссылки в виде (name, link)
4. Удалить ненужные пункты*
5. Сохранить найденный материал в отдельном файле

* Проверить наличие папки для выбранного года; создать, если необходимо
6. Перейти по каждой ссылке в хранилище; загрузить её html; сохранить в файл
	с переданным именем в папке для нужного года
"""
def store_html_item(YEAR, title, link):
	if any(char in title for char in '/:*?"<>|'): 
		[(title:=title.replace(char, '_')) for char in '/:*?"<>|']
	path = f'film_htmls/{YEAR}/{title}.html'
	if not os.path.exists(path):
		r = requests.get(link)
		with open(path, 'w', encoding='utf-8') as f:
			f.write(r.text)
			print(f'"{title}" movie page has been saved')
	else:
		print(f'"{title}" movie page already stored')


def get_film_container_item(div_mw_pages):
	film_list = div_mw_pages.find_all('li')
	film_container_item = [(film.find('a')['title'], 'https://ru.wikipedia.org'+film.find('a')['href']) 
							for film in film_list 
							if 'Список лидеров кинопроката' not in film.find('a')['title']]
	return film_container_item


def download_container(YEAR_NUMBER, link):
	""":YEAR_NUMBER - str type"""

	r = requests.get(link)
	soup = BeautifulSoup(r.text, 'html.parser')
	div_list = [soup.find('div', {'id': 'mw-pages'})]
	
	is_complete = False
	while not is_complete:
		# list with 2 items
		next_page = [e for e in div_list[-1].find_all('a') if 'Следующая страница' in e]
		if next_page:
			# request.get + soup + extract div + add it to div_list
			r = requests.get('https://ru.wikipedia.org'+next_page[0]['href'])
			soup = BeautifulSoup(r.text, 'html.parser')
			div = soup.find('div', {'id': 'mw-pages'})
			div_list.append(div)
		else:
			is_complete = True

	film_container = []
	for div_mw_pages in div_list:
		film_container.extend(get_film_container_item(div_mw_pages))
	
	with open(f'film_lists/{YEAR_NUMBER}_year_storage.pkl','wb') as f:
		dump(film_container, f)
		print(f'film_container for {YEAR_NUMBER} year has been saved in local storage')

	return film_container


def get_film_container(YEAR_NUMBER):
	assert type(YEAR_NUMBER)==str, "YEAR_NUMBER should be an str type"

	path = f'film_lists/{YEAR_NUMBER}_year_storage.pkl'
	if not os.path.exists(path):
		film_container = download_container(YEAR_NUMBER, FILM_DICTIONARY[YEAR_NUMBER])
	else:
		print(f'film_container for {YEAR_NUMBER} year has been restored from local storage')
		with open(path, 'rb') as f:
			film_container = load(f)
	return film_container


if __name__ == "__main__":
	if not os.path.exists('film_lists'): os.mkdir('film_lists')
	if not os.path.exists('film_htmls'): os.mkdir('film_htmls')

	YEARS = list(map(lambda y: str(y), range(2015,2021)))
	for YEAR_NUMBER in YEARS:
		# collect (name, link) for every film during [2015,2020]
		film_container = get_film_container(YEAR_NUMBER)
		path = f'film_htmls/{YEAR_NUMBER}'
		if not os.path.exists(path): os.mkdir(path)
		for film_title, film_link in film_container:
			store_html_item(YEAR_NUMBER, film_title, film_link)

	print("\nAll films' descriptions had been downloaded\n")
