from bs4 import BeautifulSoup

import datetime
import json
import os
import time
import threading
import urllib3

cricbuzz_base_url = 'https://www.cricbuzz.com/'
cricbuzz_home_page_url = 'https://www.cricbuzz.com/cricket-match/live-scores'
http = urllib3.PoolManager()


def find_live_matches():
    '''
        This function will search for all the live matches on cricbuzz website and return their cricbuzz url and title as json.
    '''
    r = http.request('GET', cricbuzz_home_page_url)
    soup = BeautifulSoup(r.data, 'html.parser')

    live_matches = []

    for link in soup.find_all('a'):
        url = str(link.get('href'))
        title = link.get('title')
        # Only take live matches.
        if url.startswith("/live-cricket-scores/") and title is not None and "live" in str(title).lower():
            # if url.startswith("/live-cricket-scores/") and title is not None:
            live_matches.append((url[20:], title))

    # Remove duplicate links
    live_matches = list(set(live_matches))

    return json.dumps(live_matches)


def print_score(batsmen_info, team, score, overs):
    os.system("""
              osascript -e 'display notification "{}" with title "{}"'
              """.format(batsmen_info[0][0] + " " + batsmen_info[0][1] + "(" + batsmen_info[0][2] + ")\n" + batsmen_info[1][0] + " " + batsmen_info[1][1] + "(" + batsmen_info[1][2] + ")", team + "    " + score + " (" + overs + ")"))


def find_information(full_score):
    '''
        Processing and cleaning.
    '''
    team = full_score.find_previous_sibling('span')
    team = team.text.strip()

    full_score = full_score.text.strip()
    score, overs = full_score.split('\xa0')
    overs = overs[1:-1]

    return [full_score, score, overs, team]


def find_batsmen_information(battings):
    '''
        Extracting batsmen name, score and no. of balls faced.    
    '''
    batsmen_information = []

    for batting in battings:
        batsmen = batting.find_parent('div').find_parent('div')
        batsmen_name = batsmen.find('a').text
        batsmen_score = batsmen.find_all('div')[2].text
        batsmen_balls_faced = batsmen.find_all('div')[3].text
        batsmen_information.append(
            (batsmen_name, batsmen_score, batsmen_balls_faced))

    return batsmen_information


def fetch_live_match_updates_after_every_over(match):
    current_match = []

    while True:
        r = http.request('GET', cricbuzz_base_url +
                         "live-cricket-scorecard" + match[0])
        soup = BeautifulSoup(r.data, 'html.parser')

        full_score = soup.find('span', class_="pull-right")
        if full_score is None:
            print("Sorry! Unable to fetch score!")
            return

        battings = soup.find_all(
            "span", text='batting')
        batsmen_information = find_batsmen_information(battings)
        [full_score, score, overs, team] = find_information(full_score)

        flag = 0

        if len(current_match) == 0 or current_match[2] != overs:
            current_match = []
            current_match.append(team)
            current_match.append(score)
            current_match.append(overs)
            if '.' not in current_match[2]:
                flag = flag + 1

        # Over is completed
        if flag:
            print_score(batsmen_information, team, score, overs)

        time.sleep(5)


def fetch_live_match_updates_after_every_ball(match):
    current_match = []

    while True:
        r = http.request('GET', cricbuzz_base_url +
                         "live-cricket-scorecard" + match[0])
        soup = BeautifulSoup(r.data, 'html.parser')

        full_score = soup.find('span', class_="pull-right")

        if full_score is None:
            print("Sorry! Unable to fetch score!")
            return

        battings = soup.find_all(
            "span", text='batting')
        batsmen_information = find_batsmen_information(battings)
        [full_score, score, overs, team] = find_information(full_score)

        flag = 0

        if len(current_match) == 0 or current_match[2] != overs:
            current_match = []
            current_match.append(team)
            current_match.append(score)
            current_match.append(overs)
            flag = flag + 1

        # Over is completed
        if flag:
            print_score(batsmen_information, team, score, overs)

        time.sleep(5)


