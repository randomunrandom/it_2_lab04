import json
import math
import re
from tqdm import tqdm


def process(filename):
    tmpl = list()
    s = str()
    file = open(filename, 'r', encoding='UTF-8')
    line = file.readline()
    o = line.find('/') + 1
    t = int(line[o:line.find('/', o)])
    o = line.find('/', o) + 1
    c = int(line[o:line.find('/', o)])
    o = line.find('/', o) + 1
    p = int(line[o:line.find('/', o)])
    for line in file:
        line = line.replace(r'\n', '')
        if line[0] == '/':
            if tmp == 1:
                s = s.replace('\n', '')
                tmpl.append(dict(tom=t, chapter=c, part=p, text=s))
                s = ''
            tmp = 0
            o = line.find('/') + 1
            t = int(line[o:line.find('/', o)])
            o = line.find('/', o) + 1
            c = int(line[o:line.find('/', o)])
            o = line.find('/', o) + 1
            p = int(line[o:line.find('/', o)])
            # print('t = {}, c = {}, g = {}'.format(t, c, p))
            # print(line)
        else:
            s = s.replace(r'\n', '')
            s = s + line
            tmp = 1
    s = s.replace('\n', '')
    tmpl.append(dict(tom=t, chapter=c, part=p, text=s))
    s = ''
    backward_list = list()
    for i in tqdm(range(len(tmpl))):
        tmpl[i]['data'] = list()
        add = list()
        tmpl[i]['data']['amount_of_words'] = len(tmpl[i]['text'])
        words = tmpl[i]['text'].split()
        for j in range(len(words)):
            words[j] = words[j].replace('.', '')
            words[j] = words[j].replace(',', '')
            words[j] = words[j].replace(':', '')
            words[j] = words[j].replace(';', '')
            words[j] = words[j].replace('«', '')
            words[j] = words[j].replace('»', '')
            words[j] = words[j].replace('–', '')
            words[j] = words[j].replace('_', '')
            words[j] = words[j].replace('(', '')
            words[j] = words[j].replace(')', '')
            words[j] = words[j].replace('[', '')
            words[j] = words[j].replace(']', '')
            words[j] = words[j].lower()
            add.append(dict(word=words[j], TF=1))
            leng = len(add) - 1
            for k in range(leng):
                if add[k]['word'] == words[j]:
                    add.pop()
                    add[k]['TF'] = add[k]['TF'] + 1
            backward_list.append(dict(word=words[j], data=list(), ind_doc=1))
            backward_list[-1]['data'].append(
                dict(tom=tmpl[i]['tom'], chapter=tmpl[i]['chapter'], part=tmpl[i]['part'], place=j))
            leng = len(backward_list) - 1
            for k in range(leng):
                if backward_list[k]['word'] == words[j]:
                    backward_list.pop()
                    backward_list[k]['data'].append(
                        dict(tom=tmpl[i]['tom'], chapter=tmpl[i]['chapter'], part=tmpl[i]['part'], place=j))
                    btmp = 0
                    for bel in backward_list[k]['data']:
                        if (bel['tom'] != tmpl[i]['tom']) or (bel['chapter'] != tmpl[i]['chapter']) or (
                                bel['part'] != tmpl[i]['part']):
                            btmp = btmp + 1
                    if btmp == len(backward_list[k]['data']) - 1:
                        backward_list[k]['ind_doc'] = backward_list[k]['ind_doc'] + 1
        for k in range(len(add)):
            add[k]['TF'] = float(add[k]['TF'] / len(add))
        tmpl[i]['data']['forward_list'] = add

        print(
            '\rtom={}, chapter={}, part={}, data={}\r'.format(tmpl[i]['tom'], tmpl[i]['chapter'], tmpl[i]['part'],
                                                              tmpl[i]['data']))
    for el in backward_list:
        el['IDF'] = float(math.log(len(tmpl) / el['ind_doc']))
        print('\rword = {}, data={}, ind_doc={}, IDF={}\r'.format(el['word'], el['data'], el['ind_doc'], el['IDF']))
    with open('processed_text.json', 'w', encoding='UTF-8') as outfile:
        json.dump(tmpl, outfile, ensure_ascii=False)
    with open('backward_list.json', 'w', encoding='UTF-8') as outfile:
        json.dump(backward_list, outfile, ensure_ascii=False)
    print('processing finished!')
    return


def sfunc1(elem):
    return elem[-1]


