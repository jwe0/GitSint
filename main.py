import tls_client, os
from bs4 import BeautifulSoup



class Scrape:
    def __init__(self, username) -> None:
        self.session = tls_client.Session()
        self.user = username
        self.html = ""
        self.repositoies = []
        self.longest_name = 0
        self.longest_desc = 0

    def Make_Downloads(self):
        if not os.path.exists("/Downloads"):
            os.mkdir("Downloads")

    def Verify_User(self):
        response = self.session.get("https://github.com/{}".format(self.user))

        if response.status_code == 200:
            return True
        return False
    
    def Is_Readme(self):
        url = "https://raw.githubusercontent.com/{}/main/README.md".format(f"{self.user}/{self.user}")

        response = self.session.get(url)
        if response.status_code == 200:
            return (True, "Read me file exists auto downloaded to Downloads/{folder}/{name}.md".format(name=self.user, folder=self.user), response.text)
        return (False, "No Readme", None)
    
    def Is_gitsite(self):
        url = "https://{}.github.io".format(self.user)

        response = self.session.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.find('title').get_text(strip=True)
            return (True, "Git site exists auto downloaded to Downloads/{folder}/{name}.html".format(name=self.user, folder=self.user), title, response.content)
        else:
            return (False, "No git site found", "", "")



    def Start_Scrape(self):
        if not self.Verify_User():
            print("User not found")
            exit()
        page = self.session.get("https://github.com/{}".format(self.user)).text
        self.html = page


        



        name = self.Name()
        bio = self.Bio()
        location = self.Locations()
        links = self.Links()
        status = self.Status()
        org = self.Organizations()
        readme = self.Is_Readme()
        site = self.Is_gitsite()

        if readme[0]:
            if not os.path.exists("Downloads/{}".format(self.user)):
                os.mkdir("Downloads/{}".format(self.user))
            with open("Downloads/{folder}/{name}.md".format(name=self.user, folder=self.user), 'w') as f:
                f.write(readme[2])

        if site[0]:
            if not os.path.exists("Downloads/{}".format(self.user)):
                os.mkdir("Downloads/{}".format(self.user))
            with open("Downloads/{folder}/{name}.html".format(name=self.user, folder=self.user), 'w') as f:
                f.write(site[3].decode())


        print("\n > General\n")
        print("Name:         [{}]".format(name))
        print("Bio:          [{}]".format(bio))
        print("Location:     [{}]".format(location))
        print("Links:        [{}]".format(links))
        print("Status:       [{}]".format(status))
        print("Organiation:  [{}]".format(org))
        print("Readme?       [{}]".format(readme[1]))
        print("Gitsite?      [{msg}{title}]".format(msg=site[1], title=f" | {site[2]}" if site[2] else ""))

        print()

        

        self.Repositories()
        self.Followers()

    def Name(self):
        return BeautifulSoup(self.html, 'html.parser').find('span', itemprop="name").get_text(strip=True)
    
    def Bio(self):
        return BeautifulSoup(self.html, 'html.parser').find('div', class_='p-note user-profile-bio mb-3 js-user-profile-bio f4').get('data-bio-text') if BeautifulSoup(self.html, 'html.parser').find('div', class_='p-note user-profile-bio mb-3 js-user-profile-bio f4') else "No Bio"
    
    def Links(self):
        return BeautifulSoup(self.html, 'html.parser').find('a', class_="Link--primary").get('href') if BeautifulSoup(self.html, 'html.parser').find('a', class_="Link--primary") else "No links"

    def Locations(self):
        return BeautifulSoup(self.html, 'html.parser').find('li', class_='vcard-detail pt-1 hide-sm hide-md', itemprop='homeLocation').get('aria-label').replace("Home location: ", "") if BeautifulSoup(self.html, 'html.parser').find('li', class_='vcard-detail pt-1 hide-sm hide-md', itemprop='homeLocation') else "No location"

    def Status(self):
        return BeautifulSoup(self.html, 'html.parser').find('div', class_='user-status-message-wrapper f6 color-fg-default no-wrap').get_text(strip=True) if BeautifulSoup(self.html, 'html.parser').find('div', class_='user-status-message-wrapper f6 color-fg-default no-wrap') else "No Status"

    def Repositories(self):
        content = self.session.get("https://github.com/{}?tab=repositories".format(self.user)).text

        hrefs = []
        names = []
        descriptions = []

        soup = BeautifulSoup(content, 'html.parser')

        repositories = soup.find_all('li', class_='col-12')

        for repositry in repositories:

            hrefs.append(repositry.find('a').get('href'))

            names.append(repositry.find('a', itemprop="name codeRepository").get_text(strip=True))

            description = repositry.find('p', itemprop="description")

            descriptions.append(description.get_text(strip=True)[:20] + "..."  if description else "No description found")

        self.longest_name = max(len(name) for name in names)
        self.longest_desc = max(len(desc) for desc in descriptions)
        self.repositoies = names.copy()

        
        print("\n > Repositories\n")
        for i in range(len(names)):

            name = names[i]
            description = descriptions[i]

            while len(name) < self.longest_name:
                name += " "

            while len (description) < self.longest_desc:
                description += " "

            print(f"{name}\t\t{description}\t\t{hrefs[i]}")
                




    def Followers(self):
        followers = []

        content = self.session.get("https://github.com/{}?tab=followers".format(self.user)).text

        soup = BeautifulSoup(content, 'html.parser')

        follower_links = soup.find_all('a', class_="d-inline-block no-underline mb-1")

        for follower_link in follower_links:
            follower_span = follower_link.find('span', class_='Link--secondary pl-1')
            
            if follower_span:
                followers_u = follower_span.get_text(strip=True)
                followers.append(followers_u)

        print("\n > Followers\n")

        for follower in followers:
            print("{count}. {follower}".format(count=followers.index(follower) + 1, follower=follower))




    def Organizations(self):
        return BeautifulSoup(self.html, 'html.parser').find('a', class_='avatar-group-item').get('aria-label') if BeautifulSoup(self.html, 'html.parser').find('a', class_='avatar-group-item') else "No organization"



class Main:
    def Main():
        user = input("Username: ")
        scrape = Scrape(user)
        scrape.Make_Downloads()

        scrape.Start_Scrape()

if __name__ == "__main__":
    Main.Main()