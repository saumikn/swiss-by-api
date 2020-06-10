# Option 1
**Converting Lichess Swiss/Arena to SwissSys Crosstable**

1. Get the URL of the tournament: For example, an arena might have a URL https://lichess.org/tournament/vAT26cQv, and a swiss might have a URL https://lichess.org/swiss/E6PijXZ4

2. Run `python arena.py {url}`

3. After you have run this code, a file called xtable.csv will be created. Open the file in SwissSys 10.

4. Edit the file data.csv to include the details of all the players in the tournament. You need their lichess username, USCF ID, and Name, but you don't need the timestamp.

5. Import data.csv into SwissSys. If you need help with this, there is a video tutorial at https://new.uschess.org/rules/swisssys-feature-helping-chess-com-us-chess-rated-events/



# Option 2
**Running using SwissSys (Much more work required, but allows complete control over pairings, just like an OTB tournament)**

## Do this once

1. Follow Steps 1 and 2 here: https://developers.google.com/sheets/api/quickstart/python

2. Run `python sheets.py` to save your Google Sheets credentials into `token.pickle`. You will only need to do this once

3. Generate a personal lichess access token at https://lichess.org/account/oauth/token/create 

## Do this at the beginning of the tournament

1. Create a new Google Sheet at https://sheets.google.com. Note the spreedsheet id, which you can find in the URL of your new Google Sheet at https://docs.google.com/spreadsheets/d/**spreadsheetId**/edit#gid=0

2. make a `.env` file with the following contents:
    ```
    LICHESS_TOKEN="{lichess token}"
    GOOGLE_SHEET_ID="{spreadsheet id}"
    GOOGLE_SHEET_NAME="{sheet name}"
    ```
    The Sheet Name will be the name of the tab you want to post pairings go.

## Tournament Use

2. For each section in the tournament, copy and paste the pairings from SwissSys into a seperate file.

3. Run main.py with the section pairing paths as arguments. For example: `python main.py -start /pairings/section1 /pairings/section2 /pairings/section3`

4. If your network disconnects during the middle of the round, and you want to pick up where you left off, run `python main.py -continue`.