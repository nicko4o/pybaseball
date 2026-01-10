# Lahman Data Acquisition Functions

Pull data from [Sean Lahman's database](http://www.seanlahman.com/baseball-archive/statistics/), now maintained by [SABR (Society for American Baseball Research)](https://sabr.org/lahman-database/).

> **Note**: The original GitHub source (`chadwickbureau/baseballdatabank`) is no longer available. You must manually download the database from SABR's website and extract it to your pybaseball cache directory.

## Setup

1. Visit [https://sabr.org/lahman-database/](https://sabr.org/lahman-database/)
2. Download the **Comma-delimited version** (zip file)
3. Extract the contents to your pybaseball cache directory (typically `~/.pybaseball/cache/`)

After extraction, you should have a folder like `lahman_2025` containing a `core/` subdirectory.

## Usage

```python
from pybaseball.lahman import *

# park id, name, alias, city, state, and country
parks = parks()

# all star roster data: player, year, team, league, position
allstar = all_star_full()

# each player's games played per position for each season
appearances = appearances()

# manager awards by year
awards_mgr = awards_managers()

# player awards by year
awards_player = awards_players()

# vote shares by year for manager awards 
award_share_mgr = awards_share_managers()

# vote shares by year for player awards 
award_share_player = awards_share_players()

# batting stats by year, regular season
batting = batting()

# batting stats by year, post season
batting_post = batting_post()

# the college a player played at each year
college_playing = college_playing()

# fielding stats by year 
fielding = fielding()

# games played in left, center, right field 
fielding_of = fielding_of()

# LF/CF/RF splits
fielding_of_split = fielding_of_split()

# postseason fielding 
fielding_post = fielding_post()

# hall of fame voting by year 
hall_of_fame = hall_of_fame()

# home game attendance by park by year 
home_games = home_games()

# managers by team and year
managers = managers()

# split season managers data
managers_half = managers_half()

# historical player pitching stats
pitching = pitching()

# postseason pitching stats
pitching_post = pitching_post()

# salary data
salaries = salaries()

# schools attended by each player
schools = schools()

# playoff series winners and losers 
series_post = series_post()

# data on teams by year: record, division, stadium, attendance, etc
teams = teams()

# current and historical franchises, whether they're still active, and their ids
teams_franchises = teams_franchises()

# split season data for teams
teams_half = teams_half() 
```
