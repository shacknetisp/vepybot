"""
The MIT License (MIT)

Copyright (c) 2013 Brendan Abel

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
""" Converts text to Pig Latin

>>> import piglatin
>>> 
>>> piglatin.translate('this is a test string')
'is-thay is-ay a-ay est-tay ing-stray'

"""
import re
import string
from string import ascii_letters


def translate(txt):
	""" Translates text into pig latin ."""

	vowels = 'aeiou'
	# Separates text into words and whitespace
	words = re.findall(r'(?:\S+)|(?:\s+)', txt)
	output = []
	ascii_set = set(ascii_letters)
	for word in words:
		# Whitespace does not require translation
		if not word.strip():
			output.append(word)
			continue
		# Punctuation does not require translation
		if not ascii_set.intersection(word):
			output.append(word)
			continue
		
		# Gather pre and post punctuation (ie; qhotes, etc.).  They should
		# still remain at the beginning and end of the translated word.
		m = re.match(r'^(?P<pre>[\W]*)(?P<word>.+?)(?P<post>[\W]*)$', word)
		d = m.groupdict()
		

		# pig latin removes any leading consonants to a word and places them
		# at the end of the word, followed by -ay.  If the word starts with a 
		# vowel, just append -ay.  Treat y as a vowel only if it is not at 
		# the beginning of a word and preceded by a consonant (this isn't 
		# foolproof, but it works in most cases).
		i = 0
		word = d['word']
		while len(word) > i:
			if word[i].lower() in vowels:
				break
			if i > 0 and word[i].lower() == 'y':
				break				
			i += 1
		d['fore'] = word[i:]
		d['aft'] = word[:i]
		new_word = '{pre}{fore}{aft}ay{post}'.format(**d)
		output.append(new_word)
	return ''.join(output) 
			
			