def fetch_live_match_updates_after_every_wicket(match):
    current_match = []

    while True:
        r = http.request('GET', cricbuzz_base_url +
                         "live-cricket-scorecard" + match[0])
        soup = BeautifulSoup(r.data, 'html.parser')

        full_score = soup.find('span', class_="pull-right")
        if full_score is None:
            print("Sorry! Unable to fetch score!")
            return

        battings = soup.find_all(
            "span", text='batting')
        batsmen_information = find_batsmen_information(battings)
        [full_score, score, overs, team] = find_information(full_score)

        flag = 0
        if len(current_match) == 0:
            current_match.append(team)
            current_match.append(score)
            current_match.append(overs)
        elif current_match[2] != overs and score[-1:] > current_match[1][-1:]:
            current_match = []
            current_match.append(team)
            current_match.append(score)
            current_match.append(overs)
            flag = flag + 1

        # Over is completed
        if flag:
            print_score(batsmen_information, team, score, overs)

        time.sleep(5)


def fetch_live_match_updates_after_every_four_or_six(match):
    current_match = []

    while True:
        r = http.request('GET', cricbuzz_base_url +
                         "live-cricket-scorecard" + match[0])
        soup = BeautifulSoup(r.data, 'html.parser')

        full_score = soup.find('span', class_="pull-right")
        if full_score is None:
            print("Sorry! Unable to fetch score!")
            return

        battings = soup.find_all(
            "span", text='batting')
        batsmen_information = find_batsmen_information(battings)
        [full_score, score, overs, team] = find_information(full_score)

        flag = 0
        if len(current_match) > 0 and current_match[2] != overs and int(score.split('-')[0]) - int(current_match[1].split('-')[0]) in [4, 6]:
            flag = flag + 1

        current_match = []
        current_match.append(team)
        current_match.append(score)
        current_match.append(overs)

        # Over is completed
        if flag:
            print_score(batsmen_information, team, score, overs)

        time.sleep(5)


def fetch_live_match_updates_after_every_major_moment(match):
    current_match = []

    while True:
        r = http.request('GET', cricbuzz_base_url +
                         "live-cricket-scorecard" + match[0])
        soup = BeautifulSoup(r.data, 'html.parser')

        full_score = soup.find('span', class_="pull-right")
        if full_score is None:
            print("Sorry! Unable to fetch score!")
            return

        battings = soup.find_all(
            "span", text='batting')
        batsmen_information = find_batsmen_information(battings)
        [full_score, score, overs, team] = find_information(full_score)

        flag = 0
        if len(current_match) > 0 and current_match[2] != overs and ('.' not in overs or int(score.split('-')[0]) - int(current_match[1].split('-')[0]) in [4, 6] or score[-1:] > current_match[1][-1:]):
            flag = flag + 1

        current_match = []
        current_match.append(team)
        current_match.append(score)
        current_match.append(overs)

        # Major momment has happened
        if flag:
            print_score(batsmen_information, team, score, overs)

        time.sleep(5)


def helper():
    live_matches = find_live_matches()
    live_matches = json.loads(live_matches)

    print("\nSelect which match you want to follow:\n")
    for idx, match in enumerate(live_matches):
        print(idx+1, match[1])
    selection = input()

    try:
        selection = int(selection)
    except ValueError:
        print("Please enter an integer.")
        return

    if selection < 1 or selection > len(live_matches):
        print("Invalid input.")
        return

    print("\nWhich type of summary you want to see:\n\n1. After every over.\n2. After every ball.\n3. After every 4/6.\n4. After every wicket.\n5. After every 4/6/wicket/over.")
    summary_type = input()

    try:
        summary_type = int(summary_type)
    except ValueError:
        print("Please enter an integer.")
        return

    if summary_type == 1:
        timerThread = threading.Thread(
            target=fetch_live_match_updates_after_every_over, kwargs=dict(match=live_matches[selection-1]))
        timerThread.start()
    elif summary_type == 2:
        timerThread = threading.Thread(
            target=fetch_live_match_updates_after_every_ball, kwargs=dict(match=live_matches[selection-1]))
        timerThread.start()
    elif summary_type == 3:
        timerThread = threading.Thread(
            target=fetch_live_match_updates_after_every_four_or_six, kwargs=dict(match=live_matches[selection-1]))
        timerThread.start()
    elif summary_type == 4:
        timerThread = threading.Thread(
            target=fetch_live_match_updates_after_every_wicket, kwargs=dict(match=live_matches[selection-1]))
        timerThread.start()
    elif summary_type == 5:
        timerThread = threading.Thread(
            target=fetch_live_match_updates_after_every_major_moment, kwargs=dict(match=live_matches[selection-1]))
        timerThread.start()
    else:
        print("Invalid selection.")


if __name__ == "__main__":
    helper()
