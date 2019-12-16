import csv
import itertools
import WinExp

# Takes 3-letter codes for away, home, and desired team. Returns 'a' if the desired team is the away team,
# 'h' if it's the home team, and 'x' if it's neither.
def pitcher_team(awayTeam, homeTeam, teamCode):
    if teamCode == awayTeam:
        return 'a'
    if teamCode == homeTeam:
        return 'h'
    else:
        return 'x'

# Returns lists of scores in each inning using the linescores from Retrosheet's game logs. The home team
# not batting in the bottom of the last inning is represented as a 0, not an 'x'
def generate_inninglists(awayLinescore, homeLinescore):
    ddInning = False
    ddInningScore = ''
    awayInnings = []
    homeInnings = []  
    for inning in awayLinescore:
        if ddInning == 'val1':
            ddInningScore = ddInningScore + inning
            ddInning = 'val2'
        elif ddInning == 'val2':
            ddInningScore = ddInningScore + inning
            ddInning = False
            awayInnings.append(int(ddInningScore))
            ddInningScore = ''
        elif inning == '(':
            ddInning = 'val1'
        elif inning == ')':
            continue
        elif inning == 'x':
            continue
        else:
            awayInnings.append(int(inning))
    for inning in homeLinescore:
        if ddInning == 'val1':
            ddInningScore = ddInningScore + inning
            ddInning = 'val2'

        elif ddInning == 'val2':
            ddInningScore = ddInningScore + inning
            ddInning = False
            homeInnings.append(int(ddInningScore))
            ddInningScore = ''

        elif inning == '(':
            ddInning = 'val1'

        elif inning == ')':
            continue

        elif inning == 'x':
            homeInnings.append(0)

        else:
            homeInnings.append(int(inning))

    return awayInnings, homeInnings

# Implemented rather poorly. 
# This takes a list of innings from each team, as well as the team that the pitcher is on. Each half inning, it uses
# win_with_pitcher to determine if our hypothetical pitcher can come in and finish out the game. It either returns
# False if the pitcher can win the game, or a tuple of (awayScore, homeScore, inning, side, pitcherTeam) at the point
# which the pitcher can win the game.
def score_tally(awayInnings, homeInnings, pitcherTeam):
    awayScore = 0
    homeScore = 0
    inning = 1
    result = False 
    if pitcherTeam == 'x':
        return result
    for (a, h) in zip(awayInnings, homeInnings):
        # print('T',inning, awayScore, homeScore)
        if win_with_pitcher(awayScore, homeScore, inning, 'top', pitcherTeam) != False:
            print(awayScore, homeScore, 'top', inning, f'won by {pitcherTeam}')
            result = awayScore, homeScore, inning, 'top', pitcherTeam
            break
        awayScore += a
        # print('B',inning, awayScore, homeScore)
        if win_with_pitcher(awayScore, homeScore, inning, 'bottom', pitcherTeam) != False:
            print(awayScore, homeScore, 'bottom', inning, f'won by {pitcherTeam}')
            result = awayScore, homeScore, inning, 'bottom', pitcherTeam
            break
        homeScore += h
        inning += 1
    return result

# Bodged together again.
# Checks whether the pitcher, giving up exactly 1 run per inning, can win the game for his team. Returns either False
# if the pitcher cannot win, or the situation in which he can win.
def win_with_pitcher(awayScore, homeScore, inning, side, pitcherTeam):
    if pitcherTeam == 'a':
        if inning >= 9:
            if (awayScore - homeScore) >= 2:
                # print(awayScore, homeScore, inning, side)
                return True, awayScore, homeScore, inning, side
            else:
                # print('No win')
                return False
        elif (awayScore - homeScore) >= (11-inning):
            # print(awayScore, homeScore, inning, side)
            return True, awayScore, homeScore, inning, side
        else:
            # print('No win')
            return False

    elif pitcherTeam == 'h':
        if inning >= 9:
            if (homeScore - awayScore) >= 2:
                # print(awayScore, homeScore, inning, side)
                return True, awayScore, homeScore, inning, side
            else:
                # print('No win')
                return False
        elif (homeScore - awayScore) >= (11-inning):
            # print(awayScore, homeScore, inning, side)
            return True, awayScore, homeScore, inning, side
        else:
            # print('No win')
            return False

# Finds the WPA added by our 9 ERA reliever
def find_WPA(awayScore, homeScore, inning, side, pitcherTeam):
    probCalc = WinExp.WinExpCalculator(4.5, .525)
    if side == 'top':
        side = 0
    elif side == 'bottom':
        side = 1
    prob = probCalc.getWinPct(1,(homeScore - awayScore),inning,0,side)
    if pitcherTeam == 'a':
        return prob
    elif pitcherTeam == 'h':
        return (1 - prob)

WPA = 0

with open('GL2019.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        games = 0
        for row in csv_reader:
            awayTeam = row[3]
            homeTeam = row[6]
            awayLinescore = row[19]
            homeLinescore = row[20]
            games +=1 

            awayInnings, homeInnings = generate_inninglists(awayLinescore, homeLinescore)

            
            # Specify the team you want, or 'ALL' for all teams
            selected_team = 'ALL'

            # awayInnings, homeInnings = generate_inninglists(awayLinescore, homeLinescore)
            if selected_team != 'ALL':
                st = score_tally(awayInnings, homeInnings, pitcher_team(awayTeam, homeTeam,selected_team))
                if st != False:
                    print(find_WPA(st[0], st[1], st[2], st[3], st[4]))
                    WPA += find_WPA(st[0], st[1], st[2], st[3], st[4])

            # The block below calculates potential WPA for all teams in all games. To get an  estimate for WPA/162,
            # divide total WPA by 30.

            else:
                st = score_tally(awayInnings, homeInnings, 'a')
                if st != False:
                    print(find_WPA(st[0], st[1], st[2], st[3], st[4]))
                    WPA += find_WPA(st[0], st[1], st[2], st[3], st[4])

                st = score_tally(awayInnings, homeInnings, 'h')
                if st != False:
                    print(find_WPA(st[0], st[1], st[2], st[3], st[4]))
                    WPA += find_WPA(st[0], st[1], st[2], st[3], st[4])
        print('****************')
        print(games, 'games')
        print('WPA:', WPA)
