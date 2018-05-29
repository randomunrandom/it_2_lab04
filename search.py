import json
import math
import re
from tqdm import tqdm


# Адам <3

def snipset(s_w=list(), t=int(), c=int(), p=int()):
    s_proc = open('processed_text.json', 'r', encoding='UTF-8').read()
    s_data = json.loads(proc_text)
    s_tmp1 = 0
    s_tmp2 = 0
    for s_i in s_data:
        if s_i['tom'] == t and s_i['chapter'] == c and s_i['part'] == p:
            for s_j in range(len(s_i['text'].split())):
                # print(s_j, end='')
                if '.' in s_i['text'].split()[s_j]:
                    s_tmp1 = s_j + 1
                if s_i['text'].split()[s_j].lower() in s_w:
                    s_tmp2 = s_j
                    break
            break
    for s_i in s_data:
        if s_i['tom'] == t and s_i['chapter'] == c and s_i['part'] == p:
            for s_j in range(s_tmp1, max(s_tmp1 + 20, s_tmp2)):
                if s_j == s_tmp1:
                    s_i['text'].split()[s_j] = s_i['text'].split()[s_j][s_i['text'].split()[s_j].find('.'):]
                s_str = re.sub('[.,:;«»–_()[\]]', '', s_i['text'].split()[s_j].lower())
                if s_str in s_w:
                    print('!!!' + s_i['text'].split()[s_j] + '!!!', end=' ')
                else:
                    print(s_i['text'].split()[s_j], end=' ')
            print('...')

    return


def process(filename):
    tmp_l = list()
    s = str()
    p_tmp = 0
    file = open(filename, 'r', encoding='UTF-8')
    line = file.readline()
    o = line.find('/') + 1
    t = int(line[o:line.find('/', o)])
    o = line.find('/', o) + 1
    c = int(line[o:line.find('/', o)])
    o = line.find('/', o) + 1
    p = int(line[o:line.find('/', o)])
    for line in file:
        line = line.replace(r'\n', ' ')
        if line[0] == '/':
            if p_tmp == 1:
                s = s.replace('\n', ' ')
                tmp_l.append(dict(tom=t, chapter=c, part=p, text=s))
                s = ''
            p_tmp = 0
            o = line.find('/') + 1
            t = int(line[o:line.find('/', o)])
            o = line.find('/', o) + 1
            c = int(line[o:line.find('/', o)])
            o = line.find('/', o) + 1
            p = int(line[o:line.find('/', o)])
        else:
            s = s.replace(r'\n', ' ')
            s = s + line
            p_tmp = 1
    s = s.replace('\n', ' ')
    tmp_l.append(dict(tom=t, chapter=c, part=p, text=s))
    backward_list = list()
    for p_i in tqdm(range(len(tmp_l))):
        tmp_l[p_i] = dict(data=list())
        add = list()
        tmp_l[p_i] = dict(data=dict(amount_of_words=len(tmp_l[p_i]['text'])))
        p_words = tmp_l[p_i]['text'].split()
        for p_j in range(len(p_words)):
            p_words[p_j] = re.sub('[.,:;«»–_()[\]]', '', p_words[p_j])
            p_words[p_j] = p_words[p_j].lower()
            add.append(dict(word=p_words[p_j], TF=1))
            p_leng = len(add) - 1
            for p_k in range(p_leng):
                if add[p_k]['word'] == p_words[p_j]:
                    add.pop()
                    add[p_k]['TF'] = add[p_k]['TF'] + 1
            backward_list.append(dict(word=p_words[p_j], data=list(), ind_doc=1))
            backward_list[-1]['data'].append(
                dict(tom=tmp_l[p_i]['tom'], chapter=tmp_l[p_i]['chapter'], part=tmp_l[p_i]['part'], place=p_j))
            p_leng = len(backward_list) - 1
            for p_k in range(p_leng):
                if backward_list[p_k]['word'] == p_words[p_j]:
                    backward_list.pop()
                    backward_list[p_k]['data'].append(
                        dict(tom=tmp_l[p_i]['tom'], chapter=tmp_l[p_i]['chapter'], part=tmp_l[p_i]['part'], place=p_j))
                    btmp = 0
                    for bel in backward_list[p_k]['data']:
                        if (bel['tom'] != tmp_l[p_i]['tom']) or (bel['chapter'] != tmp_l[p_i]['chapter']) or (
                                bel['part'] != tmp_l[p_i]['part']):
                            btmp = btmp + 1
                    if btmp == len(backward_list[p_k]['data']) - 1:
                        backward_list[p_k]['ind_doc'] = backward_list[p_k]['ind_doc'] + 1
        for p_k in range(len(add)):
            add[p_k]['TF'] = float(add[p_k]['TF'] / len(add))
        tmp_l[p_i]['data'] = dict(forward_list=add)

        print('\rtom={}, chapter={}, part={}, data={}\r'.format(tmp_l[p_i]['tom'], tmp_l[p_i]['chapter'],
                                                                tmp_l[p_i]['part'],
                                                                tmp_l[p_i]['data']))
    for el in backward_list:
        el['IDF'] = float(math.log(len(tmp_l) / el['ind_doc']))
        print('\rword = {}, data={}, ind_doc={}, IDF={}\r'.format(el['word'], el['data'], el['ind_doc'], el['IDF']))
    with open('processed_text.json', 'w', encoding='UTF-8') as outfile:
        json.dump(tmp_l, outfile, ensure_ascii=False)
    with open('backward_list.json', 'w', encoding='UTF-8') as outfile:
        json.dump(backward_list, outfile, ensure_ascii=False)
    print('processing finished!')
    return


def sfunc1(elem):
    return elem[-1]


def sfunc2(elem):
    sf2_tmp = 0
    for sf2_i in range(len(elem['dist'])):
        sf2_tmp = sf2_tmp + elem['dist'][sf2_i]
    return sf2_tmp


# process('resources\\sampletext.txt')
proc_text = open('processed_text.json', 'r', encoding='UTF-8').read()
data_proc = json.loads(proc_text)
back_list = open('backward_list.json', 'r', encoding='UTF-8').read()
data_back = json.loads(back_list)
inp = input('input search request ')
words = inp.split()
print('you typed: ', end=' ')
for i in range(len(words)):
    words[i] = re.sub('[.,:;«»–_()[\]]', '', words[i])
    words[i] = words[i].lower()
    print(words[i], end=' ')
print('\n*because python console doesn\'t sopport formating key words would be encapsulated in \'!!!\'*')
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
    snipset(words, res[i][0]['tom'], res[i][0]['chapter'], res[i][0]['part'])
res2 = list()
pos = list()
for i in range(len(data_proc)):
    pos.append(dict(tom=data_proc[i]['tom'], chapter=data_proc[i]['chapter'], part=data_proc[i]['part'], seen=dict(())))
    res2 = data_proc[i]['text'].split()
    for k in range(len(words)):
        pos[i]['seen'][k] = list()
    for j in range(len(res2)):
        res2[j] = re.sub('[.,:;«»–_()[\]]', '', res2[j])
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
    print('-\n-\nmethod 2:')
for i in range(len(pos)):
    print("{}: tom: {} chapter: {} part: {}".format(i + 1, pos[i]['tom'], pos[i]['chapter'], pos[i]['part']))
    if i == 4:
        print("-----------------------------------")
    snipset(words, pos[i]['tom'], pos[i]['chapter'], pos[i]['part'])
if res == list() and pos == list():
    print('couldn\'t find anythind :c')