def sfunc2(elem):
    tmp = 0
    for i in range(len(elem['dist'])):
        tmp = tmp + elem['dist'][i]
    return tmp


# process('resources\\sampletext.txt')
proc_text = open('processed_text.json', 'r', encoding='UTF-8').read()
data_proc = json.loads(proc_text)
back_list = open('backward_list.json', 'r', encoding='UTF-8').read()
data_back = json.loads(back_list)
inp = input('input search request ')
words = inp.split()
for i in range(len(words)):
    words[i] = re.sub(".,:;«»–_\(\)\[]", '', words[i])
    words[i] = words[i].lower()
flag = 0
res = list()
for wi in words:
    for dbi in data_back:
        if wi == dbi['word']:
            for dpi in data_proc:
                for dpfi in dpi['data']['forward_list']:
                    if dpfi['word'] == wi:
                        res.append([
                            dict(tom=dpi['tom'], chapter=dpi['chapter'], part=dpi['part']),
                            dict(word=wi, IDF=dbi['IDF'], TF=dpfi['TF'])
                        ])
                        leng = len(res) - 1
                        for ri in range(leng):
                            if res[ri][0] == dict(tom=dpi['tom'], chapter=dpi['chapter'], part=dpi['part']):
                                res.pop()
                                if res[ri][1]['word'] != wi:
                                    res[ri].append(dict(word=wi, IDF=dbi['IDF'], TF=dpfi['TF']))

topop = list()
for i in range(len(res)):
    if (len(res[i])) != len(words) + 1:
        topop.append(i)
topop.reverse()
for i in topop:
    res.pop(i)
tmp = 0
for i in range(len(res)):
    for j in range(len(words)):
        tmp += res[i][j + 1]['IDF'] * res[i][j + 1]['TF']
    res[i].append(tmp)
    tmp = 0
res.sort(key=sfunc1)
res.reverse()
if res != list():
    print('method 1:')
for i in range(len(res)):
    print("{}: tom: {} chapter: {} part: {}".format(i + 1, res[i][0]['tom'], res[i][0]['chapter'], res[i][0]['part']))
    if i == 4:
        print("-----------------------------------")

res2 = list()
pos = list()
for i in range(len(data_proc)):
    pos.append(dict(tom=data_proc[i]['tom'], chapter=data_proc[i]['chapter'], part=data_proc[i]['part'], seen=dict(())))
    res2 = data_proc[i]['text'].split()
    for k in range(len(words)):
        pos[i]['seen'][k] = list()
    for j in range(len(res2)):
        res2[j] = re.sub(".,:;«»–_\(\)\[]", '', res2[j])
        res2[j] = res2[j].lower()
        for k in range(len(words)):
            if res2[j] == words[k]:
                pos[i]['seen'][k].append(666)
                pos[i]['seen'].get(k).append(j)

topop = list()
for i in range(len(pos)):
    for j in range(len(pos[i]['seen'])):
        if (len(pos[i]['seen'][j])) == 0:
            topop.append(i)
topop = list(set(topop))
topop.reverse()
for i in topop:
    pos.pop(i)
tmp = 0
for i in range(len(pos)):
    for j in range(len(pos[i]['seen'])):
        pos[i]['seen'][j] = list(set(pos[i]['seen'][j]))
for i in range(len(pos)):
    for j in range(len(pos[i]['seen'])):
        if (len(pos[i]['seen'][j])) > tmp:
            tmp = len(pos[i]['seen'][j])
for i in range(len(pos)):
    for j in range(len(pos[i]['seen'])):
        if (len(pos[i]['seen'][j])) < tmp:
            tmp = len(pos[i]['seen'][j])
    pos[i]['min'] = tmp
for i in range(len(pos)):
    for j in range(len(pos[i]['seen'])):
        pos[i]['seen'][j] = pos[i]['seen'][j][:pos[i]['min']]
for i in range(len(pos)):
    pos[i].update(dict(dist=list()))
    for j in range(len(pos[i]['seen'])):
        for k in range(len(pos[i]['seen'][j]) - 1):
            tmp = tmp + abs(pos[i]['seen'][j][k] - pos[i]['seen'][j][k + 1])
        pos[i]['dist'].append(tmp)
        tmp = 0
pos.sort(key=sfunc2)
pos.reverse()
if pos != list():
    print('method 2:')
for i in range(len(pos)):
    print("{}: tom: {} chapter: {} part: {}".format(i + 1, pos[i]['tom'], pos[i]['chapter'], pos[i]['part']))
    if i == 4:
        print("-----------------------------------")
