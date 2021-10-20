# ScarperSocial
Scrape emails, phone numbers and social media accounts from a website. <br>
You can use the found information to gather more information or just find ways to contact the site.
<p align="left">
    <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="python" width="70" height="70"/>
    </p>
    
## Installation & Setup

```bash
git clone https://github.com/kal1gh0st/ScarperSocial.git
cd ScarperSocial
pip3 install -r requirements.txt
```
<br>

## Usage
```bash
# Simple scan
python3 TheScrapper.py --url URL
# Use found URLS and scan them too
python3 TheScrapper.py --url URL --crawl
# Get more info about the found socialmedia accounts
python3 TheScrapper.py --url URL -s
```
*If you dont like the banner just add "-b".*
<br>

![immagine](https://user-images.githubusercontent.com/56889513/136005295-71688f39-a643-4954-92b2-38b3a8bccf61.png)


## SocialMedia
If you want to add more SocialMedia sites just append them to the [`socials.txt`](./socials.txt) file and if you want, you can add them with a [pull request](https://www.lifewire.com/best-products-4781319).

## TODO
 - [ ] Verbose Mode
 - [ ] API

# Bugs or ideas?
If you find any bug or if you have some ideas create an [issue](https://github.com/champmq/TheScrapper/issues).
