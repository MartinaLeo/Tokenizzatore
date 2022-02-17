import nltk
import re
from nltk import bigrams
from nltk import trigrams
import xlsxwriter
import pandas as pd
import os


def estraiTokens(frasi, non_normalizzare):
    tokensTOT = list()
    tokensTOT_normalizzati = list()
    for frase in frasi:
        nuova_frase = re.sub(r"['’]", "' ", frase)
        tokens = nltk.word_tokenize(nuova_frase)
        tokensTOT += tokens
    for token in tokensTOT:
        if token == "'":
            index = tokensTOT.index(token)
            tokensTOT[index-1] += token
            tokensTOT.remove(token)
    for token in tokensTOT:
        if token in non_normalizzare:
            tokensTOT_normalizzati.append(token)
        else:
            tokensTOT_normalizzati.append(token.lower())
    return tokensTOT_normalizzati


def ottieniClassiFrequenza(tokens):
    freq = dict()
    for token in tokens:
        freq[token] = freq.get(token, 0) + 1

    lst = list()
    for k,v in freq.items():
        lst.append((v,k))
        lst = sorted(lst)
        # crea un dizionario per la classe di frequenza e uno per zipf
        diz_classe= dict()
        for e in lst:
            diz_classe[e[0]] = diz_classe.get(e[0], 0)+1

        diz_zipf = dict()
        rango = 1
        for e in sorted(lst, reverse=True):
            diz_zipf[rango] = e[0]
            rango +=1
    return diz_classe.items(), diz_zipf.items()


def calcolaCumulataParoleTipo(classeFreq, len_vocabolario):
    colonne = ['Classe', 'Cumulata Tipo']
    df = pd.DataFrame(columns=colonne)
    index = 1
    classeFreq= sorted(list(classeFreq))
    classe = classeFreq[0][0]
    cum = classeFreq[0][1] / len_vocabolario
    df.loc[index] = [f'v{classe}', cum]
    index+=1
    for e in classeFreq[1:]:
        classe = e[0]
        cum += e[1] / len_vocabolario
        if cum >= 0.99:
            cum = round(cum)
        df.loc[index] = [f'v{classe}', cum]
        index +=1
    return df


def calcolaCumulataParoleToken(classeFreq, num_tokens):
    colonne = ['Classe', 'Cumulata Token']
    df = pd.DataFrame(columns=colonne)
    index = 1
    classeFreq = sorted(list(classeFreq))
    classe = classeFreq[0][0]
    cum = classeFreq[0][1] / num_tokens
    df.loc[index] = [f'v{classe}', cum]
    index += 1

    for e in classeFreq[1:]:
        classe = e[0]
        cum += (e[1] * e[0]) / num_tokens
        if cum >= 0.99:
            cum = round(cum)
        df.loc[index] = [f'v{classe}', cum]
    return df


def crea_foglioxlsx(writer, df, sheet, nome_titolo='', crea_grafico=False):
    # Convert the dataframe to an XlsxWriter Excel object.
    df.to_excel(writer, sheet_name=sheet)

    # Get the xlsxwriter objects from the dataframe writer object.
    workbook = writer.book
    worksheet = writer.sheets[sheet]
    if crea_grafico:
        # Create a chart object.
        chart = workbook.add_chart({'type': 'line'})

        # Get the dimensions of the dataframe.
        (max_row, max_col) = df.shape

        # Configure the series of the chart from the dataframe data.

        #     [sheetname, first_row, first_col, last_row, last_col]
        chart.add_series({
            'categories': [sheet, 1, 1, max_row, 1], # x axis
            'values': [sheet, 1, 2, max_row, 2], # y axis
            'line': {'color': '#4472C4'}
        })

        # setting titles
        chart.set_title({'name': nome_titolo})
        chart.set_legend({'delete_series': [0]})
        chart.set_x_axis({'name': [sheet, 0, 1]})
        chart.set_y_axis({'name': [sheet, 0, 2]})

        # inserisce il grafico (riga, colonna, foglio)
        worksheet.insert_chart(1, 3, chart)


def tokenizza(testo, path, non_normalizzare=None):
    if non_normalizzare is None:
        non_normalizzare = []
    path = path.rstrip()
    if not os.path.exists(path):
        os.makedirs(path)
    path += '/'
    sent_tokenizer = nltk.data.load('tokenizers/punkt/italian.pickle')
    frasi = sent_tokenizer.tokenize(testo)
    tokens = estraiTokens(frasi, non_normalizzare)
    lunghezza_testo = len(tokens)
    vocabolario = list(set(tokens))
    lunghezza_vocabolario = len(vocabolario)
    TTR = lunghezza_vocabolario/lunghezza_testo
    classe_frequenza, distribuzione_zipf = ottieniClassiFrequenza(tokens)
    df_cum_type = calcolaCumulataParoleTipo(classe_frequenza, lunghezza_vocabolario)
    df_cum_tok = calcolaCumulataParoleToken(classe_frequenza, lunghezza_testo)

    df_tok = pd.DataFrame(columns=['Token'])
    index = 1
    for token in tokens:
        df_tok.loc[index] = [token]
        index += 1

    df_stats = pd.DataFrame(columns=['Totale Tokens', 'Totale parole tipo', 'TTR'])
    df_stats.loc[1] = [lunghezza_testo, lunghezza_vocabolario, TTR]

    df_freq = pd.DataFrame(columns=['Classe', 'Frequenza'])
    index = 1
    for e in classe_frequenza:
        df_freq.loc[index] = [e[0], e[1]]
        index += 1

    df_zipf = pd.DataFrame(columns=['Rango', 'Frequenza'])
    index = 1
    for e in distribuzione_zipf:
        df_zipf.loc[index] = [e[0], e[1]]
        index += 1

    # crea il Pandas Excel writer usando XlsxWriter come engine
    writer = pd.ExcelWriter(path +'Statistiche.xlsx', engine='xlsxwriter')

    crea_foglioxlsx(writer, df_freq, 'Sheet1', crea_grafico=True, nome_titolo='Spettro di frequenza')
    crea_foglioxlsx(writer, df_zipf, 'Sheet2', crea_grafico=True, nome_titolo='Distribuzione di Zipf')
    crea_foglioxlsx(writer, df_tok, 'Sheet3')
    crea_foglioxlsx(writer, df_stats, 'Sheet4')
    crea_foglioxlsx(writer, df_cum_type, 'Sheet5')
    crea_foglioxlsx(writer, df_cum_tok, 'Sheet6')

    # chiude il writer e salva il contenuto del foglio excel
    writer.save()