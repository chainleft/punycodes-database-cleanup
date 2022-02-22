from emoji import UNICODE_EMOJI
import re
import datetime
import pandas as pd

def detectAlphabet(line):
    maxchar = max(line)
    if '\u3400' <= maxchar <= '\u9fff':
        return 'Chinese'
    elif '\u0600' <= maxchar <= '\u06ff':
        return 'Arabic'
    elif '\u3040' <= maxchar <= '\u309f':
        return 'Hiragana'
    elif '\u30a0' <= maxchar <= '\u30ff':
        return 'Katakana'
    elif '\uac00' <= maxchar <= '\ud7af':
        return 'Hangul'
    elif '\u0370' <= maxchar <= '\u03ff':
        return 'Greek'
    elif '\u1f00' <= maxchar <= '\u1fff':
        return 'Greek'
    elif '\u0400' <= maxchar <= '\u04ff':
        return 'Cyrillic'
    elif '\u0e00' <= maxchar <= '\u0e7f':
        return 'Thai'
    elif '\u0900' <= maxchar <= '\u097f':
        return 'Devanagari'
    elif '\u0980' <= maxchar <= '\u09ff':
        return 'Bengali'
    elif '\u1400' <= maxchar <= '\u167f':
        return 'Cyrillic'
    elif '\u0590' <= maxchar <= '\u05ff':
        return 'Hebrew'
    elif '\u0000' <= maxchar <= '\u024f':
        return 'Latin'
    elif '\u0a00' <= maxchar <= '\u0a7f':
        return 'Gurmukhi'
    elif '\u0a80' <= maxchar <= '\u0aff':
        return 'Gujarati'
    elif '\u0b80' <= maxchar <= '\u0bff':
        return 'Tamil'
    elif '\u0d80' <= maxchar <= '\u0dff':
        return 'Sinhala'
    elif '\u0c00' <= maxchar <= '\u0c7f':
        return 'Telugu'
    elif '\u13a0' <= maxchar <= '\u13fd':
        return 'Cherokee'
    elif '\u0c80' <= maxchar <= '\u0cff':
        return 'Kannada'
    elif '\u0b00' <= maxchar <= '\u0b7f':
        return 'Oriya'
    else:
    	return 'Other'

def hasEmoji(s):
    s_list = list(s)
    count = 0
    for i in s_list:
        count += i in UNICODE_EMOJI['en']
    return bool(count)

asciis = ('ϾϿ','ಠ_ಠ','ಠ⁔ಠ','┣▇▇▇═─','(๏y๏)','┌∩┐﴾◣_◢﴿┌∩┐','ლ﴾ಠ益ಠლ﴿','❨╯°□°❩╯෴┻━┻','╯❨°□°❩╯෴┻━┻','❨╯°□°❩╯︵┻━┻','⧹o⧸','┬─┬ノ❨º⸏ºノ❩','┬─┬ノ❨°＿°ノ❩','┬─┬ノ❨°⸏°ノ❩','┬─┬ノ❨°□°ノ❩','┬─┬ノ❨o_oノ❩','┬─┬ノ❨o⸏oノ❩','┬─┬ノ❨º＿ºノ❩','ಠ＿ಠ','ಠ⸏ಠ')

df_codes = pd.read_csv('puny_backup.csv')
df_codes = df_codes.drop_duplicates(keep='first')
df_codes = df_codes.dropna()
df_codes = df_codes[{'ID','Display Punycode'}]
df_codes = df_codes.reset_index(drop=True)
#df_codes['ID'] = df_codes['ID'].str.lower()

df = pd.read_excel('Punycodes_rawdata.xlsx')
df.rename(columns={'Domain': 'ID','First registration': 'Timestamp','Url': 'Link'}, inplace=True)
df = df.drop_duplicates(keep='first')
df = df.dropna()

df['Timestamp'] = df['Timestamp'].str.replace('.','')
Hpart1 = df['Timestamp'].str.split(", ").str[2].str.split(":").str[0].str.split(" ").str[0]
Hpart2 = df['Timestamp'].str.split(", ").str[2].str.split(" ").str[1]
Mins = df['Timestamp'].str.split(", ").str[2].str.split(":").str[1].str.split(" ").str[0].fillna('00')
Days = df['Timestamp'].str.split(", ").str[0].str.split(" ").str[1]
Months = pd.to_datetime(df['Timestamp'].str[:3], format="%b").dt.month.astype(str)
Years = df['Timestamp'].str.split(", ").str[1]
df['RealTimestamp'] = Years + "-" + Months + "-" + Days + " " + Hpart1 + ":" + Mins + " " +  Hpart2

df['Timestamp'] = pd.to_datetime(df['RealTimestamp'], format='%Y-%m-%d %I:%M %p')
df['Year'] = df['Timestamp'].dt.year
df['Month'] = df['Timestamp'].dt.month
df['Day'] = df['Timestamp'].dt.day
df['Hour'] = df['Timestamp'].dt.hour
df['Minute'] = df['Timestamp'].dt.minute
df = df[Years.astype(int)<2018]
df.drop(['RealTimestamp'], axis=1, inplace=True)
df = df.sort_values(by=['Timestamp'])
df = df.reset_index(drop=True)

df_merged = pd.merge(df,df_codes,on='ID',how='left').drop_duplicates(keep='first')

df = df_merged



df.loc[~df['ID'].str.contains(pat = '/'),'Prefix'] = df['ID'].str.split('/').str[0] + '/'
df.loc[~df['ID'].str.contains(pat = '/'),'Prefix'] = ''
df.loc[~df['ID'].str.contains(pat = '/'),'Punycode'] = df['ID'].str.split('/').str[1]
df.loc[~df['ID'].str.contains(pat = '/'),'Punycode'] = df['ID']

puny_categories = list()
alphabets = list()

for i in range(len(df.index)):
    puny = df['Display Punycode'][i]
    if pd.isna(puny):
        puny_category = "Word"
        alphabet = ""
    else:
        alphabet = detectAlphabet(puny)
        if hasEmoji(puny):
            puny_category = "Emoji"
            alphabet = ""
        elif alphabet == "Chinese":
            puny_category = "Word"
        elif puny in asciis:
            puny_category = "ASCII Art"
            alphabet = ""
        elif len(puny) == 1:
            if alphabet == "Other":
                puny_category = "Symbol"
                alphabet = ""
            else:
                puny_category = "Character"
        else:
            puny_category = "Word"
    puny_categories.append(puny_category)
    alphabets.append(alphabet)

df['Category'] = puny_categories
df['Alphabet'] = alphabets

df['Misprint'] = False
df['Misprint'][pd.isna(df['Display Punycode'])] = True
df.index.name = 'Rank'

df['Block'] = ''

cols = ['ID','Prefix','Punycode','Display Punycode','Link','Block','Year','Month','Day','Hour','Minute','Timestamp','Category','Alphabet','Misprint']
df = df[cols]

df.to_excel('~/Documents/Punycodes/punycode_cleaned.xlsx', sheet_name='Sheet1')
#df.to_csv('~/Documents/Punycodes/punycode_cleaned.csv',encoding='UTF-32')
