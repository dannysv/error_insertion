import sys
import glob
import random
from itertools import combinations
import pprint
import json
from utils.utils import save_txt, save_txt_encoding, save_json
import tqdm

#this function sorts a list of tuples using the second element of each tuple
def Sort_Tuple(tup):
    # getting length of list of tuples 
    lst = len(tup)
    for i in range(0, lst):
        for j in range(0, lst-i-1):
            if (tup[j][1] > tup[j + 1][1]):
                temp = tup[j]
                tup[j]= tup[j + 1]
                tup[j + 1]= temp
    return tup

#fiz isso aqui global pra nao ter que toda hora ficar pegando a tabela de erros
#salva os erros num dicionário no qual as chaves são os caracteres originais e os valroes são tuplas (erro, frequencia)
error_table_file = open("troca_caracteres.txt", "r", encoding="utf8")
error_table_dic = {}
for line in error_table_file:
    original_char = line.split(" ")[0]
    error = line.split(" ")[1]
    freq = int(line.split(" ")[2].replace("\n", ""))
    error_table_dic.setdefault(original_char, [])
    error_table_dic[original_char].append((error, freq))

for key in error_table_dic.keys():
    error_table_dic[key] = Sort_Tuple(error_table_dic[key])
    error_table_dic[key].reverse()


#pega as substrings de tamanho <= 2, cria um dicionario com as possiveis inserções de erro, usando essas substrings da palavra
#falta fazer o processo de decidir qual erro que vai ser inserido (e inserir o erro)
def insert_error(word, next_word):
    #gets all substrings
    #substrings = [word[x:y] for x, y in combinations(range(len(word) + 1), r = 2)] 
    #substrings = [x for x in substrings if len(x)<=2]
    substrings = []
    for x, y in zip(word[:-1], word[1:]):
        substrings.append(x)
        substrings.append(x+y)
    substrings.append(word[-1])

    possible_insertions = {}

    #só passa o dicionario gllobal pra um temporário menor, que só tem as chaves ue são substrings da palavra atual
    for substring in substrings:
        if substring in error_table_dic.keys():
            possible_insertions[substring] = error_table_dic[substring]

    # error_word = tournamentSelection(possible_insertions, word, 5)
    error_word, skip_flag = create_random_error(possible_insertions, word, next_word, 20)
    
    return error_word, skip_flag


'''
    Retorna a palavra com erro de maior frequencia que participou de um torneio

    Caso não tenha sido possível formar algum erro, retorna a original

    Recebe como parâmetros: 
     - dicionario com mudanças (podendo ser o dicionario gerado com as mudanças em específico para a palavra)
     - palavra para que seja gerado os erros
     - tamanho do torneio sendo realizado
'''
def tournamentSelection(possible_changes_dict, word, tournament_size):
    # Gera erros na palavra
    variations = generate_possible_errors(possible_changes_dict, word)

    if len(variations) == 0:
        return word

    tournament_winner = word
    tournament_value = 0

    # Realiza torneio entre os erros gerados, ganha o erro que participou do torneio com maior frequencia de trocas
    for i in range(tournament_size):
        selected_challenger = variations[random.randrange(len(variations))]
        if tournament_winner == "" or tournament_value < selected_challenger[1]:
            tournament_winner = selected_challenger[0]
            tournament_value = selected_challenger[1]

    return tournament_winner

def create_random_error(possible_erros, word, next_word, tournament_size):
    # Gerar um erro aleatório no meio/redor de uma palavra (word) - algum simbolo simples [',.´`] ~ 0.005
    # Juntar duas palavras (word, next_word) ~ 0.05
    # Separar uma palavra ao meio (word) ~ 0.1
    # Inserir um erro para simular os quais são identificador pelo OCR

    # error type
    # 0 - inseriu simbolo
    # 1 - juntou
    # 2 - separou
    # 3 - trocou char

    error_word = ""
    error_type = 0
    skip_flag = False
    random_choice = random.random()
    if random_choice <= 0.001:
        error_word = simbolo(word)
        skip_flag = 0
    elif random_choice <= 0.05:
        error_word, skip_flag = junta(word, next_word)
    elif random_choice <= 0.1:
        error_word = separa(word)
        skip_flag = 2
    else:
        error_word = misspelled(possible_erros, word, tournament_size)
        skip_flag = 3
    return error_word, skip_flag 

def misspelled(possible_erros, word, tournament_size):
    error_tuple = tournament_errors_dictionary(possible_erros, tournament_size)
    new_changed = []
    if error_tuple is not None:
        size_troca = len(error_tuple[0])
        for index_word in range(len(word)):
            # Gera pedaço de palavra para analisar se deves gerar erro
                # 'if' final garante que palavras de tamanho 1 também sofram alterações para erros
            word_piece = word[index_word:index_word+size_troca] if (index_word+size_troca < len(word)) else word[index_word:]
            if word_piece == error_tuple[0]:
                changed_word = (word[0:index_word] if index_word > 0 else "") + error_tuple[1][0] + word[index_word+size_troca:len(word)]
                new_changed.append(changed_word)
        # print("{} x {}".format(word, new_changed[random.randrange(len(new_changed))]), end='')
        return new_changed[random.randrange(len(new_changed))]
    else:
        return word

