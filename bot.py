import os
import requests
from random import randrange
import re
import urllib.parse
import pathlib
from bs4.element import NavigableString
from numpy.core.numeric import full
import validators
import math
import discord
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
from bs4 import BeautifulSoup
from langdetect import detect
from deep_translator import GoogleTranslator
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

chrome_options = Options()
#chrome_options.add_argument("--headless")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

df_games = pd.read_csv('data.csv')

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.name == GUILD:
            print("SlanttiBot in online!")
            break
        
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content == "!game":
        
        rand_int = randrange(7785)
        game_name = df_games['Name'][rand_int]
        game_provider = df_games['Provider'][rand_int]
        image_url = df_games['Image_url'][rand_int]
        rtp = df_games['RTP'][rand_int]
        pay_lines = df_games['Pay_lines'][rand_int]
        free_spins = df_games['Free_spins'][rand_int]
        bonus_game = df_games['Bonus_game'][rand_int]
        #max_win = df_games['Max Win'][rand_int]
        
        if "nan" in str(rtp) or "Unknown" in str(rtp):
            rtp = "-"
        if "nan" in str(bonus_game):
            bonus_game = "-"
        if "nan" in str(pay_lines):
            pay_lines = "-"
        #if "Unknown" in str(max_win):
            #max_win = "-"

        
        embed=discord.Embed(title=game_name, color=discord.Color.blue())
        #embed.set_author(name=bot.user.display_name, icon_url=bot.user.avatar_url)
        file = discord.File("thumbnail_images/" + image_url, filename=image_url)

        embed.set_thumbnail(url="attachment://" + image_url)
        embed.add_field(name="Provider", value=game_provider, inline=True) 
        
        embed.add_field(name="Free Spins", value=free_spins, inline=True)
        embed.add_field(name="Bonus Game", value=bonus_game, inline=True)
        embed.add_field(name="RTP", value=rtp, inline=True) 
        embed.add_field(name="Pay Lines", value=pay_lines, inline=True)
        #embed.add_field(name="Max Win", value="x123", inline=True)
        #embed.add_field(name="Max Win", value=max_win, inline=True)
        await message.channel.send(file=file, embed=embed)

    if message.content.startswith("!"):
        languageIsSet = False
        df_terms = pd.read_csv('terms_data.csv')
        pd.set_option('display.max_colwidth', None)
        terms = []
        terms_str = []
        is_this_game_banned = "None"
        regex_patterns = open(str(pathlib.Path().resolve()) + r"/regex_patterns.txt", "r")
        
        message_content_without_exclamation_mark = message.content[1:]
        message_content_list = message_content_without_exclamation_mark.split()
        print(message_content_list[-1])
        casino_url = message_content_list[0]

        if message_content_list[-1] != casino_url:
            if "/" not in message_content_list[-1]:
                message_content_list.pop(0)
                is_this_game_banned = ' '.join([str(elem) for elem in message_content_list])
            else:
                language = message_content_list[-1].replace("/", "")
                languageIsSet = True
     
        if "https://" not in casino_url:
            casino_url = "https://" + casino_url
        if validators.url(casino_url):
            please_wait = await message.channel.send("Please wait...")
            get_url = requests.get(casino_url)
            soup = BeautifulSoup(get_url.text, "html.parser")

            if languageIsSet == False:
                if "/fi" in get_url.url:
                        casino_url = get_url.url.replace("/fi", "/en")
                        language = "fi"
                elif "/sv" in get_url.url:
                        casino_url = get_url.url.replace("/sv", "/en")
                        language = "sv"
                elif "/de" in get_url.url:
                        casino_url = get_url.url.replace("/de", "/en")
                        language = "de"
                elif "/no" in get_url.url:
                        casino_url = get_url.url.replace("/no", "/en")
                        language = "no"
                elif "/ja" in get_url.url:
                        casino_url = get_url.url.replace("/ja", "/en")
                        language = "ja"
                elif "/jp" in get_url.url:
                        casino_url = get_url.url.replace("/jp", "/en")
                        language = "ja"
                elif "/ja-jp" in get_url.url:
                        casino_url = get_url.url.replace("/ja-jp", "/en")
                        language = "ja"
                else:
                    language = "english"

            if casino_url in df_terms["Casino Url"].values:
                index_of_value = df_terms[df_terms["Casino Url"]==casino_url].index.values
                terms_from_csv = df_terms["Terms"].iloc[index_of_value].to_string(index=False)
                url_to_terms = df_terms["Url To Terms"].iloc[index_of_value].to_string(index=False)
                char_range = len(terms_from_csv)

                if language != "english":
                    translated = GoogleTranslator(source='auto', target=language).translate(terms_from_csv)
                    terms_from_csv = translated
                if is_this_game_banned == "None":
                    await please_wait.delete()
                    for number in range(int(math.ceil(char_range / 1990))):
                        if(number == 0):
                            await message.channel.send("*" + terms_from_csv[0 : 1990] + "*")
                        else:
                            await message.channel.send("*" + terms_from_csv[number * 1990 : (number + 1) * 1990] + "*")
                    
                    await message.channel.send(url_to_terms)
                else:
                    await please_wait.delete()
                    if is_this_game_banned.lower() in terms_from_csv.lower():
                        await message.channel.send("The game " + "*" + is_this_game_banned + "*" + " was found in the terms and conditions! " + url_to_terms)
                    else:
                        await message.channel.send("*" + is_this_game_banned + "*" + " was not found in the terms and conditions!")
                        return
            else:
                driver = webdriver.Chrome(str(pathlib.Path().resolve()) + r"/chromedriver.exe",options=chrome_options)
                driver.get(casino_url)

                try:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//body//a[contains(@href, 'rules') or contains(@href, 'terms') or contains(@href, 'conditions') or contains(@href, 'Rules') or contains(@href, 'Terms') or contains(@href, 'Conditions')]")))
                except TimeoutException:
                    await message.channel.send("Couldn't find any terms and conditions. " + driver.current_url + " might not be a casino OR the site has a CAPTCHA check that Slanttibot can't pass OR Slanttibot couldn't change the language to English.")
                    return
                finally:
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                links = []
                
                word = ["bonus"]

                for link in soup.findAll('a', href=re.compile(r'\bterms|\brules|\bconditions|\bpolicy')): 
                    links.append(link['href'])
                    print(link)
                    print("<---")
                if any("bonus" in x for x in links):
                    links[:] = [url for url in links if any(sub in url for sub in word)]
                    
                    
                else:
                    driver.get(urllib.parse.urljoin(driver.current_url, links[0]))
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    for link in soup.findAll('a', href=re.compile(r'\bterms|\brules|\bconditions')):
                        links.append(link['href'])
                    if any("bonus" in x for x in links):
                        links[:] = [url for url in links if any(sub in url for sub in word)]
                
                if links != []:
                    
                    driver.get(urllib.parse.urljoin(driver.current_url, links[0]))
                    url_to_terms = driver.current_url
                    try:
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[text()[contains(.,"wagering")]]')))
                    finally:
                        soup = BeautifulSoup(driver.page_source, 'html.parser')
                        
                        driver.quit()
                        for s in soup.select('script'):
                            s.extract()
                        for t in soup.findAll(text=re.compile(r''+ regex_patterns.read(), re.IGNORECASE)):
                                                        
                            if isinstance(t, NavigableString):
                                terms.append(t.parent)
                                if ":" in t:
                                    for sibling in t.parent.next_siblings:
                                        terms.append(sibling)
                                    
                                continue
                            else:    
                                terms.append(t.parent.text)
                                if ":" in t:
                                    terms.append(t.next.text)
                        if terms != []:
                            terms2 = []
                            
                            terms = list(dict.fromkeys(terms))
                            for x in terms:
                                
                                if isinstance(x, NavigableString):
                                    x = str(x)
                                else:
                                    x = x.text
                                x = x.replace("\n", " ").replace("\xa0", " ").replace("*", "").rstrip()
                                
                                terms2.append(x)
                            terms_str = str(terms2)[1:-1]
                            char_range = len(terms_str)
                            
                            get_index = df_terms.iloc[-1]
                            y = get_index.name
                            if y in df_terms.index:
                                y+=1
                                df_terms2 = pd.DataFrame({'Casino Url': casino_url, 'Terms':terms_str, 'Url To Terms':url_to_terms}, index=[y])
                                df_terms2.to_csv('terms_data.csv', mode='a', index=True, header=False)

                            # --- For terms_data.csv reset ---
                            #df_terms2.to_csv('terms_data.csv')
                            #df_terms2 = pd.DataFrame({'Casino Url': casino_url, 'Terms':terms_str, 'Url To Terms':url_to_terms}, index=[0])
                            #df_terms2.to_csv('terms_data.csv') #, mode='a', index=True, header=False
                            
                            if is_this_game_banned == "None":
                                await please_wait.delete()
                                for number in range(int(math.ceil(char_range / 1990))):
                                    if(number == 0):
                                        
                                        await message.channel.send("*" + terms_str[0 : 1990] + "*")
                                       
                                    else:
                                        await message.channel.send("*" + terms_str[number * 1990 : (number + 1) * 1990] + "*")
                                await message.channel.send(url_to_terms)
                            else:
                                await please_wait.delete()
                                if is_this_game_banned.lower() in terms_str.lower():
                                    await message.channel.send("The game " + "*" + is_this_game_banned + "*" + " was found in the terms and conditions! " + url_to_terms)
                                else:
                                    await message.channel.send("*" + is_this_game_banned + "*" + " was not found in the terms and conditions!")
                                    return
                        else:
                            print("terms is empty")
                            await message.channel.send(driver.current_url)
                            return
                else:
                    print("links is empty")
                    return   
        else:
            print("not a valid url")
            return
    else:
        return

bot.run(TOKEN)