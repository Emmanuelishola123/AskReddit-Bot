import math
import re
from time import time
import urllib
from urllib.request import urlopen, Request
import text2speech
import os
from pathlib import Path
import ffmpeg
import thumbnail
# from upload_video import upload_video
import praw
from dotenv import load_dotenv

load_dotenv()


clientId = os.getenv('CLIENTID')
clientSecret = os.getenv('CLIENTSECRET')
userAgent = os.getenv('USERAGENT')
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')


# reddit = praw.Reddit(client_id=clientId,
#                      client_secret=clientSecret,
#                      user_agent=userAgent,
#                      username=username,
#                      password=password)


reddit = praw.Reddit(client_id='o_5oRdhuH9WqheZbLVKyNQ',
                     client_secret='o96FFoqOr8pWEPrOxZr76Ppm4aU-YA',
                     user_agent='reddit2video',
                     username='solution000',
                     password='password@Reddit')


videoLengthInMin = 2


temp_path = os.getcwd() + "/temp"
path = os.getcwd() + "/generated"


def generate_askreddit_q_a():
    #CREATE T2S TEMP FOLDER
    Path(path+"/t2s").mkdir(parents=True, exist_ok=True)
    #CREATE VIDEO TEMP FOLDER
    Path(path+"/video").mkdir(parents=True, exist_ok=True)

    stop_generating = False

    for submission in reddit.subreddit('AskReddit').hot(limit=20):
        print(submission)
        print('question....')
       
        if stop_generating:
            break

        print(submission.title)
        print('title')
        print(reddit)
        print('reddit')

        if len(submission.title) > 0:
            nextTopic = False
            with open(temp_path+"/used.txt") as f:
                for line in f:
                    if line.strip() == submission.title.strip():
                        nextTopic = True

            if nextTopic:
                continue

            with open(temp_path+"/used.txt", "a") as text_file:
                text_file.write(submission.title + '\n')

            # ThumbPath = path + "/thumb"       
            # Path(ThumbPath).mkdir(parents=True, exist_ok=True)
            
            # ThumbTempPath = path + "/thumb/temp"
            ThumbTempPath = path + "/thumb"
            defaultThumbnail = 'https://images.unsplash.com/photo-1616509091215-57bbece93654?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1000&q=80'
            Path(ThumbTempPath).mkdir(parents=True, exist_ok=True)
            thumbBgUrl = defaultThumbnail or thumbnail.create(submission.title)["urls"]["raw"] 
            print(thumbBgUrl)
            titleasd = submission.title.replace(" ", "-").replace("\'", "").replace("'", "").replace('"', '')
            print(titleasd)
            # goalThumbPath = ThumbTempPath + '/' + titleasd.translate({ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`~-=_+"}).replace("/", "/").replace(" ", "-")+ '.png'
            goalThumbPath = ThumbTempPath + '/' + 'thumbnail.png'
            print(goalThumbPath)
            urllib.request.urlretrieve(thumbBgUrl, goalThumbPath)
            #thumbnail.combineImages(ThumbTempPath + '/' + submission.title.translate({ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`~-=_+"}).replace(" ", "-") + '.png'.replace("/", "/").replace("//", "/"),+ "/templates/thumb.png",ThumbPath + '/' + submission.title.translate({ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`~-=_+"}).replace(" ", "-") + '.png'.replace("/", "/").replace("//", "/"))


            # currentPostPath = path + "/t2s/" + submission.title.translate(
            #     {ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`~-=_+"}).replace(" ", "-").replace("\'", "").replace("'", "").replace('"', '')

            # currentPostPath = path + "/t2s" 
            # Path(currentPostPath).mkdir(parents=True, exist_ok=True)

            #CREATE T2S TEMP FOLDER
            currentPostPath = path + "/t2s"
            # Path(currentPostPath).mkdir(parents=True, exist_ok=True)


            # currentPostVideoPath = path + "/video/" + submission.title.translate(
            #     {ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`~-=_+"}).replace(" ", "-").replace("\'", "").replace("'", "").replace('"', '')

            #CREATE VIDEO TEMP FOLDER
            currentPostVideoPath = path + "/video"
            # Path(currentPostVideoPath).mkdir(parents=True, exist_ok=True)


            #CREATE TEXT2SPEECH TITLE MP3 TEMP
            text2speech.convert(submission.title.replace("..",".").replace("\n",""), currentPostPath, "title","male")

            currentT2SLength = math.ceil(ffmpeg.getFileLength(currentPostPath + "/title.mp3"))

            # CREATE VIDEO TITLE MP4 TEMP
            ffmpeg.videoFromImage(temp_path + "/templates/blank.png", currentPostVideoPath + "/title.mp4",currentT2SLength++(currentT2SLength/4))

            Path(currentPostVideoPath+"/temp").mkdir(parents=True, exist_ok=True)      ########################################
            Path(currentPostVideoPath + "/final").mkdir(parents=True, exist_ok=True)   ########################################
 
            lines = ffmpeg.splitTextIntoLineArray(submission.title,105)
            print(lines)

            heightStartAuthor = math.ceil((23 - len(lines)) / 2) * 40
            heightStartText = heightStartAuthor + 40

            #ADD AUTHOR TO VIDEO
            ffmpeg.overlayText(currentPostVideoPath + "/title.mp4",str(submission.author),27,"medium.ttf","#5aa5d9",currentPostVideoPath + "/temp/title.mp4",300.5,heightStartAuthor)

            #ADD TEXT TO VIDEO
            index = 1
            for line in lines:
                line = re.sub(r'^https?:\/\/.*[\r\n]*', '', line, flags=re.MULTILINE)
                finalPath = "/temp"
                if len(lines) == index:
                    finalPath = "/final"

                if index % 2 != 0:
                    if len(lines) != index:
                        finalPath = ""
                    ffmpeg.overlayText(currentPostVideoPath + "/temp/title.mp4",line.replace(",",""),27.5,"regular.ttf","#ffffff",currentPostVideoPath + finalPath + "/title.mp4",300.5,heightStartText+(35*(index-1)))
                else:
                    ffmpeg.overlayText(currentPostVideoPath + "/title.mp4",line.replace(",",""),27.5,"regular.ttf","#ffffff",currentPostVideoPath + finalPath + "/title.mp4",300.5,heightStartText+(35*(index-1)))
                index = index + 1

            # ADD SHARE BUTTONS
            Path(currentPostVideoPath + "/final/overlay").mkdir(parents=True, exist_ok=True)
            ffmpeg.addImageToVideo(currentPostVideoPath + "/final/title.mp4",temp_path + "/templates/share.png", 300.5, heightStartText + (35 * len(lines)),currentPostVideoPath + "/final/overlay/title.mp4")
            # ADD VOTE BUTTONS
            Path(currentPostVideoPath + "/final/overlay2").mkdir(parents=True, exist_ok=True)
            ffmpeg.addImageToVideo(currentPostVideoPath + "/final/overlay/title.mp4",temp_path + "/templates/vote.png", 240, heightStartAuthor,currentPostVideoPath + "/final/overlay2/title.mp4")



            # CREATE VIDEO TITLE MP4 WITH T2S
            currentVidPath = currentPostVideoPath + "/final/overlay2/title.mp4"
            currentT2SPath = currentPostPath + "/title.mp3"

            mp4WithT2SPath = currentPostVideoPath + "/withT2S/"
            Path(mp4WithT2SPath).mkdir(parents=True, exist_ok=True)
            ffmpeg.combineAudioWithVideo(currentT2SPath, currentVidPath, mp4WithT2SPath + "title.mp4")


            submission = reddit.submission(url=submission.url)


            #COUNT THE AVG COMMENT LENGTH
            commentCount = 0
            allCommentsLength = 0
            for top_level_comment in submission.comments:
                if len(str(top_level_comment)) < 10:
                    allCommentsLength += len(top_level_comment.body)
                    commentCount += 1
            avgCommentLength = allCommentsLength / commentCount

            #CREATING VIDEO PARTS
            index = 0
            currentVideoLengthInSeconds = 0
            for top_level_comment in submission.comments:
                if len(str(top_level_comment)) < 10:
                    if len(top_level_comment.body) > avgCommentLength:
                        lines = ffmpeg.splitTextIntoLineArray(top_level_comment.body.strip(), 105)
                        print(lines)
                        heightStartAuthor = math.ceil((23-len(lines))/2)*40
                        heightStartText = heightStartAuthor + 40

                        #CREATE TEXT2SPEECH MP3 TEMP
                        text2speech.convert(top_level_comment.body.strip().replace("..",".").replace("..",".").replace("\n",""), currentPostPath, str(index), "male")
                        currentT2SLength = math.ceil(ffmpeg.getFileLength(currentPostPath + "/" + str(index) + ".mp3"))

                        #CREATE VIDEO MP4 TEMP
                        ffmpeg.videoFromImage(temp_path+"/templates/blank.png",currentPostVideoPath+"/"+str(index)+".mp4",currentT2SLength+(currentT2SLength/4))

                        # ADD AUTHOR TO VIDEO
                        ffmpeg.overlayText(currentPostVideoPath + "/"+str(index)+".mp4", str(top_level_comment.author), 27, "medium.ttf","#5aa5d9", currentPostVideoPath + "/temp/"+str(index)+".mp4", 300.5, heightStartAuthor)

                        # ADD TEXT TO VIDEO
                        indexText = 1
                        for line in lines:
                            finalPath = "/temp"
                            if len(lines) == indexText:
                                finalPath = "/final"

                            if indexText % 2 != 0:
                                if len(lines) != indexText:
                                    finalPath = ""

                                ffmpeg.overlayText(currentPostVideoPath + "/temp/"+str(index)+".mp4", line.replace(",", "??"), 27.5,
                                                "regular.ttf", "#ffffff", currentPostVideoPath + finalPath + "/"+str(index)+".mp4", 300.5,
                                                heightStartText + (35 * (indexText - 1)))
                            else:
                                ffmpeg.overlayText(currentPostVideoPath + "/"+str(index)+".mp4", line.replace(",", "??"), 27.5,
                                                "regular.ttf", "#ffffff", currentPostVideoPath + finalPath + "/"+str(index)+".mp4",
                                                300.5, heightStartText + (35 * (indexText - 1)))
                            indexText = indexText + 1

                        #ADD SHARE BUTTONS
                        Path(currentPostVideoPath + "/final/overlay").mkdir(parents=True, exist_ok=True)
                        ffmpeg.addImageToVideo(currentPostVideoPath + "/final/" + str(index) + ".mp4",temp_path+"/templates/share.png",300.5,heightStartText+(35*len(lines)),currentPostVideoPath + "/final/overlay/" + str(index) + ".mp4")
                        #ADD VOTE BUTTONS
                        Path(currentPostVideoPath + "/final/overlay2").mkdir(parents=True, exist_ok=True)
                        ffmpeg.addImageToVideo(currentPostVideoPath + "/final/overlay/" + str(index) + ".mp4",temp_path + "/templates/vote.png", 240, heightStartAuthor,currentPostVideoPath + "/final/overlay2/" + str(index) + ".mp4")


                        # CREATE VIDEO MP4 WITH T2S
                        currentT2SPath = currentPostPath + "/" + str(index) + ".mp3"

                        mp4WithT2SPath = currentPostVideoPath + "/withT2S/"
                        Path(mp4WithT2SPath).mkdir(parents=True, exist_ok=True)

                        ffmpeg.combineAudioWithVideo(currentT2SPath,currentPostVideoPath + "/final/overlay2/" + str(index) + ".mp4",mp4WithT2SPath+str(index)+".mp4")


                        # COMBINE ALL VIDEO PARTS TO VIDEO
                        # finalVideoPath = path + "/finalVideos/" + submission.title.translate({ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`~-=_+"}).replace(" ", "-").replace(" ", "-").replace("\'", "").replace("'", "").replace('"', '')
                        finalVideoPath = path + "/finalVideos"
                        Path(finalVideoPath).mkdir(parents=True, exist_ok=True)
                        Path(finalVideoPath+"/temp").mkdir(parents=True, exist_ok=True)         ############################################
                        Path(finalVideoPath + "/final").mkdir(parents=True, exist_ok=True)      ############################################


                        #Combine Current Video with rest
                        currentVideoLengthInSeconds = currentVideoLengthInSeconds + currentT2SLength + 1  # +1 Second because of the transisation
                        videoLengthReached = currentVideoLengthInSeconds/60 > videoLengthInMin or index == len(submission.comments)-1
                        if index < 1:
                            if not videoLengthReached:
                                ffmpeg.concatVideos(currentPostVideoPath + "/withT2S/title.mp4", temp_path + "/templates/trans.mp4",finalVideoPath + "/temp/finalVideo.mp4")
                                ffmpeg.concatVideos(finalVideoPath + "/temp/finalVideo.mp4",currentPostVideoPath + "/withT2S/0.mp4",finalVideoPath + "/finalVideo.mp4")
                            else:
                                ffmpeg.concatVideos(currentPostVideoPath + "/withT2S/title.mp4", temp_path + "/templates/trans.mp4",finalVideoPath + "/temp/finalVideo.mp4")
                                ffmpeg.concatVideos(finalVideoPath + "/temp/finalVideo.mp4",currentPostVideoPath + "/withT2S/0.mp4",finalVideoPath + "/final/finalVideo.mp4")
                        else:
                            if not videoLengthReached:
                                ffmpeg.concatVideos(finalVideoPath + "/finalVideo.mp4", temp_path + "/templates/trans.mp4",finalVideoPath + "/temp/finalVideo.mp4")
                                ffmpeg.concatVideos(finalVideoPath + "/temp/finalVideo.mp4",currentPostVideoPath + "/withT2S/"+str(index)+".mp4",finalVideoPath + "/finalVideo.mp4")
                            else:
                                ffmpeg.concatVideos(finalVideoPath + "/finalVideo.mp4", temp_path + "/templates/trans.mp4",finalVideoPath + "/temp/finalVideo.mp4")
                                ffmpeg.concatVideos(finalVideoPath + "/temp/finalVideo.mp4",currentPostVideoPath + "/withT2S/"+str(index)+".mp4",finalVideoPath + "/final/finalVideo.mp4")

                        '''finalPath = "/temp"
                        if videoLengthReached:
                            finalPath = "/final"

                        if index > 0:
                            if index % 2 == 0:
                                if not videoLengthReached:
                                    finalPath = ""
                                ffmpeg.concatVideos(finalVideoPath + "/temp/finalVideo.mp4",currentPostVideoPath + "/withT2S/" + str(index) + ".mp4",finalVideoPath + finalPath + "/finalVideo.mp4")
                            else:
                                ffmpeg.concatVideos(finalVideoPath + "/finalVideo.mp4",currentPostVideoPath + "/withT2S/" + str(index) + ".mp4",finalVideoPath + finalPath + "/finalVideo.mp4")
                        else:
                            if not videoLengthReached:
                                finalPath = ""
                            # Combine Title Video with First Video
                            ffmpeg.concatVideos(currentPostVideoPath + "/withT2S/title.mp4",currentPostVideoPath + "/withT2S/0.mp4",finalVideoPath + finalPath + "/finalVideo.mp4")
                            '''


                        #STOP WHEN VIDEO LENGTH REACHED
                        if videoLengthReached:
                            break

                        index = index + 1
                           
            stop_generating = True




                    # ADD BACKGROUND MUSIC
                    # finalVideoPath = path + "/finalVideos/" + submission.title.translate({ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`~-=_+"}).replace(" ", "-")+"/final/finalVideo.mp4"
                    # musicPath = path + "/templates/music.mp3"
                    # ffmpeg.addAudioToVideo(musicPath,finalVideoPath,path + "/finalVideos/" + submission.title.translate({ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`~-=_+"}).replace(" ", "-")+"/final/finalVideoWithMusic.mp4")
       

# video_data = {
#     "file": "video.mp4",
#     "title": f"{redditbot.post_data[0]['title']} - Dankest memes and comments {dt_string}!",
#     "description": "#shorts\nGiving you the hottest AskReddit question and answer of the day",
#     "keywords": "AskReddit,Reddit",
#     "privacyStatus": "public",
# }
# print('Uploading.........')
# upload_video()
# print('Wake up........')

        
# 1 Zeile == 105Characktzer
# usernameColor == #5aa5d9

#DRAW USERNAME
#ffmpeg -i 0.mp4 -vf "drawtext=fontfile=medium.ttf: text='burnova': fontcolor=#5aa5d9: fontsize=27: x=300.5:y=168.5:" -codec:a copy 0Text.mp4

#DRAW TEXT !!!!!!! REMOVE , IN TEXT!!!!!
#ffmpeg -i 0Text.mp4 -vf "drawtext=fontfile=regular.ttf: text='Lorem Ipsum': fontcolor=#ffffff: fontsize=27: x=300.5:y=217:" -codec:a copy 0Text2.mp4

#+35px every line