from utils.utils import read_json, save_json
import codecs

data = read_json('./abstracts_cleaned_erro-0.15.json')
for i, k in enumerate(data.keys()):
    text_gs = data[k]['abstracts_pt']
    text_ocr = data[k]['abstracts_pt_error']
    print(k)
    gs = codecs.open('../ochre_app/gspt/'+str(i+1)+'.txt', 'w')
    ocr = codecs.open('../ochre_app/ocrpt/'+str(i+1)+'.txt', 'w')
    gs.write(text_gs)
    ocr.write(text_ocr)
    md = {"doc_id":str(i+1)}
    save_json('../ochre_app/mdpt/md'+str(i+1)+'.json', md)
