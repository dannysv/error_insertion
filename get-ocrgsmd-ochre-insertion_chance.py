from utils.utils import read_json, save_json
import codecs
import sys 
import os 

def processar(insertion_chance):
    #pasta para os textos corretos
    if os.path.exists('../ochre_app/gspt-'+str(insertion_chance)) == False:
        os.mkdir('../ochre_app/gspt-'+str(insertion_chance))
    #pasta para os textos com erros
    if os.path.exists('../ochre_app/ocrpt-'+str(insertion_chance)) == False:
        os.mkdir('../ochre_app/ocrpt-'+str(insertion_chance))
    #pasta com os nomes dos arquivos
    if os.path.exists('../ochre_app/mdpt-'+str(insertion_chance)) == False:
        os.mkdir('../ochre_app/mdpt-'+str(insertion_chance))
    
    #json fonte com abstracts 
    data = read_json('./abstracts_cleaned_erro-'+str(insertion_chance)+'.json')
    for i, k in enumerate(data.keys()):
        text_gs = data[k]['abstracts_pt']
        text_ocr = data[k]['abstracts_pt_error']
        print(k)
        gs = codecs.open('../ochre_app/gspt-'+str(insertion_chance)+'/'+str(i+1)+'.txt', 'w')
        ocr = codecs.open('../ochre_app/ocrpt-'+str(insertion_chance)+'/'+str(i+1)+'.txt', 'w')
        gs.write(text_gs)
        ocr.write(text_ocr)
        md = {"doc_id":str(i+1)}
        save_json('../ochre_app/mdpt-'+str(insertion_chance)+'/md'+str(i+1)+'.json', md)

if __name__ == "__main__":
    insertion_chance = sys.argv[1]
    processar(insertion_chance)