def simbolo(word):
    symbol = [',', '.', '\'', '´', '`']
    random_spot_word = random.randrange(0, len(word))
    random_symbol = symbol[random.randrange(0, len(symbol))]
    return word[:random_spot_word] + random_symbol + word[random_spot_word:]

def junta(word, next_word):
    return word+next_word, 1

def separa(word):
    if len(word) <= 1:
        return word
    separa_space = random.randrange(1, len(word))
    return word[:separa_space] + " " + word[separa_space:]

def tournament_errors_dictionary(possible_changes_dict, tournament_size):
    if (possible_changes_dict): # Verifica se existe dados no dicionario
        possible_changes_list = []
        for key,val in possible_changes_dict.items():
            for i in val:
                possible_changes_list.append((key, i))
        tournament_winner = None
        tournament_value = 0
        for i in range(tournament_size):
            selected_challenger = possible_changes_list[random.randrange(len(possible_changes_list))]
            # print("{}:{} X {}:{}".format(tournament_winner, tournament_value, selected_challenger, selected_challenger[1][1]))
            if tournament_winner == None or tournament_value < selected_challenger[1][1]:
                tournament_winner = selected_challenger
                tournament_value = selected_challenger[1][1]
        return tournament_winner
    else:
        None

'''
    Geração de erros nas palavras a partir de um dicionario
    Erros sendo gerados apenas 1 vez na palavra
'''
def generate_possible_errors(possible_changes_dict, word):
    word_variations = []
    size_substing_analysis = [1,2] # Analise de variacoes em palavras sendo feitas com substring de tamanhos 1 e 2
    for size_analysis in size_substing_analysis:
        for index_word in range(len(word)):
            # Gera pedaço de palavra para analisar se deves gerar erro
                # 'if' final garante que palavras de tamanho 1 também sofram alterações para erros
            word_piece = word[index_word:index_word+size_analysis] if (index_word+size_analysis < len(word)) else ("" if len(word)>1 else word)
            if word_piece in possible_changes_dict.keys():
                for error in possible_changes_dict[word_piece]:
                    # Cria palavra com erro e adiciona em lista
                    changed_word = (word[0:index_word] if index_word > 0 else "") + error[0] + word[index_word+size_analysis:len(word)]
                    word_variations.append((changed_word, error[1]))

    return word_variations


'''
process text: for a given text return the error_inserted version
''' 
def process_text(text, insertion_chance):
    error_tuples = []
    words = text.replace("\n"," ").split(" ")
    i = 0
    temp_text = ""
    while i < len(words):
        new_word = ""
        random_number = random.uniform(0,1)
        word = words[i]
        if word != "":
            if random_number <= insertion_chance:
                if i < len(words)-1:
                    next_word = words[i+1]
                else:   
                    next_word = ""
                new_word, skip_flag = insert_error(word, next_word)

                if skip_flag == 1:
                    error_type = "J"
                elif skip_flag == 0:
                    error_type = "I"
                elif skip_flag == 2:
                    error_type = "S"
                elif skip_flag == 3:
                    error_type = "T"

                temp_text += new_word + " "

                if word != new_word:
                    indexes_in_word = [z for z in range(min( len(word),len(new_word) ) ) if word[z] != new_word[z]] # considera o menor pois o ultimo character sera ignorado
                    index_in_word = 0
                    if len(indexes_in_word) == 0: # quer dizer que o erro foi inserido no ultimo caracter
                        index_in_word = min( len(word), len(new_word) ) -1
                    else:
                        index_in_word = indexes_in_word[0] - 1      

                    if error_type == "J":
                        error_tuples.append( (word + " " + words[i+1], new_word, error_type, index_in_word, i)   )
                        i += 1
                    else:
                        error_tuples.append( (word, new_word, error_type, index_in_word, i) )
            #else só escreve a palavra original
            else:
                temp_text += word + " "
        i += 1

    #retornar o texto novo 
    return temp_text, error_tuples 

#processar especificamente o arquivo em formato json de abstracts
def process_abstracts(path, path_out, insertion_chance):
    lines = []
    saida = {}
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    for k in tqdm.tqdm(data.keys()):
        item = data[k]
        try:
            text = data[k]['abstracts_pt'].encode('latin-1').decode('utf-8')
        except Exception as e:
            text = data[k]['abstracts_pt']

        text_mod, error_tuples = process_text(text, insertion_chance)
        item['abstracts_pt_error']=text_mod 
        item['error_tuples'] = error_tuples
        saida.update({k:item})
    save_json(path_out, saida)
    

# criar tres versiones con diferentes insertion_chance
process_abstracts('./abstracts_cleaned.json', './abstracts_cleaned_erro-0.10.json', 0.10)
process_abstracts('./abstracts_cleaned.json', './abstracts_cleaned_erro-0.15.json', 0.15)
process_abstracts('./abstracts_cleaned.json', './abstracts_cleaned_erro-0.25.json', 0.25)
