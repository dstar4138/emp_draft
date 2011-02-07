Name: Social Networking for the Terminal Geek
Author: Alexander Dean

DESCRIPTION:
-------------------------------------------------------------------------------
  Connect to and interact with today's modern social networking sites such as 
Facebook and Twitter within a terminal. Reduces the amount of mouse interaction
as well as the constant refreshing and tabbing of web browsers.

PURPOSE:
-------------------------------------------------------------------------------
  The purpose of this application is to have fun using the Facebook and Twitter 
APIs, learn SVN, and get familiar with Charva which is going to be the text 
based UI that I will be using for the interactive mode. I'm not brand new to 
Java, but I am to organized software maintenance and design. This will be a 
nice introduction. 

IDEAL USAGE:
-------------------------------------------------------------------------------
java SNTG [-iha] [-s LOC_CODE status] [-g LOC_CODE [friend_id]] 
  		  [--getfriendids LOC_CODE] [--getfriendinfo LOC_CODE [id]]
  		  [-aevrt LOC_CODE] [--changepassword LOC_CODE]
  			   
	-i, --interactive = interactive mode, uses Charva based TUI.
	-h, -?, --help    = displays this help menu.
	
	LOC_CODE: SNTG can interact with several social networking sites, this code
		tells SNTG where to look, if one isn't provided it will scower all of  
		your accounts to get the appropriate information.
			Codes:
				0,al = all sites
				1,rs = rss feeds only
				2,tw = twitter only
				3,fb = facebook only
				more to come...
  Updating:	
	-s, --setstats = set status on given site, status must be in quotes
				
  Information:	
    -g, --getstats = pull status and print to stdout	 
	--getfriendids  = gets the friend ids of people you know and prints them to
			stdout in the format: [user]::[id], for twitter it gets your 
			followers' ids
	--getfriendinfo = gets information on your friend and prints it to stdout
	
  Settings:
    -a, --addsite  = add an account to the list.
	-e, --editsite = adjust a current account settings such as the current
			login information or bio.
	--changepassword  = change the password of a given account
	-v, --viewsite = displays your account information of a given account.
	-t, --showall  = displays all of your account info, passwords, and hidden
			info.	
	-r, --removesite = removes an account from the list, if a LOC_CODE of 0 
			is provided, then all accounts will be removed after confirmation.

