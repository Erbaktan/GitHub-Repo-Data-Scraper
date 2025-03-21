import pandas as pd
import requests
import time
import calendar
import openpyxl

git_api = 'https://api.github.com/repos/'
per_page = 100  # Number of items per page
list_languages = []  # List of languages

# Function for adding a language to the filter
def add_languages():
    while True:
        text = input("\nEnter language name or type STOP: \n").strip()
        if text.lower() == "stop":
            break
        if text:
            list_languages.append(text.lower())
        else:
            print("Invalid input, try again.")

first_year = int(input('Enter the first year: '))  # First date of the data
last_year = int(input('Enter the last year: '))  # Last date of the data

while True:
    question = input('Do you want to get all languages? (yes/no) ').strip().lower()
    if question == "no":
        add_languages()  # Filter languages
    else:
        break
github_token = input('Enter your GitHub Token: ').strip()


def get_repo_data(year, month):
    repo_list = []  # List to collect data
    page = 1  # GitHub API paginates results
    
    
    headers = {"Authorization": f"token {github_token}"}
    
    date_from = f"{year}-{month:02d}-01"
    date_to = f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]}"  # Get last day of the month
    
    while len(repo_list) < 100:
        url = f"https://api.github.com/search/repositories?q=created:{date_from}..{date_to}&sort=stars&order=desc&per_page={per_page}&page={page}"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            if "items" not in data or not data["items"]:
                break
            
            for repo in data["items"]:
                repo_lang = repo["language"]
                if repo_lang and repo_lang.lower() in list_languages:
                    repo_list.append({
                        "Name": repo["name"],
                        "Author": repo["owner"]["login"],
                        "Stars": repo["stargazers_count"],
                        "Forks": repo["forks_count"],
                        "Language": repo_lang,
                        "Year": year,
                        "Month": month,
                        "Date of publication": repo["created_at"],
                        "URL": repo["html_url"]
                    })
                if len(repo_list) >= 100:
                    break
            
            if len(data["items"]) < per_page:
                break
            
            page += 1  
        else:
            print(f"Request error ({year}-{month}): {response.status_code}")
            time.sleep(10)
            break
    
    return repo_list

all_repos = []

for year in range(first_year, last_year + 1):
    for month in range(1, 13):
        print(f"📅 {year}-{month:02d} | Fetching popular repositories...")
        repos = get_repo_data(year, month)
        all_repos.extend(repos)
        time.sleep(2)  # Delay to avoid API rate limits

df = pd.DataFrame(all_repos)

with pd.ExcelWriter("repos_filtered.xlsx", engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="Repositories", index=False)

print("✅ Data successfully collected and saved in repos_filtered.xlsx!")