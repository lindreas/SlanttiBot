import os
import requests
from random import randrange
import re
import urllib.parse
import pathlib
from bs4.element import NavigableString
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
from deep_translator import GoogleTranslator
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

bot = commands.Bot(command_prefix='!', activity=discord.Game(name="!help"))

@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.name == GUILD:
            print("SlanttiBot in online!")
            break
        
@bot.event
async def on_message(message):
    df_games = pd.read_csv('data.csv')
    df_games_lowercase = pd.read_csv('data.csv')

    if message.author == bot.user:
        return

    if message.content == "!help":
        embed=discord.Embed(title="How to use SlanttiBot", color=discord.Color.from_rgb(228,175,255))
        file = discord.File("thumbnail_images/help.png", filename="help.png")
        embed.set_thumbnail(url="attachment://help.png")
        embed.add_field(name="!examplecasino.com", value="Enter a url to an online casino to fetch the games that are banned from playing with bonusmoney.", inline=True)
        embed.add_field(name="!examplecasino.com /de", value="Translate the result from english. Available languages: \n`arabic: ar \nbulgarian: bg \ncatalan: ca \nchinese (simplified): zh-CN \nchinese (traditional): zh-TW \ncroatian: hr \nczech: cs \ndanish: da \ndutch: nl \nestonian: et \nfinnish: fi \nfrench: fr`", inline=True)
        embed.add_field(name="\u200b", value="`german: de \ngreek: el \nhungarian: hu \nicelandic: is \nitalian: it \njapanese: ja \nkorean: ko \nlatvian: lv \nlithuanian: lt \nnorwegian: no \npolish: pl \nportuguese: pt \nrussian: ru \nslovak: sk \nslovenian: sl \nspanish: es \nswedish: sv \nturkish: tr`", inline=True) 
        embed.add_field(name="!examplecasino.com Book of Dead", value="Check if a specific game is banned.", inline=True)
        embed.add_field(name="!stats Book of Dead", value="Returns the stats of a chosen game.", inline=True) 
        embed.add_field(name="!game", value="SlanttiBot suggests a random game to you!", inline=True)

        await message.channel.send(file=file, embed=embed)

    if message.content == "!game":

        rand_int = randrange(7785)
        game_name = df_games['Name'][rand_int]
        game_provider = df_games['Provider'][rand_int]
        image_url = df_games['Image_url'][rand_int]
        rtp = df_games['RTP'][rand_int]
        pay_lines = df_games['Pay_lines'][rand_int]
        free_spins = df_games['Free_spins'][rand_int]
        bonus_game = df_games['Bonus_game'][rand_int]

        if "nan" in str(rtp) or "Unknown" in str(rtp):
            rtp = "-"
        if "nan" in str(bonus_game):
            bonus_game = "-"
        if "nan" in str(pay_lines):
            pay_lines = "-"
        
        embed=discord.Embed(title=game_name, color=discord.Color.from_rgb(228,175,255))
        file = discord.File("thumbnail_images/" + image_url.lower(), filename=image_url.lower())

        embed.set_thumbnail(url="attachment://" + image_url.lower())
        embed.add_field(name="Provider", value=game_provider, inline=True) 
        
        embed.add_field(name="Free Spins", value=free_spins, inline=True)
        embed.add_field(name="Bonus Game", value=bonus_game, inline=True)
        embed.add_field(name="RTP", value=rtp, inline=True) 
        embed.add_field(name="Pay Lines", value=pay_lines, inline=True)

        await message.channel.send(file=file, embed=embed)

    if message.content.startswith("!stats"):
        message_content_without_exclamation_mark = message.content[1:]
        message_content_list = message_content_without_exclamation_mark.split()
        game_for_stats = ' '.join([str(elem) for elem in message_content_list[1:]])
        
        df_games_lowercase['Name'] = df_games_lowercase['Name'].str.lower()
        game_for_stats_index = df_games.loc[df_games_lowercase['Name'] == game_for_stats.lower()].index.values
        
        if game_for_stats_index.size < 1:
            await message.channel.send("Game " + "**" + game_for_stats + "**" + " not found!")
        else:
            game_for_stats_index = int(game_for_stats_index)
            game_name = df_games['Name'][game_for_stats_index]
            game_provider = df_games['Provider'][game_for_stats_index]
            image_url = df_games['Image_url'][game_for_stats_index]
            rtp = df_games['RTP'][game_for_stats_index]
            pay_lines = df_games['Pay_lines'][game_for_stats_index]
            free_spins = df_games['Free_spins'][game_for_stats_index]
            bonus_game = df_games['Bonus_game'][game_for_stats_index]
            
            if "nan" in str(rtp) or "Unknown" in str(rtp):
                rtp = "-"
            if "nan" in str(bonus_game):
                bonus_game = "-"
            if "nan" in str(pay_lines):
                pay_lines = "-"

            
            embed=discord.Embed(title=game_name, color=discord.Color.from_rgb(228,175,255))
            
            file = discord.File("thumbnail_images/" + image_url.lower(), filename=image_url.lower())

            embed.set_thumbnail(url="attachment://" + image_url.lower())
            embed.add_field(name="Provider", value=game_provider, inline=True) 
            
            embed.add_field(name="Free Spins", value=free_spins, inline=True)
            embed.add_field(name="Bonus Game", value=bonus_game, inline=True)
            embed.add_field(name="RTP", value=rtp, inline=True) 
            embed.add_field(name="Pay Lines", value=pay_lines, inline=True)

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

            if "/fi" in get_url.url:
                    casino_url = get_url.url.replace("/fi", "/en")
            elif "/sv" in get_url.url:
                    casino_url = get_url.url.replace("/sv", "/en")
            elif "/da" in get_url.url:
                    casino_url = get_url.url.replace("/da", "/en")
            elif "/de" in get_url.url:
                    casino_url = get_url.url.replace("/de", "/en")
            elif "/no" in get_url.url:
                    casino_url = get_url.url.replace("/no", "/en")
            elif "/ja" in get_url.url:
                    casino_url = get_url.url.replace("/ja", "/en")
            elif "/jp" in get_url.url:
                    casino_url = get_url.url.replace("/jp", "/en")
            elif "/ja-jp" in get_url.url:
                    casino_url = get_url.url.replace("/ja-jp", "/en")
            elif "/nz" in get_url.url:
                    casino_url = get_url.url.replace("/nz", "/en")
            elif "/ca" in get_url.url:
                    casino_url = get_url.url.replace("/ca", "/en")
            elif "/gb" in get_url.url:
                    casino_url = get_url.url.replace("/gb", "/en")
            if languageIsSet == False:
                language = "english"

            if casino_url in df_terms["Casino Url"].values:
                index_of_value = df_terms[df_terms["Casino Url"]==casino_url].index.values
                terms_from_csv = df_terms["Terms"].iloc[index_of_value].to_string(index=False)
                url_to_terms = df_terms["Url To Terms"].iloc[index_of_value].to_string(index=False)
                char_range = len(terms_from_csv)

                if languageIsSet == True:
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
                    
                    await message.channel.send("`The result might not include the whole list. Please check it at:` " + url_to_terms)
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
                pattern = re.compile(r''+ regex_patterns.read(), re.IGNORECASE)

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
                        
                        for s in soup.select('script'):
                            s.extract()
                    
                        for t in soup.findAll(text=True):
                            if isinstance(t, NavigableString):
                                match = pattern.search(t)
                                if match:
                                    terms.append(match.string)
                                    if ":" in match.string:
                                        for sibling in t.parent.next_siblings:
                                            terms.append(sibling)
                                    continue
                            else:
                                match = pattern.search(t)
                                if match:
                                    terms.append(match.string)
                                    if ":" in match.string:
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
                            
                            if languageIsSet == True:
                                if language != "english":
                                    translated = GoogleTranslator(source='auto', target=language).translate(terms_str)
                                    terms_str = translated
                            if is_this_game_banned == "None":
                                await please_wait.delete()
                                for number in range(int(math.ceil(char_range / 1990))):
                                    if(number == 0):
                                        await message.channel.send("*" + terms_str[0 : 1990] + "*")
                                    else:
                                        await message.channel.send("*" + terms_str[number * 1990 : (number + 1) * 1990] + "*")
                                await message.channel.send("`The result might not include the whole list. Please check it at:` " + url_to_terms)
                            else:
                                await please_wait.delete()
                                if is_this_game_banned.lower() in terms_str.lower():
                                    await message.channel.send("The game " + "*" + is_this_game_banned + "*" + " was found in the terms and conditions! " + url_to_terms)
                                else:
                                    await message.channel.send("*" + is_this_game_banned + "*" + " was not found in the terms and conditions!")
                                    return
                        else:
                            await please_wait.delete()
                            await message.channel.send("Could not find any games!")
                            return
                else:
                    await please_wait.delete()
                    await message.channel.send("Could not find any games!")
                    return   
        else:
            await message.channel.send("Not a valid url! (example.com)")
            return
    else:
        return

bot.run(TOKEN)