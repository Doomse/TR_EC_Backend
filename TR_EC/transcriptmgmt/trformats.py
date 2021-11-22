import json

def interpolate(wordList, start, end):
	numOfChars = len(''.join(wordList))
	duration = end - start
	p = []
	currChar = 0
	for word in wordList:
		wordLength = len(word)
		p.append({
			"word": word,
			"start": round(start + (duration * (currChar / numOfChars)), 2),
			"end": round(start + (duration * ((currChar + wordLength) / numOfChars)), 2)
		})
		currChar += wordLength
	return p

def vtt_to_trjson(content: str):
    
    def formatted_time_to_float(time: str):
        h, m, s = time.split(':')
        return float(s) + 60*float(m) + 3600*float(h)
    
    lines = content.splitlines()
    trjson = []
    start: float
    end: float
    text = ''
    for line in lines:
        if 'WEBVTT' in line or line.startswith('NOTE '):
            continue
        if line.startswith('-'):
            line = line[1:]
        line = line.strip()
        if ' --> ' in line:
            start_str, end_str = line.split(' --> ')
            start = formatted_time_to_float(start_str)
            end = formatted_time_to_float(end_str)
        elif line != '':
            text += line
        else:  # line is empty
            if text != '':
                trjson.append(interpolate(text.split(), start, end))
                text = ''
    if text != '':
        trjson.append(interpolate(text.split(), start, end))
    return trjson

def trjson_to_vtt(content) -> str:
    pass

# format entry: format name -> (file extension, to trjson function, from trjson function)
formats = {
    "trjson": ('json', json.loads, json.dumps),
    "vtt": ('vtt', vtt_to_trjson, trjson_to_vtt),
}