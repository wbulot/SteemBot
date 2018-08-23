import os
import string
import re
import datetime
import sys
import time

while True:
    time.sleep(10)
    print '\033[1;36m' + "Recuperation de la liste des derniers posts Steemit... " + '\033[00m'
    result = os.popen("/root/piston-cli/cli.py list --sort created --columns identifier net_votes pending_payout_value created author --limit 100").read()
    listPost = result.split('\n')
    #Suppression des lignes inutiles
    listPost.pop(0)
    listPost.pop(0)
    listPost.pop(0)
    listPost.pop()
    listPost.pop()

    for index, post in enumerate(listPost):
        #On split le post pour separer title, author, vote etc ...
        post = post.split('|')
        #On supprime les elements vides (a cause de l'output merdique de piston-cli)
        post = filter(None, post)
        #On clean une derniere fois notre tableau en supprimant les espace inutiles et le sigle SBD dans la payout
        for index2, each in enumerate(post):
            if index2 == 2:
                #On supprime egalement le sigle SBD dans la payout
                post[index2] = post[index2].replace('SBD', '')
            post[index2] = post[index2].replace(' ', '')

        postIdentifier = post[0]
        postVote = post[1]
        postCashout = post[2]
        postTime = post[3]
        postAuthor = post[4]

        #On converti postTime pour qu'il soit en format date python 2017-05-25T13:43:33
        tempTime = postTime.split('T')
        tempDay = tempTime[0]
        tempHour = tempTime[1]
        tempDay = tempDay.split('-')
        tempHour = tempHour.split(':')
        postTime = datetime.datetime(int(tempDay[0]),int(tempDay[1]),int(tempDay[2]),int(tempHour[0]),int(tempHour[1]),int(tempHour[2]))

        #On insert posts.txt dans une list
        with open('posts.txt') as f:
            linesPostTxt = f.read().splitlines()

        f = open("posts.txt","r")
        PostsTxt = f.read()
        f.close()

        if re.search(postIdentifier, PostsTxt) is not None:
            #print "On a detecte le post dans le fichier, on le reecrit pas"
            pass
        else:
            textFile = open("posts.txt", "a")
            textFile.write(postIdentifier+"|"+postVote+"|"+postCashout+"|"+post[3]+"|"+postAuthor+"\n")
            textFile.close()

    print '\033[1;36m' + "Suppression des lignes obsoletes du fichier... " + '\033[00m'
    with open('posts.txt') as f:
        for line in f:
            postInfo = line.split('|')
            print postInfo
            postInfoTime = postInfo[3]
            #On converti postInfoTime pour qu'il soit en format date python 2017-05-25T13:43:33
            tempTime = postInfoTime.split('T')
            tempDay = tempTime[0]
            tempHour = tempTime[1]
            tempDay = tempDay.split('-')
            tempHour = tempHour.split(':')
            postInfoTime = datetime.datetime(int(tempDay[0]),int(tempDay[1]),int(tempDay[2]),int(tempHour[0]),int(tempHour[1]),int(tempHour[2]))

            #On creer la variable postTimeElaps
            now = datetime.datetime.utcnow()
            postTimeElaps = now - postInfoTime
            postTimeElaps = postTimeElaps.seconds/60
            if postTimeElaps < 30:
                print line
                f2 = open("posts2.txt","a")
                f2.write(line)
                f2.close()
    os.remove("posts.txt")
    os.rename("posts2.txt", "posts.txt")

    with open('posts.txt') as f:
        listPost = f.read().splitlines()

    for index, post in enumerate(listPost):
        #On split le post pour separer title, author, vote etc ...
        post = post.split('|')
        postIdentifier = post[0]
        postVote = post[1]
        postCashout = post[2]
        postTime = post[3]
        postAuthor = post[4]

        #On converti postTime pour qu'il soit en format date python 2017-05-25T13:43:33
        tempTime = postTime.split('T')
        tempDay = tempTime[0]
        tempHour = tempTime[1]
        tempDay = tempDay.split('-')
        tempHour = tempHour.split(':')
        postTime = datetime.datetime(int(tempDay[0]),int(tempDay[1]),int(tempDay[2]),int(tempHour[0]),int(tempHour[1]),int(tempHour[2]))

        #On creer la variable postTimeElaps
        now = datetime.datetime.utcnow()
        postTimeElaps = now - postTime
        postTimeElaps = postTimeElaps.seconds/60

        if postTimeElaps > 15 and postTimeElaps < 30:
            result = os.popen("/root/piston-cli/cli.py history "+postAuthor+" --types comment --limit 200 | grep '"+postAuthor+": @"+postAuthor+"' | grep -v 're-' | sort -u -t'|' -k5,5 | sort -t'|' -k1,1 -r").read()
            print "----Clean des resultats..."
            listIdentifier = result.split('\n')
            try:
                listIdentifier.pop(0) #on supprime le 1er article du check qui est celui qu'on va peut etre upvoter et donc qui n'a pas encore beaucoup de upvote
                listIdentifier.pop() #On supprime le dernier element car c'est un element vide, je sais pas pkoi
            except:
                pass
            print "----Taille de la liste : " + str(len(listIdentifier))
            voteNumbersList = []
            voteNumbersList[:] = []
            if len(listIdentifier) > 0:
                for index2, identifier in enumerate(listIdentifier):
                    #On s'arrete apres le check numero 5, pour ne checker que les 5 premiers post de l'auteur
                    if index2 <= 5:
                        identifier = identifier.split('|')
                        identifier = identifier[4]
                        identifier = identifier.replace(post[4]+':','')
                        identifier = identifier.replace(' ','')
                        #print identifier
                        #On check le nombre de vote de cet identifier en question
                        print '\033[1;36m' + "----Recuperation des votes pour le post "+str(index2)+ "... : " +identifier+ '\033[00m'
                        result = os.popen("/root/piston-cli/./cli.py read "+identifier+" --full | grep net_votes | grep -o '[0-9]\+'").read()
                        result = result.replace("\n","")
                        if result == "":
                            result = "0"
                        print "--------votes : "+ result
                        voteNumbersList.append(int(result))
            print voteNumbersList
            if len(voteNumbersList) > 0:
                voteAverage = reduce(lambda x, y: x + y, voteNumbersList) / len(voteNumbersList)
            else:
                voteAverage = 0
            print "----Moyenne = " + str(voteAverage)
            if voteAverage - int(post[1]) > 100: #Si le moyenne des votes du gars est superieur de 100 vote a celui du post checker, on vote
                print '\033[92m' + '----Go vote' + '\033[00m'
                result = os.popen("UNLOCK='975946Steem?' piston upvote "+postIdentifier).read()
                print '\033[92m' + result + '\033[00m'
                f = open("posts.txt","r")
                PostsTxt = f.read()
                f.close()
                with open('posts.txt') as f:
                    for line in f:
                        #print "if"+line+" != "+postIdentifier+"|"+postVote+"|"+postCashout+"|"+post[3]+"|"+postAuthor+"\n"
                        if line != postIdentifier+"|"+postVote+"|"+postCashout+"|"+post[3]+"|"+postAuthor+"\n":
                            #print "if"+line+" search PostsTxt is None"
                            f2 = open("posts2.txt","a")
                            f2.write(line)
                            f2.close()
                        else:
                            print '\035[92m' + 'On ecrit pas !!!' + '\035[00m'
                            print line
                os.remove("posts.txt")
                os.rename("posts2.txt", "posts.txt")
            else:
                print '\033[91m' + '----No' + '\033[00m'
                f = open("posts.txt","r")
                PostsTxt = f.read()
                f.close()
                with open('posts.txt') as f:
                    for line in f:
                        #print "if"+line+" != "+postIdentifier+"|"+postVote+"|"+postCashout+"|"+post[3]+"|"+postAuthor+"\n"
                        if line != postIdentifier+"|"+postVote+"|"+postCashout+"|"+post[3]+"|"+postAuthor+"\n":
                            #print "if"+line+" search PostsTxt is None"
                            f2 = open("posts2.txt","a")
                            f2.write(line)
                            f2.close()
                        else:
                            print '\035[92m' + 'On ecrit pas !!!' + '\035[00m'
                            print line
                os.remove("posts.txt")
                os.rename("posts2.txt", "posts.txt")
